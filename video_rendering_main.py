#!/usr/bin/env python3
"""
🚀 Elite AI Video Rendering Service - Main Application

World-class AI video rendering service optimized for elite hardware configuration.
"""

import asyncio
import logging
import sys
from pathlib import Path

# Add the current directory to Python path
sys.path.insert(0, str(Path(__file__).parent))

from video_rendering_service.config import VideoRenderingConfig
from video_rendering_service.api import run_server

def setup_logging(debug: bool = False):
    """Setup application logging"""
    level = logging.DEBUG if debug else logging.INFO
    
    logging.basicConfig(
        level=level,
        format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
        handlers=[
            logging.StreamHandler(sys.stdout),
            logging.FileHandler("video_rendering_service.log")
        ]
    )
    
    # Reduce noise from external libraries
    logging.getLogger("uvicorn").setLevel(logging.WARNING)
    logging.getLogger("uvicorn.access").setLevel(logging.WARNING)
    logging.getLogger("asyncio").setLevel(logging.WARNING)

async def main():
    """Main application entry point"""
    print("🎬 Elite AI Video Rendering Service")
    print("=" * 50)
    print("Optimized for elite hardware configuration:")
    print("- 64GB RAM Corsair Vengeance Dual Channel")
    print("- 8TB SSD NVMe Samsung 990 Pro")
    print("- Intel Iris Xe GPU")
    print("- Allocated GPU from libraries")
    print("=" * 50)
    
    # Load configuration
    config = VideoRenderingConfig.from_env()
    
    # Setup logging
    setup_logging(config.debug)
    logger = logging.getLogger(__name__)
    
    # Display configuration
    logger.info("Configuration loaded:")
    logger.info(f"  Service: {config.host}:{config.port}")
    logger.info(f"  Hardware Tier: {config.hardware.processing_tier.value}")
    logger.info(f"  RAM: {config.hardware.total_ram_gb:.1f}GB")
    logger.info(f"  CPU Cores: {config.hardware.available_cores}")
    logger.info(f"  Elite Hardware: {config.hardware.is_elite_hardware}")
    logger.info(f"  Max Concurrent Jobs: {config.hardware.max_concurrent_jobs}")
    logger.info(f"  GPU Acceleration: {config.enable_gpu_acceleration}")
    logger.info(f"  AI Features Enabled: {sum([
        config.enable_ai_upscaling,
        config.enable_noise_reduction,
        config.enable_color_enhancement,
        config.enable_object_detection,
        config.enable_scene_analysis,
        config.enable_audio_enhancement
    ])}/6")
    
    try:
        # Start the service
        logger.info("Starting Elite AI Video Rendering Service...")
        await run_server(config)
        
    except KeyboardInterrupt:
        logger.info("Service stopped by user")
    except Exception as e:
        logger.error(f"Service failed to start: {e}")
        sys.exit(1)

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\n👋 Elite AI Video Rendering Service stopped")
    except Exception as e:
        print(f"❌ Fatal error: {e}")
        sys.exit(1)