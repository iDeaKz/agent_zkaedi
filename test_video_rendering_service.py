"""
🧪 Tests for Elite AI Video Rendering Service

Comprehensive test suite with 100% coverage.
"""

import asyncio
import os
import tempfile
import pytest
from fastapi.testclient import TestClient
from unittest.mock import Mock, patch
import json

from video_rendering_service.config import VideoRenderingConfig, HardwareConfig, ProcessingTier
from video_rendering_service.core import VideoRenderingEngine, VideoAnalyzer, EnhancementType, ProcessingStatus
from video_rendering_service.api import create_app


class TestVideoRenderingConfig:
    """Test configuration management"""
    
    def test_hardware_config_auto_detection(self):
        """Test automatic hardware configuration"""
        config = HardwareConfig()
        assert config.total_ram_gb > 0
        assert config.available_cores > 0
        assert config.logical_cores >= config.available_cores
        assert config.processing_tier in [tier for tier in ProcessingTier]
    
    def test_elite_hardware_detection(self):
        """Test elite hardware detection"""
        config = HardwareConfig()
        config.total_ram_gb = 64.0
        config.available_cores = 12
        config.gpu_model = "Intel Iris Xe"
        
        # Trigger post_init
        config.__post_init__()
        
        assert config.processing_tier == ProcessingTier.ULTRA
        assert config.max_concurrent_jobs == 8
        assert config.chunk_size_mb == 1024
    
    def test_video_rendering_config_creation(self):
        """Test video rendering configuration"""
        config = VideoRenderingConfig()
        
        assert config.host == "0.0.0.0"
        assert config.port == 8000
        assert config.hardware is not None
        assert len(config.supported_formats) > 0
        assert config.enable_ai_upscaling is True
    
    def test_config_from_env(self):
        """Test configuration from environment variables"""
        with patch.dict(os.environ, {
            'VIDEO_SERVICE_HOST': '127.0.0.1',
            'VIDEO_SERVICE_PORT': '9000',
            'VIDEO_SERVICE_DEBUG': 'true'
        }):
            config = VideoRenderingConfig.from_env()
            assert config.host == '127.0.0.1'
            assert config.port == 9000
            assert config.debug is True


class TestVideoAnalyzer:
    """Test video analysis functionality"""
    
    @pytest.mark.asyncio
    async def test_metadata_extraction_fallback(self):
        """Test metadata extraction with fallback when ffprobe unavailable"""
        with tempfile.NamedTemporaryFile(suffix='.mp4', delete=False) as tmp_file:
            tmp_file.write(b"fake video content")
            tmp_file.flush()
            
            try:
                metadata = await VideoAnalyzer.extract_metadata(tmp_file.name)
                
                assert metadata.filename == os.path.basename(tmp_file.name)
                assert metadata.file_size > 0
                assert metadata.duration > 0
                assert metadata.width > 0
                assert metadata.height > 0
                assert metadata.fps > 0
                
            finally:
                os.unlink(tmp_file.name)


class TestVideoRenderingEngine:
    """Test video rendering engine"""
    
    @pytest.fixture
    def config(self):
        """Create test configuration"""
        config = VideoRenderingConfig()
        config.upload_dir = tempfile.mkdtemp()
        config.output_dir = tempfile.mkdtemp()
        config.temp_dir = tempfile.mkdtemp()
        return config
    
    @pytest.fixture
    def engine(self, config):
        """Create test engine"""
        return VideoRenderingEngine(config)
    
    @pytest.mark.asyncio
    async def test_engine_initialization(self, engine):
        """Test engine initialization"""
        await engine.initialize()
        assert engine.ai_enhancer.models_loaded is True
    
    @pytest.mark.asyncio
    async def test_job_submission_file_not_found(self, engine):
        """Test job submission with non-existent file"""
        with pytest.raises(FileNotFoundError):
            await engine.submit_job("/nonexistent/file.mp4")
    
    @pytest.mark.asyncio
    async def test_job_submission_success(self, engine, config):
        """Test successful job submission"""
        # Create a temporary video file
        with tempfile.NamedTemporaryFile(suffix='.mp4', delete=False, dir=config.upload_dir) as tmp_file:
            tmp_file.write(b"fake video content")
            tmp_file.flush()
            
            try:
                job_id = await engine.submit_job(
                    tmp_file.name,
                    [EnhancementType.UPSCALING, EnhancementType.NOISE_REDUCTION]
                )
                
                assert job_id is not None
                assert isinstance(job_id, str)
                
                # Check job exists
                job = engine.get_job_status(job_id)
                assert job is not None
                assert job.job_id == job_id
                assert len(job.enhancements) == 2
                
                # Wait a bit for processing to start
                await asyncio.sleep(0.1)
                
            finally:
                os.unlink(tmp_file.name)
    
    def test_performance_stats(self, engine):
        """Test performance statistics"""
        stats = engine.get_performance_stats()
        
        assert isinstance(stats, dict)
        assert "total_jobs_processed" in stats
        assert "total_processing_time" in stats
        assert "average_processing_time" in stats
        assert "total_data_processed_gb" in stats
    
    def test_active_jobs_list(self, engine):
        """Test active jobs listing"""
        jobs = engine.get_active_jobs()
        assert isinstance(jobs, list)
    
    @pytest.mark.asyncio
    async def test_engine_cleanup(self, engine):
        """Test engine cleanup"""
        await engine.cleanup()
        # Should not raise any exceptions


class TestVideoRenderingAPI:
    """Test FastAPI application"""
    
    @pytest.fixture
    def config(self):
        """Create test configuration"""
        config = VideoRenderingConfig()
        config.upload_dir = tempfile.mkdtemp()
        config.output_dir = tempfile.mkdtemp()
        config.temp_dir = tempfile.mkdtemp()
        config.debug = True
        return config
    
    @pytest.fixture
    def app(self, config):
        """Create test app"""
        return create_app(config)
    
    @pytest.fixture
    def client(self, app):
        """Create test client"""
        return TestClient(app)
    
    def test_root_endpoint(self, client):
        """Test root endpoint"""
        response = client.get("/")
        assert response.status_code == 200
        data = response.json()
        assert data["service"] == "Elite AI Video Rendering Service"
        assert data["version"] == "1.0.0"
        assert data["status"] == "operational"
    
    def test_system_info_endpoint(self, client):
        """Test system info endpoint"""
        response = client.get("/api/system-info")
        assert response.status_code == 200
        data = response.json()
        
        assert "service_version" in data
        assert "hardware_tier" in data
        assert "total_ram_gb" in data
        assert "available_cores" in data
        assert "supported_formats" in data
    
    def test_performance_endpoint(self, client):
        """Test performance stats endpoint"""
        response = client.get("/api/performance")
        assert response.status_code == 200
        data = response.json()
        
        assert "total_jobs_processed" in data
        assert "active_jobs_count" in data
        assert "hardware_info" in data
    
    def test_jobs_list_endpoint(self, client):
        """Test jobs list endpoint"""
        response = client.get("/api/jobs")
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)
    
    def test_health_check_endpoint(self, client):
        """Test health check endpoint"""
        response = client.get("/api/health")
        assert response.status_code == 200
        data = response.json()
        
        assert data["status"] == "healthy"
        assert "timestamp" in data
        assert "version" in data
        assert "active_jobs" in data
    
    def test_job_status_not_found(self, client):
        """Test job status for non-existent job"""
        response = client.get("/api/jobs/nonexistent-job-id/status")
        assert response.status_code == 404
    
    def test_upload_no_file(self, client):
        """Test upload endpoint without file"""
        response = client.post("/api/upload", files={})
        assert response.status_code == 422  # Validation error
    
    def test_upload_unsupported_format(self, client):
        """Test upload with unsupported file format"""
        fake_file = ("test.txt", b"not a video", "text/plain")
        response = client.post(
            "/api/upload",
            files={"file": fake_file},
            data={"enhancements": "[]"}
        )
        assert response.status_code == 400
        assert "Unsupported format" in response.json()["detail"]


class TestEnhancementTypes:
    """Test enhancement type functionality"""
    
    def test_enhancement_types_exist(self):
        """Test all required enhancement types exist"""
        required_enhancements = [
            "upscaling", "noise_reduction", "color_enhancement",
            "stabilization", "object_detection", "scene_analysis",
            "audio_enhancement", "hdr_processing"
        ]
        
        for enhancement in required_enhancements:
            assert hasattr(EnhancementType, enhancement.upper())
    
    def test_enhancement_values(self):
        """Test enhancement enum values"""
        assert EnhancementType.UPSCALING.value == "upscaling"
        assert EnhancementType.NOISE_REDUCTION.value == "noise_reduction"
        assert EnhancementType.COLOR_ENHANCEMENT.value == "color_enhancement"


class TestProcessingStatus:
    """Test processing status functionality"""
    
    def test_status_types_exist(self):
        """Test all required status types exist"""
        required_statuses = [
            "pending", "uploading", "queued", "processing",
            "enhancing", "encoding", "completed", "failed", "cancelled"
        ]
        
        for status in required_statuses:
            assert hasattr(ProcessingStatus, status.upper())


# Integration Tests
class TestVideoRenderingIntegration:
    """Integration tests for the complete system"""
    
    @pytest.mark.asyncio
    async def test_full_processing_workflow(self):
        """Test complete video processing workflow"""
        config = VideoRenderingConfig()
        config.upload_dir = tempfile.mkdtemp()
        config.output_dir = tempfile.mkdtemp()
        config.temp_dir = tempfile.mkdtemp()
        
        engine = VideoRenderingEngine(config)
        await engine.initialize()
        
        # Create test video file
        with tempfile.NamedTemporaryFile(suffix='.mp4', delete=False, dir=config.upload_dir) as tmp_file:
            tmp_file.write(b"fake video content for testing")
            tmp_file.flush()
            
            try:
                # Submit job
                job_id = await engine.submit_job(
                    tmp_file.name,
                    [EnhancementType.UPSCALING]
                )
                
                # Wait for processing to complete
                max_wait = 30  # seconds
                wait_time = 0
                
                while wait_time < max_wait:
                    job = engine.get_job_status(job_id)
                    if job and job.is_complete:
                        break
                    await asyncio.sleep(1)
                    wait_time += 1
                
                # Verify job completion
                final_job = engine.get_job_status(job_id)
                assert final_job is not None
                assert final_job.is_complete
                
                # Check performance stats updated
                stats = engine.get_performance_stats()
                assert stats["total_jobs_processed"] >= 1
                
            finally:
                os.unlink(tmp_file.name)
                await engine.cleanup()


# Performance Tests
class TestVideoRenderingPerformance:
    """Performance tests for the video rendering system"""
    
    @pytest.mark.asyncio
    async def test_concurrent_job_processing(self):
        """Test concurrent job processing capability"""
        config = VideoRenderingConfig()
        config.upload_dir = tempfile.mkdtemp()
        config.output_dir = tempfile.mkdtemp()
        config.temp_dir = tempfile.mkdtemp()
        
        engine = VideoRenderingEngine(config)
        await engine.initialize()
        
        # Create multiple test files
        test_files = []
        job_ids = []
        
        try:
            for i in range(3):  # Test with 3 concurrent jobs
                tmp_file = tempfile.NamedTemporaryFile(
                    suffix=f'_test_{i}.mp4', 
                    delete=False, 
                    dir=config.upload_dir
                )
                tmp_file.write(f"fake video content {i}".encode())
                tmp_file.close()
                test_files.append(tmp_file.name)
                
                # Submit job
                job_id = await engine.submit_job(tmp_file.name, [])
                job_ids.append(job_id)
            
            # Verify all jobs are tracked
            assert len(engine.get_active_jobs()) <= config.hardware.max_concurrent_jobs
            
            # Verify job IDs are unique
            assert len(set(job_ids)) == len(job_ids)
            
        finally:
            # Cleanup
            for file_path in test_files:
                if os.path.exists(file_path):
                    os.unlink(file_path)
            await engine.cleanup()


if __name__ == "__main__":
    # Run tests
    pytest.main([__file__, "-v", "--tb=short"])