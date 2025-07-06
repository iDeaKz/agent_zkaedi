"""
🔧 Video Rendering Service Configuration

Elite hardware-optimized configuration for maximum performance.
"""

import os
from typing import Optional, Dict, Any, List
from dataclasses import dataclass, field
from enum import Enum

try:
    import psutil
except ImportError:
    # Fallback if psutil is not available
    class MockPsutil:
        @staticmethod
        def virtual_memory():
            class Memory:
                total = 64 * 1024**3  # 64GB default
            return Memory()
        
        @staticmethod
        def cpu_count(logical=True):
            return 12 if logical else 8
    
    psutil = MockPsutil()


class ProcessingTier(Enum):
    """Processing performance tiers based on hardware capabilities"""
    ULTRA = "ultra"     # 64GB RAM, 8TB SSD, GPU acceleration
    HIGH = "high"       # 32GB+ RAM, SSD storage
    MEDIUM = "medium"   # 16GB+ RAM, standard storage
    LOW = "low"         # Basic configuration


class VideoCodec(Enum):
    """Supported video codecs for optimal hardware utilization"""
    H264 = "h264"
    H265 = "h265"
    VP9 = "vp9"
    AV1 = "av1"


@dataclass
class HardwareConfig:
    """Elite hardware configuration detection and optimization"""
    
    # Detected system specs
    total_ram_gb: float = field(default_factory=lambda: psutil.virtual_memory().total / (1024**3))
    available_cores: int = field(default_factory=lambda: psutil.cpu_count(logical=False))
    logical_cores: int = field(default_factory=lambda: psutil.cpu_count(logical=True))
    
    # Elite hardware targets
    target_ram_gb: float = 64.0
    target_storage_tb: float = 8.0
    gpu_model: str = "Intel Iris Xe"
    
    # Performance settings
    max_concurrent_jobs: int = field(default=4)
    chunk_size_mb: int = field(default=512)
    memory_buffer_gb: float = field(default=16.0)
    
    def __post_init__(self):
        """Auto-configure based on detected hardware"""
        # Optimize for elite hardware configuration
        if self.total_ram_gb >= 60:
            self.processing_tier = ProcessingTier.ULTRA
            self.max_concurrent_jobs = 8
            self.chunk_size_mb = 1024
            self.memory_buffer_gb = 32.0
        elif self.total_ram_gb >= 30:
            self.processing_tier = ProcessingTier.HIGH
            self.max_concurrent_jobs = 4
            self.chunk_size_mb = 512
            self.memory_buffer_gb = 16.0
        elif self.total_ram_gb >= 15:
            self.processing_tier = ProcessingTier.MEDIUM
            self.max_concurrent_jobs = 2
            self.chunk_size_mb = 256
            self.memory_buffer_gb = 8.0
        else:
            self.processing_tier = ProcessingTier.LOW
            self.max_concurrent_jobs = 1
            self.chunk_size_mb = 128
            self.memory_buffer_gb = 4.0
    
    @property
    def is_elite_hardware(self) -> bool:
        """Check if running on elite hardware configuration"""
        return (
            self.total_ram_gb >= 60 and
            self.available_cores >= 8 and
            "xe" in self.gpu_model.lower()
        )


@dataclass
class VideoRenderingConfig:
    """Comprehensive video rendering service configuration"""
    
    # Service settings
    host: str = "0.0.0.0"
    port: int = 8000
    debug: bool = False
    
    # Storage configuration
    upload_dir: str = "/tmp/video_uploads"
    output_dir: str = "/tmp/video_outputs"
    temp_dir: str = "/tmp/video_processing"
    max_file_size_gb: float = 10.0
    
    # Processing configuration
    hardware: HardwareConfig = field(default_factory=HardwareConfig)
    supported_formats: List[str] = field(default_factory=lambda: [
        "mp4", "avi", "mov", "mkv", "webm", "flv", "wmv", "m4v"
    ])
    output_codec: VideoCodec = VideoCodec.H264
    
    # AI Enhancement settings
    enable_ai_upscaling: bool = True
    enable_noise_reduction: bool = True
    enable_color_enhancement: bool = True
    enable_object_detection: bool = True
    enable_scene_analysis: bool = True
    enable_audio_enhancement: bool = True
    
    # Performance optimization
    enable_gpu_acceleration: bool = True
    enable_memory_mapping: bool = True
    enable_chunk_processing: bool = True
    enable_advanced_caching: bool = True
    
    # Redis configuration for task queue
    redis_host: str = "localhost"
    redis_port: int = 6379
    redis_db: int = 0
    redis_password: Optional[str] = None
    
    # WebSocket configuration
    websocket_host: str = "localhost"
    websocket_port: int = 8001
    max_websocket_connections: int = 1000
    
    # Monitoring configuration
    enable_prometheus_metrics: bool = True
    prometheus_port: int = 9090
    enable_health_checks: bool = True
    health_check_interval: int = 30
    
    # Security configuration
    max_concurrent_uploads: int = 10
    rate_limit_per_minute: int = 100
    enable_file_validation: bool = True
    allowed_mime_types: List[str] = field(default_factory=lambda: [
        "video/mp4", "video/avi", "video/quicktime", "video/x-msvideo",
        "video/webm", "video/x-flv", "video/x-ms-wmv"
    ])
    
    # Error handling configuration
    max_retry_attempts: int = 3
    retry_delay_seconds: float = 1.0
    enable_auto_recovery: bool = True
    enable_graceful_degradation: bool = True
    
    def __post_init__(self):
        """Post-initialization configuration setup"""
        # Create directories if they don't exist
        os.makedirs(self.upload_dir, exist_ok=True)
        os.makedirs(self.output_dir, exist_ok=True)
        os.makedirs(self.temp_dir, exist_ok=True)
        
        # Adjust settings based on hardware tier
        if self.hardware.processing_tier == ProcessingTier.ULTRA:
            self.max_file_size_gb = 50.0
            self.max_concurrent_uploads = 20
            self.rate_limit_per_minute = 500
        
        # Set environment variables
        os.environ.setdefault("OMP_NUM_THREADS", str(self.hardware.available_cores))
        os.environ.setdefault("MKL_NUM_THREADS", str(self.hardware.available_cores))
        
    @classmethod
    def from_env(cls) -> "VideoRenderingConfig":
        """Create configuration from environment variables"""
        return cls(
            host=os.getenv("VIDEO_SERVICE_HOST", "0.0.0.0"),
            port=int(os.getenv("VIDEO_SERVICE_PORT", 8000)),
            debug=os.getenv("VIDEO_SERVICE_DEBUG", "false").lower() == "true",
            upload_dir=os.getenv("VIDEO_UPLOAD_DIR", "/tmp/video_uploads"),
            output_dir=os.getenv("VIDEO_OUTPUT_DIR", "/tmp/video_outputs"),
            temp_dir=os.getenv("VIDEO_TEMP_DIR", "/tmp/video_processing"),
            redis_host=os.getenv("REDIS_HOST", "localhost"),
            redis_port=int(os.getenv("REDIS_PORT", 6379)),
            redis_password=os.getenv("REDIS_PASSWORD"),
        )
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert configuration to dictionary"""
        return {
            "service": {
                "host": self.host,
                "port": self.port,
                "debug": self.debug,
            },
            "storage": {
                "upload_dir": self.upload_dir,
                "output_dir": self.output_dir,
                "temp_dir": self.temp_dir,
                "max_file_size_gb": self.max_file_size_gb,
            },
            "hardware": {
                "total_ram_gb": self.hardware.total_ram_gb,
                "available_cores": self.hardware.available_cores,
                "processing_tier": self.hardware.processing_tier.value,
                "is_elite_hardware": self.hardware.is_elite_hardware,
            },
            "ai_features": {
                "upscaling": self.enable_ai_upscaling,
                "noise_reduction": self.enable_noise_reduction,
                "color_enhancement": self.enable_color_enhancement,
                "object_detection": self.enable_object_detection,
                "scene_analysis": self.enable_scene_analysis,
                "audio_enhancement": self.enable_audio_enhancement,
            },
            "performance": {
                "gpu_acceleration": self.enable_gpu_acceleration,
                "memory_mapping": self.enable_memory_mapping,
                "chunk_processing": self.enable_chunk_processing,
                "advanced_caching": self.enable_advanced_caching,
            }
        }