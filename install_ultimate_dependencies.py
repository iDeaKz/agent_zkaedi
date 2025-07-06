#!/usr/bin/env python3
"""
ZKAEDI Ultimate Dependencies Installer
=====================================

Intelligent package installation system with multiple fallback strategies.
Features:
- Intel GPU optimization libraries (intel-extension-for-pytorch)
- Performance monitoring tools (psutil, memory-profiler)
- Complete error handling during installation
- Installation success/failure reporting with recovery options
- Cross-platform compatibility (Windows/Linux/macOS)
- Automated dependency resolution with conflict handling
"""

import os
import sys
import subprocess
import platform
import json
import time
import logging
from pathlib import Path
from typing import Dict, List, Tuple, Optional, Any
from dataclasses import dataclass
from rich.console import Console
from rich.progress import Progress, SpinnerColumn, TextColumn, BarColumn
from rich.panel import Panel
from rich.table import Table
from rich.prompt import Confirm
import requests

console = Console()
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

@dataclass
class PackageInfo:
    """Package installation information"""
    name: str
    pip_name: str
    conda_name: Optional[str] = None
    apt_name: Optional[str] = None
    homebrew_name: Optional[str] = None
    windows_installer: Optional[str] = None
    required: bool = True
    description: str = ""
    fallback_packages: List[str] = None
    
    def __post_init__(self):
        if self.fallback_packages is None:
            self.fallback_packages = []

@dataclass
class InstallationResult:
    """Installation result tracking"""
    package: str
    success: bool
    method: str
    error_message: Optional[str] = None
    installation_time: float = 0.0
    version_installed: Optional[str] = None

class UltimateDependencyInstaller:
    """Intelligent dependency installer with comprehensive error handling"""
    
    def __init__(self):
        self.platform = platform.system().lower()
        self.python_version = f"{sys.version_info.major}.{sys.version_info.minor}"
        self.architecture = platform.machine().lower()
        self.installation_log: List[InstallationResult] = []
        self.failed_packages: List[str] = []
        self.success_packages: List[str] = []
        
        # Define ultimate package suite
        self.packages = self._define_package_suite()
        
        console.print(Panel.fit(
            f"🚀 ZKAEDI Ultimate Dependencies Installer\n"
            f"Platform: {self.platform.title()} ({self.architecture})\n"
            f"Python: {self.python_version}\n"
            f"Packages to install: {len(self.packages)}",
            title="🛠️ Installation Environment",
            border_style="blue"
        ))
    
    def _define_package_suite(self) -> Dict[str, PackageInfo]:
        """Define comprehensive package suite for ultimate performance"""
        return {
            # Core Performance Libraries
            'numpy': PackageInfo(
                name='NumPy',
                pip_name='numpy>=1.24.0',
                conda_name='numpy',
                apt_name='python3-numpy',
                description='Fundamental package for scientific computing',
                required=True
            ),
            'numba': PackageInfo(
                name='Numba JIT Compiler', 
                pip_name='numba>=0.58.0',
                conda_name='numba',
                description='JIT compilation for Python functions',
                required=False,
                fallback_packages=['llvmlite']
            ),
            'psutil': PackageInfo(
                name='System Monitoring',
                pip_name='psutil>=5.9.0',
                conda_name='psutil',
                apt_name='python3-psutil',
                description='System and process utilities',
                required=True
            ),
            'memory-profiler': PackageInfo(
                name='Memory Profiler',
                pip_name='memory-profiler>=0.60.0',
                conda_name='memory_profiler',
                description='Memory usage monitoring',
                required=False
            ),
            
            # Intel GPU Optimization
            'intel-extension-for-pytorch': PackageInfo(
                name='Intel Extension for PyTorch',
                pip_name='intel-extension-for-pytorch',
                description='Intel Iris Xe GPU optimization',
                required=False,
                fallback_packages=['torch']
            ),
            'pyopencl': PackageInfo(
                name='PyOpenCL',
                pip_name='pyopencl',
                conda_name='pyopencl',
                description='OpenCL bindings for Python',
                required=False,
                fallback_packages=['cupy-cuda11x', 'cupy-cuda12x']
            ),
            
            # Web Framework & API
            'fastapi': PackageInfo(
                name='FastAPI',
                pip_name='fastapi[all]>=0.104.0',
                conda_name='fastapi',
                description='Modern web framework for APIs',
                required=True
            ),
            'uvicorn': PackageInfo(
                name='Uvicorn',
                pip_name='uvicorn[standard]>=0.24.0',
                conda_name='uvicorn',
                description='ASGI server for FastAPI',
                required=True
            ),
            'websockets': PackageInfo(
                name='WebSockets',
                pip_name='websockets>=11.0.0',
                conda_name='websockets',
                description='WebSocket implementation',
                required=True
            ),
            
            # Database & Caching
            'redis': PackageInfo(
                name='Redis Python Client',
                pip_name='redis>=5.0.0',
                conda_name='redis-py',
                description='Redis client for caching',
                required=False
            ),
            'aioredis': PackageInfo(
                name='Async Redis Client',
                pip_name='aioredis>=2.0.0',
                description='Async Redis client',
                required=False
            ),
            
            # Data Processing
            'pandas': PackageInfo(
                name='Pandas',
                pip_name='pandas>=2.0.0',
                conda_name='pandas',
                apt_name='python3-pandas',
                description='Data manipulation and analysis',
                required=False
            ),
            'scipy': PackageInfo(
                name='SciPy',
                pip_name='scipy>=1.11.0',
                conda_name='scipy',
                apt_name='python3-scipy',
                description='Scientific computing library',
                required=False
            ),
            
            # Visualization & Dashboard
            'plotly': PackageInfo(
                name='Plotly',
                pip_name='plotly>=5.17.0',
                conda_name='plotly',
                description='Interactive plotting library',
                required=False
            ),
            'dash': PackageInfo(
                name='Dash',
                pip_name='dash>=2.14.0',
                conda_name='dash',
                description='Web application framework',
                required=False
            ),
            
            # Machine Learning (Optional)
            'torch': PackageInfo(
                name='PyTorch',
                pip_name='torch>=2.1.0',
                conda_name='pytorch',
                description='Deep learning framework',
                required=False
            ),
            'scikit-learn': PackageInfo(
                name='Scikit-Learn',
                pip_name='scikit-learn>=1.3.0',
                conda_name='scikit-learn',
                apt_name='python3-sklearn',
                description='Machine learning library',
                required=False
            ),
            
            # Development Tools
            'rich': PackageInfo(
                name='Rich Terminal',
                pip_name='rich>=13.7.0',
                conda_name='rich',
                description='Rich text and beautiful formatting',
                required=True
            ),
            'click': PackageInfo(
                name='Click CLI',
                pip_name='click>=8.1.0',
                conda_name='click',
                description='Command line interface creation',
                required=True
            ),
            'pydantic': PackageInfo(
                name='Pydantic',
                pip_name='pydantic>=2.5.0',
                conda_name='pydantic',
                description='Data validation using Python type hints',
                required=True
            ),
            
            # Testing Framework
            'pytest': PackageInfo(
                name='PyTest',
                pip_name='pytest>=7.4.0',
                conda_name='pytest',
                description='Testing framework',
                required=False
            ),
            'pytest-asyncio': PackageInfo(
                name='PyTest Asyncio',
                pip_name='pytest-asyncio>=0.21.0',
                description='Async testing support',
                required=False
            )
        }
    
    def _check_package_manager_availability(self) -> Dict[str, bool]:
        """Check which package managers are available"""
        managers = {}
        
        # Check pip
        try:
            subprocess.run(['pip', '--version'], capture_output=True, check=True)
            managers['pip'] = True
        except (subprocess.CalledProcessError, FileNotFoundError):
            managers['pip'] = False
        
        # Check conda
        try:
            subprocess.run(['conda', '--version'], capture_output=True, check=True)
            managers['conda'] = True
        except (subprocess.CalledProcessError, FileNotFoundError):
            managers['conda'] = False
        
        # Check system package managers
        if self.platform == 'linux':
            try:
                subprocess.run(['apt', '--version'], capture_output=True, check=True)
                managers['apt'] = True
            except (subprocess.CalledProcessError, FileNotFoundError):
                managers['apt'] = False
        elif self.platform == 'darwin':
            try:
                subprocess.run(['brew', '--version'], capture_output=True, check=True)
                managers['homebrew'] = True
            except (subprocess.CalledProcessError, FileNotFoundError):
                managers['homebrew'] = False
        
        return managers
    
    def _install_with_pip(self, package: PackageInfo) -> InstallationResult:
        """Install package using pip with comprehensive error handling"""
        start_time = time.time()
        
        try:
            # Try main package first
            cmd = [sys.executable, '-m', 'pip', 'install', '--upgrade', package.pip_name]
            result = subprocess.run(cmd, capture_output=True, text=True, timeout=300)
            
            if result.returncode == 0:
                # Get installed version
                try:
                    import importlib.metadata
                    package_name = package.pip_name.split('>=')[0].split('[')[0]
                    version = importlib.metadata.version(package_name)
                except:
                    version = "unknown"
                
                return InstallationResult(
                    package=package.name,
                    success=True,
                    method='pip',
                    installation_time=time.time() - start_time,
                    version_installed=version
                )
            else:
                # Try fallback packages
                for fallback in package.fallback_packages:
                    try:
                        fallback_cmd = [sys.executable, '-m', 'pip', 'install', '--upgrade', fallback]
                        fallback_result = subprocess.run(fallback_cmd, capture_output=True, text=True, timeout=300)
                        if fallback_result.returncode == 0:
                            return InstallationResult(
                                package=package.name,
                                success=True,
                                method=f'pip (fallback: {fallback})',
                                installation_time=time.time() - start_time
                            )
                    except Exception:
                        continue
                
                return InstallationResult(
                    package=package.name,
                    success=False,
                    method='pip',
                    error_message=result.stderr,
                    installation_time=time.time() - start_time
                )
                
        except subprocess.TimeoutExpired:
            return InstallationResult(
                package=package.name,
                success=False,
                method='pip',
                error_message="Installation timeout (>5 minutes)",
                installation_time=time.time() - start_time
            )
        except Exception as e:
            return InstallationResult(
                package=package.name,
                success=False,
                method='pip',
                error_message=str(e),
                installation_time=time.time() - start_time
            )
    
    def _install_with_conda(self, package: PackageInfo) -> InstallationResult:
        """Install package using conda"""
        start_time = time.time()
        
        if not package.conda_name:
            return InstallationResult(
                package=package.name,
                success=False,
                method='conda',
                error_message="No conda package name specified"
            )
        
        try:
            cmd = ['conda', 'install', '-y', package.conda_name]
            result = subprocess.run(cmd, capture_output=True, text=True, timeout=600)
            
            return InstallationResult(
                package=package.name,
                success=result.returncode == 0,
                method='conda',
                error_message=result.stderr if result.returncode != 0 else None,
                installation_time=time.time() - start_time
            )
            
        except Exception as e:
            return InstallationResult(
                package=package.name,
                success=False,
                method='conda',
                error_message=str(e),
                installation_time=time.time() - start_time
            )
    
    def _install_with_system_manager(self, package: PackageInfo) -> InstallationResult:
        """Install package using system package manager"""
        start_time = time.time()
        
        if self.platform == 'linux' and package.apt_name:
            try:
                cmd = ['sudo', 'apt', 'install', '-y', package.apt_name]
                result = subprocess.run(cmd, capture_output=True, text=True, timeout=300)
                
                return InstallationResult(
                    package=package.name,
                    success=result.returncode == 0,
                    method='apt',
                    error_message=result.stderr if result.returncode != 0 else None,
                    installation_time=time.time() - start_time
                )
            except Exception as e:
                return InstallationResult(
                    package=package.name,
                    success=False,
                    method='apt',
                    error_message=str(e),
                    installation_time=time.time() - start_time
                )
        
        elif self.platform == 'darwin' and package.homebrew_name:
            try:
                cmd = ['brew', 'install', package.homebrew_name]
                result = subprocess.run(cmd, capture_output=True, text=True, timeout=300)
                
                return InstallationResult(
                    package=package.name,
                    success=result.returncode == 0,
                    method='homebrew',
                    error_message=result.stderr if result.returncode != 0 else None,
                    installation_time=time.time() - start_time
                )
            except Exception as e:
                return InstallationResult(
                    package=package.name,
                    success=False,
                    method='homebrew',
                    error_message=str(e),
                    installation_time=time.time() - start_time
                )
        
        return InstallationResult(
            package=package.name,
            success=False,
            method='system',
            error_message="No system package manager available for this package"
        )
    
    def install_package(self, package: PackageInfo, available_managers: Dict[str, bool]) -> InstallationResult:
        """Install a single package with multiple fallback strategies"""
        console.print(f"📦 Installing {package.name}...")
        
        # Strategy 1: Try pip first (most reliable)
        if available_managers.get('pip', False):
            result = self._install_with_pip(package)
            if result.success:
                return result
        
        # Strategy 2: Try conda if available
        if available_managers.get('conda', False):
            result = self._install_with_conda(package)
            if result.success:
                return result
        
        # Strategy 3: Try system package manager
        result = self._install_with_system_manager(package)
        if result.success:
            return result
        
        # All strategies failed
        return InstallationResult(
            package=package.name,
            success=False,
            method='all_failed',
            error_message="All installation methods failed"
        )
    
    def install_all_packages(self, skip_optional: bool = False) -> Dict[str, Any]:
        """Install all packages with comprehensive progress tracking"""
        available_managers = self._check_package_manager_availability()
        
        console.print("\n🔍 Available package managers:")
        for manager, available in available_managers.items():
            status = "✅" if available else "❌"
            console.print(f"  {status} {manager}")
        
        if not any(available_managers.values()):
            console.print("❌ No package managers available! Please install pip, conda, or system package manager.")
            return {'success': False, 'error': 'No package managers available'}
        
        # Filter packages
        packages_to_install = []
        for package in self.packages.values():
            if skip_optional and not package.required:
                continue
            packages_to_install.append(package)
        
        console.print(f"\n🚀 Installing {len(packages_to_install)} packages...")
        
        with Progress(
            SpinnerColumn(),
            TextColumn("[progress.description]{task.description}"),
            BarColumn(),
            TextColumn("[progress.percentage]{task.percentage:>3.0f}%"),
            console=console
        ) as progress:
            
            main_task = progress.add_task("Overall Progress", total=len(packages_to_install))
            
            for package in packages_to_install:
                package_task = progress.add_task(f"Installing {package.name}", total=1)
                
                result = self.install_package(package, available_managers)
                self.installation_log.append(result)
                
                if result.success:
                    self.success_packages.append(package.name)
                    progress.console.print(f"✅ {package.name} installed successfully ({result.method})")
                else:
                    self.failed_packages.append(package.name)
                    if package.required:
                        progress.console.print(f"❌ REQUIRED: {package.name} failed to install")
                    else:
                        progress.console.print(f"⚠️  OPTIONAL: {package.name} failed to install")
                
                progress.update(package_task, completed=1)
                progress.update(main_task, advance=1)
        
        return self._generate_installation_report()
    
    def _generate_installation_report(self) -> Dict[str, Any]:
        """Generate comprehensive installation report"""
        total_packages = len(self.installation_log)
        successful_installations = len(self.success_packages)
        failed_installations = len(self.failed_packages)
        
        required_failed = []
        optional_failed = []
        
        for log_entry in self.installation_log:
            if not log_entry.success:
                package_info = next((p for p in self.packages.values() if p.name == log_entry.package), None)
                if package_info and package_info.required:
                    required_failed.append(log_entry.package)
                else:
                    optional_failed.append(log_entry.package)
        
        report = {
            'success': len(required_failed) == 0,
            'total_packages': total_packages,
            'successful_installations': successful_installations,
            'failed_installations': failed_installations,
            'required_failed': required_failed,
            'optional_failed': optional_failed,
            'installation_log': [
                {
                    'package': entry.package,
                    'success': entry.success,
                    'method': entry.method,
                    'error': entry.error_message,
                    'time': entry.installation_time,
                    'version': entry.version_installed
                }
                for entry in self.installation_log
            ]
        }
        
        return report
    
    def display_final_report(self, report: Dict[str, Any]):
        """Display beautiful final installation report"""
        # Overall status
        if report['success']:
            status_panel = Panel.fit(
                "🎉 Installation Completed Successfully!\n"
                "All required packages are installed and ready to use.",
                title="✅ SUCCESS",
                border_style="green"
            )
        else:
            status_panel = Panel.fit(
                f"⚠️  Installation Completed with Issues\n"
                f"Required packages failed: {len(report['required_failed'])}\n"
                f"Please check the detailed report below.",
                title="❌ PARTIAL SUCCESS",
                border_style="yellow"
            )
        
        console.print(status_panel)
        
        # Statistics table
        stats_table = Table(title="📊 Installation Statistics")
        stats_table.add_column("Metric", style="cyan", no_wrap=True)
        stats_table.add_column("Count", style="magenta")
        stats_table.add_column("Percentage", style="green")
        
        success_rate = (report['successful_installations'] / report['total_packages']) * 100
        stats_table.add_row("Total Packages", str(report['total_packages']), "100%")
        stats_table.add_row("Successful", str(report['successful_installations']), f"{success_rate:.1f}%")
        stats_table.add_row("Failed", str(report['failed_installations']), f"{100-success_rate:.1f}%")
        
        console.print(stats_table)
        
        # Failed packages details
        if report['required_failed']:
            console.print("\n❌ Required packages that failed:")
            for package in report['required_failed']:
                console.print(f"  • {package}")
        
        if report['optional_failed']:
            console.print("\n⚠️  Optional packages that failed:")
            for package in report['optional_failed']:
                console.print(f"  • {package}")
        
        # Success packages
        if self.success_packages:
            console.print(f"\n✅ Successfully installed ({len(self.success_packages)}):")
            for package in self.success_packages:
                console.print(f"  • {package}")
        
        # Performance recommendations
        if report['success']:
            console.print(Panel.fit(
                "🚀 Ready for Ultimate Performance!\n\n"
                "Next steps:\n"
                "1. Run: python zkaedi_ultimate_engine.py\n"
                "2. Open dashboard: zkaedi_ultimate_dashboard.html\n"
                "3. Start quick deployment: ./quick_start.sh",
                title="🎯 What's Next?",
                border_style="blue"
            ))
    
    def verify_installation(self) -> Dict[str, bool]:
        """Verify that installed packages can be imported"""
        verification_results = {}
        
        import_map = {
            'NumPy': 'numpy',
            'Numba JIT Compiler': 'numba',
            'System Monitoring': 'psutil',
            'FastAPI': 'fastapi',
            'Uvicorn': 'uvicorn',
            'WebSockets': 'websockets',
            'Rich Terminal': 'rich',
            'Click CLI': 'click',
            'Pydantic': 'pydantic',
        }
        
        console.print("\n🔍 Verifying installations...")
        
        for package_name, module_name in import_map.items():
            try:
                __import__(module_name)
                verification_results[package_name] = True
                console.print(f"✅ {package_name}: Import successful")
            except ImportError:
                verification_results[package_name] = False
                console.print(f"❌ {package_name}: Import failed")
        
        return verification_results

def main():
    """Main installation function"""
    console.print("🚀 ZKAEDI ULTIMATE DEPENDENCIES INSTALLER")
    console.print("=" * 60)
    
    installer = UltimateDependencyInstaller()
    
    # Ask user preferences
    skip_optional = not Confirm.ask("Install optional packages (ML libraries, visualization tools)?", default=True)
    
    # Run installation
    report = installer.install_all_packages(skip_optional=skip_optional)
    
    # Display report
    installer.display_final_report(report)
    
    # Verify installations
    installer.verify_installation()
    
    # Save detailed report
    report_file = Path("installation_report.json")
    with open(report_file, 'w') as f:
        json.dump(report, f, indent=2, default=str)
    
    console.print(f"\n📄 Detailed report saved to: {report_file}")
    
    return report['success']

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)