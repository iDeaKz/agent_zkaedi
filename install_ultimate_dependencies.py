#!/usr/bin/env python3
"""
🛠️ ZKAEDI Ultimate Dependencies Installer
Intelligent package installation with fallbacks and Intel GPU optimization libraries

Features:
- Bulletproof installation with error recovery
- Intel GPU optimization libraries  
- Performance monitoring tools
- Complete error handling during installation
- Installation success/failure reporting
"""

import asyncio
import json
import logging
import os
import platform
import subprocess
import sys
import time
from pathlib import Path
from typing import Dict, List, Any, Optional, Tuple
from dataclasses import dataclass, asdict

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

@dataclass
class DependencyInfo:
    """Information about a dependency"""
    name: str
    version: Optional[str] = None
    description: str = ""
    required: bool = True
    category: str = "core"
    install_command: List[str] = None
    fallback_packages: List[str] = None
    post_install_check: Optional[str] = None

@dataclass
class InstallationResult:
    """Result of dependency installation"""
    package: str
    success: bool
    install_time: float
    error_message: Optional[str] = None
    fallback_used: Optional[str] = None
    version_installed: Optional[str] = None

class UltimateDependencyInstaller:
    """Ultimate dependency installer with intelligent fallbacks"""
    
    def __init__(self):
        self.installation_results = []
        self.failed_packages = []
        self.successful_packages = []
        self.system_info = self._get_system_info()
        
        # Define comprehensive dependency list
        self.dependencies = self._define_dependencies()
        
        logger.info("🛠️ Ultimate Dependency Installer initialized")
        logger.info(f"System: {self.system_info['platform']} {self.system_info['architecture']}")
    
    def _get_system_info(self) -> Dict[str, Any]:
        """Get comprehensive system information"""
        return {
            "platform": platform.system(),
            "architecture": platform.architecture()[0],
            "python_version": platform.python_version(),
            "cpu_count": os.cpu_count(),
            "is_gpu_system": self._detect_gpu_capabilities(),
            "package_managers": self._detect_package_managers()
        }
    
    def _detect_gpu_capabilities(self) -> Dict[str, bool]:
        """Detect GPU capabilities for optimization libraries"""
        gpu_info = {
            "intel_gpu": False,
            "nvidia_gpu": False,
            "amd_gpu": False,
            "opencl_support": False
        }
        
        try:
            if platform.system() == "Windows":
                # Windows GPU detection
                result = subprocess.run(['wmic', 'path', 'win32_VideoController', 'get', 'name'], 
                                      capture_output=True, text=True, timeout=10)
                gpu_output = result.stdout.lower()
                gpu_info["intel_gpu"] = "intel" in gpu_output
                gpu_info["nvidia_gpu"] = "nvidia" in gpu_output
                gpu_info["amd_gpu"] = "amd" in gpu_output or "radeon" in gpu_output
                
            elif platform.system() == "Linux":
                # Linux GPU detection
                try:
                    with open('/proc/cpuinfo', 'r') as f:
                        cpu_info = f.read().lower()
                    gpu_info["intel_gpu"] = "intel" in cpu_info
                    
                    # Check for discrete GPUs
                    result = subprocess.run(['lspci'], capture_output=True, text=True, timeout=5)
                    if result.returncode == 0:
                        pci_info = result.stdout.lower()
                        gpu_info["nvidia_gpu"] = "nvidia" in pci_info
                        gpu_info["amd_gpu"] = "amd" in pci_info or "radeon" in pci_info
                except:
                    pass
                    
        except Exception as e:
            logger.warning(f"Could not detect GPU capabilities: {e}")
        
        return gpu_info
    
    def _detect_package_managers(self) -> List[str]:
        """Detect available package managers"""
        managers = []
        
        # Check for pip
        try:
            subprocess.run([sys.executable, '-m', 'pip', '--version'], 
                         capture_output=True, timeout=5)
            managers.append('pip')
        except:
            pass
        
        # Check for conda
        try:
            subprocess.run(['conda', '--version'], capture_output=True, timeout=5)
            managers.append('conda')
        except:
            pass
        
        # Check for system package managers
        if platform.system() == "Linux":
            for cmd in ['apt', 'yum', 'dnf', 'pacman']:
                try:
                    subprocess.run([cmd, '--version'], capture_output=True, timeout=5)
                    managers.append(cmd)
                    break
                except:
                    continue
        
        return managers
    
    def _define_dependencies(self) -> List[DependencyInfo]:
        """Define comprehensive dependency list with Intel GPU optimizations"""
        dependencies = [
            # Core performance libraries
            DependencyInfo(
                name="numba",
                version=">=0.58.0",
                description="JIT compiler for maximum performance",
                category="performance",
                install_command=[sys.executable, "-m", "pip", "install", "numba"],
                post_install_check="import numba; numba.jit"
            ),
            DependencyInfo(
                name="numpy",
                version=">=1.21.0", 
                description="Numerical computing foundation",
                category="core",
                install_command=[sys.executable, "-m", "pip", "install", "numpy"],
                post_install_check="import numpy; numpy.array([1,2,3])"
            ),
            DependencyInfo(
                name="scipy",
                version=">=1.8.0",
                description="Scientific computing library",
                category="performance",
                install_command=[sys.executable, "-m", "pip", "install", "scipy"],
                post_install_check="import scipy; scipy.__version__"
            ),
            
            # Intel GPU optimization libraries
            DependencyInfo(
                name="intel-extension-for-pytorch",
                description="Intel GPU acceleration for PyTorch",
                category="intel_gpu",
                required=False,
                install_command=[sys.executable, "-m", "pip", "install", "intel-extension-for-pytorch"],
                fallback_packages=["torch"],
                post_install_check="import intel_extension_for_pytorch"
            ),
            DependencyInfo(
                name="intel-extension-for-tensorflow",
                description="Intel optimizations for TensorFlow",
                category="intel_gpu", 
                required=False,
                install_command=[sys.executable, "-m", "pip", "install", "intel-extension-for-tensorflow"],
                fallback_packages=["tensorflow-cpu"],
                post_install_check="import tensorflow"
            ),
            DependencyInfo(
                name="oneapi-toolkit",
                description="Intel OneAPI toolkit for GPU computing",
                category="intel_gpu",
                required=False,
                install_command=["wget", "-O-", "https://apt.repos.intel.com/intel-gpg-keys/GPG-PUB-KEY-INTEL-SW-PRODUCTS.PUB"],
                fallback_packages=["opencl-headers"]
            ),
            
            # Performance monitoring
            DependencyInfo(
                name="psutil",
                version=">=5.9.0",
                description="System and process monitoring",
                category="monitoring",
                install_command=[sys.executable, "-m", "pip", "install", "psutil"],
                post_install_check="import psutil; psutil.cpu_percent()"
            ),
            DependencyInfo(
                name="py-spy",
                description="Sampling profiler for Python",
                category="monitoring",
                required=False,
                install_command=[sys.executable, "-m", "pip", "install", "py-spy"],
                post_install_check="import py_spy"
            ),
            DependencyInfo(
                name="memory-profiler",
                description="Memory usage profiling",
                category="monitoring",
                required=False,
                install_command=[sys.executable, "-m", "pip", "install", "memory-profiler"],
                post_install_check="import memory_profiler"
            ),
            
            # Caching and optimization
            DependencyInfo(
                name="cachetools",
                version=">=5.0.0",
                description="Advanced caching utilities",
                category="performance",
                install_command=[sys.executable, "-m", "pip", "install", "cachetools"],
                post_install_check="import cachetools; cachetools.TTLCache(100, 60)"
            ),
            DependencyInfo(
                name="joblib",
                version=">=1.2.0",
                description="Parallel computing and caching",
                category="performance", 
                install_command=[sys.executable, "-m", "pip", "install", "joblib"],
                post_install_check="import joblib; joblib.Parallel"
            ),
            
            # Visualization and dashboard
            DependencyInfo(
                name="plotly",
                version=">=5.0.0",
                description="Interactive visualization for dashboard",
                category="visualization",
                install_command=[sys.executable, "-m", "pip", "install", "plotly"],
                post_install_check="import plotly; plotly.__version__"
            ),
            DependencyInfo(
                name="dash",
                description="Web dashboard framework",
                category="visualization",
                required=False,
                install_command=[sys.executable, "-m", "pip", "install", "dash"],
                post_install_check="import dash"
            ),
            DependencyInfo(
                name="matplotlib",
                version=">=3.5.0",
                description="Plotting library for performance charts",
                category="visualization",
                install_command=[sys.executable, "-m", "pip", "install", "matplotlib"],
                post_install_check="import matplotlib; matplotlib.__version__"
            ),
            
            # Machine learning acceleration
            DependencyInfo(
                name="scikit-learn",
                version=">=1.2.0",
                description="Machine learning library with optimizations",
                category="ml",
                install_command=[sys.executable, "-m", "pip", "install", "scikit-learn"],
                post_install_check="import sklearn; sklearn.__version__"
            ),
            DependencyInfo(
                name="xgboost",
                description="Gradient boosting with GPU support",
                category="ml",
                required=False,
                install_command=[sys.executable, "-m", "pip", "install", "xgboost"],
                post_install_check="import xgboost"
            ),
            
            # Async and networking
            DependencyInfo(
                name="aiofiles",
                description="Asynchronous file operations",
                category="async",
                install_command=[sys.executable, "-m", "pip", "install", "aiofiles"],
                post_install_check="import aiofiles"
            ),
            DependencyInfo(
                name="asyncio-mqtt",
                description="Asynchronous MQTT client",
                category="async",
                required=False,
                install_command=[sys.executable, "-m", "pip", "install", "asyncio-mqtt"],
                post_install_check="import asyncio_mqtt"
            ),
            
            # Development tools
            DependencyInfo(
                name="rich",
                description="Rich text and beautiful formatting",
                category="dev",
                required=False,
                install_command=[sys.executable, "-m", "pip", "install", "rich"],
                post_install_check="import rich; rich.__version__"
            ),
            DependencyInfo(
                name="click",
                description="Command line interface creation",
                category="dev",
                required=False,
                install_command=[sys.executable, "-m", "pip", "install", "click"],
                post_install_check="import click"
            ),
        ]
        
        return dependencies
    
    async def install_all_dependencies(self, 
                                     categories: Optional[List[str]] = None,
                                     skip_optional: bool = False) -> Dict[str, Any]:
        """Install all dependencies with intelligent fallbacks"""
        
        if categories is None:
            categories = ["core", "performance", "monitoring", "visualization"]
            
            # Add Intel GPU categories if Intel GPU detected
            if self.system_info["is_gpu_system"].get("intel_gpu", False):
                categories.append("intel_gpu")
                logger.info("🎮 Intel GPU detected - including Intel optimization libraries")
        
        logger.info(f"🚀 Starting installation of {len(self.dependencies)} dependencies...")
        logger.info(f"Categories: {categories}")
        
        start_time = time.time()
        
        # Filter dependencies by category and requirements
        to_install = [
            dep for dep in self.dependencies
            if dep.category in categories and (not skip_optional or dep.required)
        ]
        
        logger.info(f"Installing {len(to_install)} packages...")
        
        # Install dependencies concurrently (with rate limiting)
        semaphore = asyncio.Semaphore(3)  # Limit concurrent installations
        
        tasks = [
            self._install_dependency_with_semaphore(semaphore, dep)
            for dep in to_install
        ]
        
        results = await asyncio.gather(*tasks, return_exceptions=True)
        
        # Process results
        for result in results:
            if isinstance(result, InstallationResult):
                self.installation_results.append(result)
                if result.success:
                    self.successful_packages.append(result.package)
                else:
                    self.failed_packages.append(result.package)
            elif isinstance(result, Exception):
                logger.error(f"Installation task failed: {result}")
        
        end_time = time.time()
        total_time = end_time - start_time
        
        # Generate installation report
        report = self._generate_installation_report(total_time)
        
        logger.info(f"✅ Installation complete in {total_time:.1f}s")
        logger.info(f"Success: {len(self.successful_packages)}/{len(to_install)} packages")
        
        if self.failed_packages:
            logger.warning(f"Failed packages: {self.failed_packages}")
        
        return report
    
    async def _install_dependency_with_semaphore(self, 
                                               semaphore: asyncio.Semaphore,
                                               dependency: DependencyInfo) -> InstallationResult:
        """Install single dependency with semaphore control"""
        async with semaphore:
            return await self._install_single_dependency(dependency)
    
    async def _install_single_dependency(self, dependency: DependencyInfo) -> InstallationResult:
        """Install a single dependency with fallback handling"""
        
        logger.info(f"📦 Installing {dependency.name} ({dependency.category})")
        start_time = time.time()
        
        try:
            # Try primary installation
            success = await self._try_install_package(dependency.install_command, dependency.name)
            
            if success:
                # Verify installation
                if dependency.post_install_check:
                    verification_success = await self._verify_installation(dependency.post_install_check)
                    if not verification_success:
                        logger.warning(f"⚠️ {dependency.name} installed but verification failed")
                
                install_time = time.time() - start_time
                version = await self._get_package_version(dependency.name)
                
                logger.info(f"✅ {dependency.name} installed successfully in {install_time:.1f}s")
                
                return InstallationResult(
                    package=dependency.name,
                    success=True,
                    install_time=install_time,
                    version_installed=version
                )
            
            # Try fallback packages if primary failed
            if dependency.fallback_packages:
                for fallback in dependency.fallback_packages:
                    logger.info(f"🔄 Trying fallback: {fallback}")
                    fallback_cmd = [sys.executable, "-m", "pip", "install", fallback]
                    
                    success = await self._try_install_package(fallback_cmd, fallback)
                    if success:
                        install_time = time.time() - start_time
                        version = await self._get_package_version(fallback)
                        
                        logger.info(f"✅ {fallback} (fallback) installed successfully")
                        
                        return InstallationResult(
                            package=dependency.name,
                            success=True,
                            install_time=install_time,
                            fallback_used=fallback,
                            version_installed=version
                        )
            
            # All attempts failed
            install_time = time.time() - start_time
            error_msg = f"Failed to install {dependency.name} and all fallbacks"
            
            logger.error(f"❌ {error_msg}")
            
            return InstallationResult(
                package=dependency.name,
                success=False,
                install_time=install_time,
                error_message=error_msg
            )
            
        except Exception as e:
            install_time = time.time() - start_time
            error_msg = f"Exception during installation: {str(e)}"
            
            logger.error(f"💥 {dependency.name}: {error_msg}")
            
            return InstallationResult(
                package=dependency.name,
                success=False,
                install_time=install_time,
                error_message=error_msg
            )
    
    async def _try_install_package(self, install_command: List[str], package_name: str) -> bool:
        """Try to install a package with the given command"""
        try:
            # Run installation command
            process = await asyncio.create_subprocess_exec(
                *install_command,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE
            )
            
            stdout, stderr = await asyncio.wait_for(process.communicate(), timeout=300)  # 5 min timeout
            
            if process.returncode == 0:
                return True
            else:
                logger.warning(f"⚠️ {package_name} installation failed: {stderr.decode()[:200]}")
                return False
                
        except asyncio.TimeoutError:
            logger.error(f"⏰ {package_name} installation timed out")
            return False
        except Exception as e:
            logger.error(f"💥 {package_name} installation exception: {e}")
            return False
    
    async def _verify_installation(self, check_code: str) -> bool:
        """Verify package installation by running check code"""
        try:
            process = await asyncio.create_subprocess_exec(
                sys.executable, "-c", check_code,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE
            )
            
            stdout, stderr = await asyncio.wait_for(process.communicate(), timeout=30)
            return process.returncode == 0
            
        except Exception:
            return False
    
    async def _get_package_version(self, package_name: str) -> Optional[str]:
        """Get installed package version"""
        try:
            process = await asyncio.create_subprocess_exec(
                sys.executable, "-m", "pip", "show", package_name,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE
            )
            
            stdout, stderr = await asyncio.wait_for(process.communicate(), timeout=10)
            
            if process.returncode == 0:
                output = stdout.decode()
                for line in output.split('\n'):
                    if line.startswith('Version:'):
                        return line.split(':', 1)[1].strip()
            
            return None
            
        except Exception:
            return None
    
    def _generate_installation_report(self, total_time: float) -> Dict[str, Any]:
        """Generate comprehensive installation report"""
        successful_count = len(self.successful_packages)
        failed_count = len(self.failed_packages)
        total_count = successful_count + failed_count
        
        # Calculate category statistics
        category_stats = {}
        for result in self.installation_results:
            dep = next((d for d in self.dependencies if d.name == result.package), None)
            if dep:
                category = dep.category
                if category not in category_stats:
                    category_stats[category] = {"success": 0, "failed": 0, "total": 0}
                
                category_stats[category]["total"] += 1
                if result.success:
                    category_stats[category]["success"] += 1
                else:
                    category_stats[category]["failed"] += 1
        
        report = {
            "installation_summary": {
                "total_packages": total_count,
                "successful_installations": successful_count,
                "failed_installations": failed_count,
                "success_rate_percent": (successful_count / total_count * 100) if total_count > 0 else 0,
                "total_time_seconds": total_time,
                "average_time_per_package": total_time / total_count if total_count > 0 else 0
            },
            "category_breakdown": category_stats,
            "successful_packages": self.successful_packages,
            "failed_packages": self.failed_packages,
            "detailed_results": [asdict(result) for result in self.installation_results],
            "system_info": self.system_info,
            "recommendations": self._generate_recommendations()
        }
        
        return report
    
    def _generate_recommendations(self) -> List[str]:
        """Generate recommendations based on installation results"""
        recommendations = []
        
        # Check for critical failures
        critical_packages = ["numpy", "numba", "psutil"]
        failed_critical = [pkg for pkg in critical_packages if pkg in self.failed_packages]
        
        if failed_critical:
            recommendations.append(f"❗ Critical packages failed: {failed_critical}. System may not perform optimally.")
        
        # Check for Intel GPU optimization
        if self.system_info["is_gpu_system"].get("intel_gpu", False):
            intel_packages = ["intel-extension-for-pytorch", "intel-extension-for-tensorflow"]
            failed_intel = [pkg for pkg in intel_packages if pkg in self.failed_packages]
            
            if failed_intel:
                recommendations.append("🎮 Intel GPU optimizations failed. Consider manual Intel OneAPI installation.")
        
        # Check for monitoring tools
        monitoring_packages = ["psutil", "py-spy", "memory-profiler"]
        failed_monitoring = [pkg for pkg in monitoring_packages if pkg in self.failed_packages]
        
        if failed_monitoring:
            recommendations.append("📊 Some monitoring tools failed. Performance insights may be limited.")
        
        # Success recommendations
        if len(self.failed_packages) == 0:
            recommendations.append("🎉 Perfect installation! All packages installed successfully.")
        elif len(self.failed_packages) <= 2:
            recommendations.append("✅ Excellent installation success rate. System ready for optimization.")
        
        return recommendations
    
    async def install_system_dependencies(self) -> Dict[str, Any]:
        """Install system-level dependencies (requires admin privileges)"""
        logger.info("🔧 Installing system dependencies...")
        
        system_deps = []
        
        if platform.system() == "Linux":
            system_deps = [
                "build-essential",
                "python3-dev",
                "libblas-dev",
                "liblapack-dev",
                "gfortran",
                "opencl-headers",
                "ocl-icd-opencl-dev"
            ]
        elif platform.system() == "Darwin":  # macOS
            system_deps = [
                "gcc",
                "libomp"
            ]
        
        # Try to install system dependencies
        results = []
        for dep in system_deps:
            try:
                if platform.system() == "Linux" and "apt" in self.system_info["package_managers"]:
                    cmd = ["sudo", "apt", "install", "-y", dep]
                elif platform.system() == "Darwin":
                    cmd = ["brew", "install", dep]
                else:
                    continue
                
                process = await asyncio.create_subprocess_exec(
                    *cmd,
                    stdout=asyncio.subprocess.PIPE,
                    stderr=asyncio.subprocess.PIPE
                )
                
                stdout, stderr = await asyncio.wait_for(process.communicate(), timeout=300)
                
                results.append({
                    "package": dep,
                    "success": process.returncode == 0,
                    "error": stderr.decode() if process.returncode != 0 else None
                })
                
            except Exception as e:
                results.append({
                    "package": dep,
                    "success": False,
                    "error": str(e)
                })
        
        return {
            "system_dependencies": results,
            "total_attempted": len(system_deps),
            "successful": sum(1 for r in results if r["success"])
        }
    
    def save_installation_report(self, report: Dict[str, Any], filename: str = "installation_report.json"):
        """Save installation report to file"""
        try:
            with open(filename, 'w') as f:
                json.dump(report, f, indent=2, default=str)
            logger.info(f"📄 Installation report saved to {filename}")
        except Exception as e:
            logger.error(f"Failed to save report: {e}")

async def main():
    """Main function for dependency installation"""
    installer = UltimateDependencyInstaller()
    
    logger.info("🚀 ZKAEDI Ultimate Dependencies Installer")
    logger.info("=" * 60)
    
    try:
        # Install Python dependencies
        report = await installer.install_all_dependencies(
            categories=["core", "performance", "monitoring", "visualization"],
            skip_optional=False
        )
        
        # Display results
        summary = report["installation_summary"]
        logger.info("\n📊 INSTALLATION SUMMARY")
        logger.info("=" * 40)
        logger.info(f"✅ Successful: {summary['successful_installations']}")
        logger.info(f"❌ Failed: {summary['failed_installations']}")
        logger.info(f"📈 Success Rate: {summary['success_rate_percent']:.1f}%")
        logger.info(f"⏱️ Total Time: {summary['total_time_seconds']:.1f}s")
        
        if report["recommendations"]:
            logger.info("\n💡 RECOMMENDATIONS")
            logger.info("=" * 40)
            for rec in report["recommendations"]:
                logger.info(f"  {rec}")
        
        # Save detailed report
        installer.save_installation_report(report, "zkaedi_installation_report.json")
        
        logger.info("\n🎉 Installation process complete!")
        
        return report
        
    except Exception as e:
        logger.error(f"💥 Installation failed: {e}")
        return {"error": str(e)}

if __name__ == "__main__":
    asyncio.run(main())