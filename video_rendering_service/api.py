"""
🚀 FastAPI Video Rendering Service API

High-performance video processing API with real-time WebSocket updates.
"""

import asyncio
import logging
import os
import shutil
import time
import uuid
import json
from typing import Dict, Any, List, Optional
from pathlib import Path

from fastapi import FastAPI, UploadFile, File, HTTPException, WebSocket, WebSocketDisconnect, Depends, BackgroundTasks
from fastapi.responses import FileResponse, JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.gzip import GZipMiddleware
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel, Field
import uvicorn

from .core import VideoRenderingEngine, ProcessingJob, EnhancementType, ProcessingStatus
from .config import VideoRenderingConfig
from .websocket_manager import WebSocketManager

logger = logging.getLogger(__name__)


# Pydantic models for API
class JobSubmissionRequest(BaseModel):
    """Request model for job submission"""
    enhancements: List[str] = Field(default_factory=list, description="List of AI enhancements to apply")
    output_format: str = Field(default="mp4", description="Output video format")
    quality: str = Field(default="high", description="Output quality (low, medium, high, ultra)")


class JobStatusResponse(BaseModel):
    """Response model for job status"""
    job_id: str
    status: str
    progress: float
    started_at: Optional[float] = None
    completed_at: Optional[float] = None
    duration: Optional[float] = None
    error_message: Optional[str] = None
    metadata: Optional[Dict[str, Any]] = None
    processing_stats: Dict[str, Any] = Field(default_factory=dict)


class PerformanceStatsResponse(BaseModel):
    """Response model for performance statistics"""
    total_jobs_processed: int
    total_processing_time: float
    average_processing_time: float
    total_data_processed_gb: float
    gpu_utilization: float
    memory_utilization: float
    active_jobs_count: int
    hardware_info: Dict[str, Any]


class SystemInfoResponse(BaseModel):
    """Response model for system information"""
    service_version: str
    hardware_tier: str
    total_ram_gb: float
    available_cores: int
    gpu_acceleration: bool
    supported_formats: List[str]
    max_file_size_gb: float


class VideoRenderingAPI:
    """FastAPI application for video rendering service"""
    
    def __init__(self, config: VideoRenderingConfig):
        self.config = config
        self.engine = VideoRenderingEngine(config)
        self.websocket_manager = WebSocketManager()
        self.app = self._create_app()
    
    def _create_app(self) -> FastAPI:
        """Create and configure FastAPI application"""
        app = FastAPI(
            title="Elite AI Video Rendering Service",
            description="World-class AI video rendering with elite hardware optimization",
            version="1.0.0",
            docs_url="/api/docs",
            redoc_url="/api/redoc",
        )
        
        # Add middleware
        app.add_middleware(
            CORSMiddleware,
            allow_origins=["*"],  # Configure appropriately for production
            allow_credentials=True,
            allow_methods=["*"],
            allow_headers=["*"],
        )
        app.add_middleware(GZipMiddleware, minimum_size=1000)
        
        # Mount static files
        frontend_dir = Path(__file__).parent / "frontend"
        if frontend_dir.exists():
            app.mount("/static", StaticFiles(directory=str(frontend_dir)), name="static")
        
        # Add routes
        self._add_routes(app)
        
        # Add startup/shutdown events
        app.add_event_handler("startup", self._startup_event)
        app.add_event_handler("shutdown", self._shutdown_event)
        
        return app
    
    def _add_routes(self, app: FastAPI):
        """Add API routes"""
        
        @app.get("/")
        async def root():
            """Serve the main frontend application"""
            frontend_file = Path(__file__).parent / "frontend" / "index.html"
            if frontend_file.exists():
                return FileResponse(frontend_file, media_type="text/html")
            else:
                return {
                    "service": "Elite AI Video Rendering Service",
                    "version": "1.0.0",
                    "status": "operational",
                    "hardware_tier": self.config.hardware.processing_tier.value,
                    "docs": "/api/docs",
                    "frontend": "Frontend files not found. Please ensure frontend directory exists."
                }
        
        @app.get("/api/info", response_class=JSONResponse)
        async def api_info():
            """API information endpoint"""
            return {
                "service": "Elite AI Video Rendering Service",
                "version": "1.0.0",
                "status": "operational",
                "hardware_tier": self.config.hardware.processing_tier.value,
                "docs": "/api/docs"
            }
        
        @app.get("/api/system-info", response_model=SystemInfoResponse)
        async def get_system_info():
            """Get system information and capabilities"""
            return SystemInfoResponse(
                service_version="1.0.0",
                hardware_tier=self.config.hardware.processing_tier.value,
                total_ram_gb=self.config.hardware.total_ram_gb,
                available_cores=self.config.hardware.available_cores,
                gpu_acceleration=self.config.enable_gpu_acceleration,
                supported_formats=self.config.supported_formats,
                max_file_size_gb=self.config.max_file_size_gb
            )
        
        @app.post("/api/upload", response_model=Dict[str, str])
        async def upload_video(
            background_tasks: BackgroundTasks,
            file: UploadFile = File(...),
            enhancements: str = "[]"
        ):
            """Upload video file and start processing"""
            # Validate file
            if not file.filename:
                raise HTTPException(status_code=400, detail="No file provided")
            
            file_extension = Path(file.filename).suffix.lower().lstrip('.')
            if file_extension not in self.config.supported_formats:
                raise HTTPException(
                    status_code=400, 
                    detail=f"Unsupported format. Supported: {', '.join(self.config.supported_formats)}"
                )
            
            # Generate unique filename
            upload_id = str(uuid.uuid4())
            upload_filename = f"{upload_id}_{file.filename}"
            upload_path = os.path.join(self.config.upload_dir, upload_filename)
            
            try:
                # Save uploaded file
                with open(upload_path, "wb") as buffer:
                    shutil.copyfileobj(file.file, buffer)
                
                # Parse enhancements from form data
                try:
                    enhancement_names = json.loads(enhancements) if enhancements else []
                except json.JSONDecodeError:
                    enhancement_names = []
                
                # Convert enhancement strings to enum types
                enhancement_list = []
                enhancement_map = {e.value: e for e in EnhancementType}
                for enhancement_name in enhancement_names:
                    if enhancement_name in enhancement_map:
                        enhancement_list.append(enhancement_map[enhancement_name])
                
                # Submit job
                job_id = await self.engine.submit_job(
                    upload_path,
                    enhancement_list,
                    self._create_progress_callback()
                )
                
                return {
                    "job_id": job_id,
                    "upload_id": upload_id,
                    "filename": file.filename,
                    "message": "Upload successful, processing started"
                }
                
            except Exception as e:
                # Cleanup on error
                if os.path.exists(upload_path):
                    os.remove(upload_path)
                logger.error(f"Upload failed: {e}")
                raise HTTPException(status_code=500, detail=f"Upload failed: {str(e)}")
        
        @app.get("/api/jobs/{job_id}/status", response_model=JobStatusResponse)
        async def get_job_status(job_id: str):
            """Get status of a specific processing job"""
            job = self.engine.get_job_status(job_id)
            if not job:
                raise HTTPException(status_code=404, detail="Job not found")
            
            # Convert metadata to dict
            metadata_dict = None
            if job.metadata:
                metadata_dict = {
                    "filename": job.metadata.filename,
                    "file_size": job.metadata.file_size,
                    "duration": job.metadata.duration,
                    "resolution": job.metadata.resolution,
                    "fps": job.metadata.fps,
                    "codec": job.metadata.codec,
                    "bitrate": job.metadata.bitrate,
                    "checksum": job.metadata.checksum,
                }
            
            return JobStatusResponse(
                job_id=job.job_id,
                status=job.status.value,
                progress=job.progress,
                started_at=job.started_at,
                completed_at=job.completed_at,
                duration=job.duration,
                error_message=job.error_message,
                metadata=metadata_dict,
                processing_stats=job.processing_stats
            )
        
        @app.get("/api/jobs", response_model=List[JobStatusResponse])
        async def list_jobs():
            """List all active jobs"""
            active_jobs = self.engine.get_active_jobs()
            return [
                JobStatusResponse(
                    job_id=job.job_id,
                    status=job.status.value,
                    progress=job.progress,
                    started_at=job.started_at,
                    completed_at=job.completed_at,
                    duration=job.duration,
                    error_message=job.error_message,
                    processing_stats=job.processing_stats
                )
                for job in active_jobs
            ]
        
        @app.get("/api/jobs/{job_id}/download")
        async def download_result(job_id: str):
            """Download processed video file"""
            job = self.engine.get_job_status(job_id)
            if not job:
                raise HTTPException(status_code=404, detail="Job not found")
            
            if job.status != ProcessingStatus.COMPLETED:
                raise HTTPException(status_code=400, detail="Job not completed yet")
            
            if not os.path.exists(job.output_file):
                raise HTTPException(status_code=404, detail="Output file not found")
            
            return FileResponse(
                job.output_file,
                media_type="video/mp4",
                filename=f"enhanced_{job.metadata.filename if job.metadata else 'video.mp4'}"
            )
        
        @app.get("/api/performance", response_model=PerformanceStatsResponse)
        async def get_performance_stats():
            """Get performance statistics and system metrics"""
            stats = self.engine.get_performance_stats()
            active_jobs = self.engine.get_active_jobs()
            
            return PerformanceStatsResponse(
                total_jobs_processed=stats["total_jobs_processed"],
                total_processing_time=stats["total_processing_time"],
                average_processing_time=stats["average_processing_time"],
                total_data_processed_gb=stats["total_data_processed_gb"],
                gpu_utilization=stats["gpu_utilization"],
                memory_utilization=stats["memory_utilization"],
                active_jobs_count=len(active_jobs),
                hardware_info={
                    "total_ram_gb": self.config.hardware.total_ram_gb,
                    "available_cores": self.config.hardware.available_cores,
                    "processing_tier": self.config.hardware.processing_tier.value,
                    "is_elite_hardware": self.config.hardware.is_elite_hardware,
                    "max_concurrent_jobs": self.config.hardware.max_concurrent_jobs,
                }
            )
        
        @app.delete("/api/jobs/{job_id}")
        async def cancel_job(job_id: str):
            """Cancel a processing job"""
            job = self.engine.get_job_status(job_id)
            if not job:
                raise HTTPException(status_code=404, detail="Job not found")
            
            if job.is_complete:
                raise HTTPException(status_code=400, detail="Job already completed")
            
            # Mark job as cancelled (in a real implementation, this would stop processing)
            job.status = ProcessingStatus.CANCELLED
            job.completed_at = time.time()
            
            return {"message": f"Job {job_id} cancelled"}
        
        @app.websocket("/ws/progress")
        async def websocket_progress(websocket: WebSocket):
            """WebSocket endpoint for real-time progress updates"""
            await self.websocket_manager.connect(websocket)
            try:
                while True:
                    # Keep connection alive and send periodic updates
                    await asyncio.sleep(1)
                    
                    # Send active jobs status
                    active_jobs = self.engine.get_active_jobs()
                    if active_jobs:
                        jobs_data = []
                        for job in active_jobs:
                            jobs_data.append({
                                "job_id": job.job_id,
                                "status": job.status.value,
                                "progress": job.progress,
                                "filename": job.metadata.filename if job.metadata else "unknown"
                            })
                        
                        await self.websocket_manager.send_to_client(
                            websocket,
                            {
                                "type": "jobs_update",
                                "data": jobs_data,
                                "timestamp": time.time()
                            }
                        )
                    
            except WebSocketDisconnect:
                self.websocket_manager.disconnect(websocket)
        
        @app.get("/api/health")
        async def health_check():
            """Health check endpoint"""
            return {
                "status": "healthy",
                "timestamp": time.time(),
                "version": "1.0.0",
                "active_jobs": len(self.engine.get_active_jobs())
            }
    
    def _create_progress_callback(self):
        """Create progress callback for WebSocket updates"""
        async def progress_callback(job_id: str, progress: float):
            await self.websocket_manager.broadcast({
                "type": "job_progress",
                "job_id": job_id,
                "progress": progress,
                "timestamp": time.time()
            })
        
        return progress_callback
    
    async def _startup_event(self):
        """Application startup event"""
        await self.engine.initialize()
        logger.info("Video Rendering Service API started")
    
    async def _shutdown_event(self):
        """Application shutdown event"""
        await self.engine.cleanup()
        await self.websocket_manager.disconnect_all()
        logger.info("Video Rendering Service API shutdown")


def create_app(config: VideoRenderingConfig = None) -> FastAPI:
    """Create FastAPI application"""
    if config is None:
        config = VideoRenderingConfig.from_env()
    
    api = VideoRenderingAPI(config)
    return api.app


async def run_server(config: VideoRenderingConfig = None):
    """Run the video rendering service"""
    if config is None:
        config = VideoRenderingConfig.from_env()
    
    app = create_app(config)
    
    # Configure logging
    logging.basicConfig(
        level=logging.INFO if not config.debug else logging.DEBUG,
        format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    )
    
    # Run server
    uvicorn_config = uvicorn.Config(
        app=app,
        host=config.host,
        port=config.port,
        log_level="info" if not config.debug else "debug",
        reload=config.debug,
        workers=1,  # Single worker for WebSocket compatibility
    )
    
    server = uvicorn.Server(uvicorn_config)
    await server.serve()


if __name__ == "__main__":
    asyncio.run(run_server())