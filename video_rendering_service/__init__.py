"""
🎬 Elite AI Video Rendering Service

World-class AI video rendering service optimized for elite hardware:
- 64GB RAM Corsair Vengeance Dual Channel
- 8TB SSD NVMe Samsung 990 Pro  
- Intel Iris Xe GPU
- Allocated GPU from libraries

Features:
- AI-powered video enhancement
- Real-time processing and progress tracking
- Advanced error handling and recovery
- Performance optimization for elite hardware
- Comprehensive monitoring and analytics
"""

__version__ = "1.0.0"
__author__ = "Elite AI System"

# Import core components
from .core import VideoRenderingEngine
from .config import VideoRenderingConfig

# Conditionally import API components
try:
    from .api import create_app
    __all__ = ["VideoRenderingEngine", "create_app", "VideoRenderingConfig"]
except ImportError:
    # FastAPI not available, skip API imports
    __all__ = ["VideoRenderingEngine", "VideoRenderingConfig"]