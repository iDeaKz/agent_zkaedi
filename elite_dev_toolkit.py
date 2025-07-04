#!/usr/bin/env python3
"""
Elite AI System - Developer Experience Toolkit
Comprehensive development tools for elite productivity
"""

import os
import sys
import json
import time
import subprocess
import argparse
from pathlib import Path
from typing import Dict, List, Any, Optional, Tuple
import requests
import yaml
from dataclasses import dataclass
from rich.console import Console
from rich.table import Table
from rich.progress import Progress, SpinnerColumn, TextColumn
from rich.panel import Panel
from rich.syntax import Syntax
from rich.prompt import Prompt, Confirm
import docker
import psutil


console = Console()


@dataclass
class EliteDevConfig:
    """Configuration for Elite Development Environment"""
    project_root: Path
    api_url: str = "http://localhost:8000"
    dashboard_url: str = "http://localhost:3000"
    database_url: str = "postgresql://localhost:5432/elite_ai"
    redis_url: str = "redis://localhost:6379"
    docker_compose_file: str = "docker-compose.yml"
    test_patterns: List[str] = None
    
    def __post_init__(self):
        if self.test_patterns is None:
            self.test_patterns = ["test_*.py", "*_test.py", "tests/*.py"]


class EliteDevToolkit:
    """Elite Developer Experience Toolkit - Your coding companion"""
    
    def __init__(self, config: EliteDevConfig):
        self.config = config
        self.docker_client = None
        try:
            self.docker_client = docker.from_env()
        except Exception:
            console.print("⚠️  Docker not available", style="yellow")
    
    def status(self) -> Dict[str, Any]:
        """Get comprehensive system status"""
        console.print("🔍 Checking Elite AI System Status...", style="cyan")
        
        status = {
            "timestamp": time.strftime("%Y-%m-%d %H:%M:%S"),
            "system": self._check_system_health(),
            "services": self._check_services(),
            "database": self._check_database(),
            "tests": self._check_test_status(),
            "dependencies": self._check_dependencies(),
            "performance": self._check_performance()
        }
        
        self._display_status(status)
        return status
    
    def _check_system_health(self) -> Dict[str, Any]:
        """Check overall system health"""
        health = {
            "cpu_usage": psutil.cpu_percent(interval=1),
            "memory_usage": psutil.virtual_memory().percent,
            "disk_usage": psutil.disk_usage('/').percent,
            "load_average": os.getloadavg() if hasattr(os, 'getloadavg') else None
        }
        
        # API health check
        try:
            response = requests.get(f"{self.config.api_url}/health", timeout=5)
            health["api_status"] = "healthy" if response.status_code == 200 else "unhealthy"
            health["api_response_time"] = response.elapsed.total_seconds()
        except Exception as e:
            health["api_status"] = "error"
            health["api_error"] = str(e)
        
        return health
    
    def _check_services(self) -> Dict[str, Any]:
        """Check Docker services status"""
        services = {}
        
        if not self.docker_client:
            return {"error": "Docker not available"}
        
        try:
            containers = self.docker_client.containers.list(all=True)
            for container in containers:
                if any(name in container.name for name in ['elite', 'postgres', 'redis', 'nginx']):
                    services[container.name] = {
                        "status": container.status,
                        "health": getattr(container.attrs.get('State', {}), 'Health', {}).get('Status'),
                        "ports": container.ports,
                        "created": container.attrs['Created']
                    }
        except Exception as e:
            services["error"] = str(e)
        
        return services
    
    def _check_database(self) -> Dict[str, Any]:
        """Check database connectivity and status"""
        db_status = {}
        
        try:
            # Try to connect via API
            response = requests.get(f"{self.config.api_url}/health/database", timeout=5)
            if response.status_code == 200:
                db_status["connection"] = "healthy"
                db_data = response.json()
                db_status.update(db_data)
            else:
                db_status["connection"] = "unhealthy"
        except Exception as e:
            db_status["connection"] = "error"
            db_status["error"] = str(e)
        
        return db_status
    
    def _check_test_status(self) -> Dict[str, Any]:
        """Check test suite status"""
        test_status = {
            "last_run": None,
            "total_tests": 0,
            "passed": 0,
            "failed": 0,
            "coverage": None
        }
        
        # Check for test results file
        test_results_file = self.config.project_root / "test_results.json"
        if test_results_file.exists():
            try:
                with open(test_results_file) as f:
                    results = json.load(f)
                    test_status.update(results)
            except Exception:
                pass
        
        # Check for coverage report
        coverage_file = self.config.project_root / ".coverage"
        if coverage_file.exists():
            try:
                result = subprocess.run(
                    ["coverage", "report", "--format=json"],
                    capture_output=True, text=True, cwd=self.config.project_root
                )
                if result.returncode == 0:
                    coverage_data = json.loads(result.stdout)
                    test_status["coverage"] = coverage_data.get("totals", {}).get("percent_covered")
            except Exception:
                pass
        
        return test_status
    
    def _check_dependencies(self) -> Dict[str, Any]:
        """Check dependency status and conflicts"""
        deps_status = {
            "outdated": [],
            "conflicts": [],
            "security_issues": []
        }
        
        try:
            # Check for outdated packages
            result = subprocess.run(
                ["pip", "list", "--outdated", "--format=json"],
                capture_output=True, text=True
            )
            if result.returncode == 0:
                deps_status["outdated"] = json.loads(result.stdout)
        except Exception:
            pass
        
        try:
            # Check for security issues
            result = subprocess.run(
                ["safety", "check", "--json"],
                capture_output=True, text=True
            )
            if result.returncode != 0:  # Safety returns non-zero when issues found
                deps_status["security_issues"] = json.loads(result.stdout)
        except Exception:
            pass
        
        return deps_status
    
    def _check_performance(self) -> Dict[str, Any]:
        """Check system performance metrics"""
        performance = {}
        
        try:
            # API performance test
            start_time = time.time()
            response = requests.get(f"{self.config.api_url}/health")
            end_time = time.time()
            
            if response.status_code == 200:
                performance["api_response_time"] = end_time - start_time
                performance["api_status"] = "ok"
            else:
                performance["api_status"] = "slow"
        except Exception:
            performance["api_status"] = "error"
        
        return performance
    
    def _display_status(self, status: Dict[str, Any]):
        """Display system status in a beautiful format"""
        # System Health Panel
        health = status["system"]
        health_panel = Panel(
            f"🖥️  CPU: {health['cpu_usage']:.1f}%\n"
            f"💾 Memory: {health['memory_usage']:.1f}%\n"
            f"💿 Disk: {health['disk_usage']:.1f}%\n"
            f"🌐 API: {health.get('api_status', 'unknown')} "
            f"({health.get('api_response_time', 0):.3f}s)",
            title="System Health",
            border_style="green" if health.get('api_status') == 'healthy' else "red"
        )
        
        # Services Table
        services_table = Table(title="Docker Services")
        services_table.add_column("Service", style="cyan")
        services_table.add_column("Status", style="green")
        services_table.add_column("Health", style="blue")
        
        for service_name, service_info in status["services"].items():
            if isinstance(service_info, dict):
                services_table.add_row(
                    service_name,
                    service_info.get("status", "unknown"),
                    service_info.get("health", "unknown") or "N/A"
                )
        
        # Tests Panel
        test_info = status["tests"]
        test_panel = Panel(
            f"📊 Total Tests: {test_info['total_tests']}\n"
            f"✅ Passed: {test_info['passed']}\n"
            f"❌ Failed: {test_info['failed']}\n"
            f"📈 Coverage: {test_info['coverage'] or 'N/A'}%",
            title="Test Status",
            border_style="green" if test_info['failed'] == 0 else "red"
        )
        
        console.print(health_panel)
        console.print(services_table)
        console.print(test_panel)
    
    def quick_setup(self):
        """Quick development environment setup"""
        console.print("🚀 Elite AI Quick Setup", style="bold cyan")
        
        with Progress(
            SpinnerColumn(),
            TextColumn("[progress.description]{task.description}"),
            console=console,
        ) as progress:
            
            # Step 1: Environment check
            task1 = progress.add_task("Checking environment...", total=None)
            self._check_environment()
            progress.update(task1, completed=True)
            
            # Step 2: Install dependencies
            task2 = progress.add_task("Installing dependencies...", total=None)
            self._install_dependencies()
            progress.update(task2, completed=True)
            
            # Step 3: Setup database
            task3 = progress.add_task("Setting up database...", total=None)
            self._setup_database()
            progress.update(task3, completed=True)
            
            # Step 4: Start services
            task4 = progress.add_task("Starting services...", total=None)
            self._start_services()
            progress.update(task4, completed=True)
            
            # Step 5: Run initial tests
            task5 = progress.add_task("Running initial tests...", total=None)
            self._run_quick_tests()
            progress.update(task5, completed=True)
        
        console.print("✅ Setup complete! Your Elite AI system is ready.", style="bold green")
        self._show_quick_start_info()
    
    def _check_environment(self):
        """Check development environment prerequisites"""
        requirements = {
            "python": {"cmd": ["python", "--version"], "min_version": "3.10"},
            "docker": {"cmd": ["docker", "--version"], "required": True},
            "docker-compose": {"cmd": ["docker-compose", "--version"], "required": True},
            "node": {"cmd": ["node", "--version"], "min_version": "16"},
            "npm": {"cmd": ["npm", "--version"], "required": False}
        }
        
        for tool, config in requirements.items():
            try:
                result = subprocess.run(config["cmd"], capture_output=True, text=True)
                if result.returncode == 0:
                    console.print(f"✅ {tool}: {result.stdout.strip()}", style="green")
                else:
                    if config.get("required", False):
                        console.print(f"❌ {tool}: Not found (required)", style="red")
                        raise Exception(f"{tool} is required but not found")
                    else:
                        console.print(f"⚠️  {tool}: Not found (optional)", style="yellow")
            except Exception as e:
                if config.get("required", False):
                    raise e
    
    def _install_dependencies(self):
        """Install Python and Node.js dependencies"""
        # Python dependencies
        if (self.config.project_root / "requirements.txt").exists():
            subprocess.run(["pip", "install", "-r", "requirements.txt"], 
                         cwd=self.config.project_root, check=True)
        
        # Node.js dependencies (if package.json exists)
        package_json = self.config.project_root / "package.json"
        if package_json.exists():
            subprocess.run(["npm", "install"], cwd=self.config.project_root, check=True)
        
        # Frontend dependencies
        frontend_package = self.config.project_root / "dashboard" / "frontend" / "package.json"
        if frontend_package.exists():
            subprocess.run(["npm", "install"], 
                         cwd=self.config.project_root / "dashboard" / "frontend", 
                         check=True)
    
    def _setup_database(self):
        """Setup database if needed"""
        if self.docker_client:
            # Start database container if not running
            try:
                postgres_container = self.docker_client.containers.get("elite-postgres")
                if postgres_container.status != "running":
                    postgres_container.start()
            except docker.errors.NotFound:
                # Container doesn't exist, will be created by docker-compose
                pass
    
    def _start_services(self):
        """Start all services using docker-compose"""
        compose_file = self.config.project_root / self.config.docker_compose_file
        if compose_file.exists():
            subprocess.run(
                ["docker-compose", "up", "-d"],
                cwd=self.config.project_root,
                check=True
            )
            
            # Wait for services to be ready
            time.sleep(10)
    
    def _run_quick_tests(self):
        """Run a quick test suite"""
        try:
            result = subprocess.run(
                ["python", "-m", "pytest", "tests/", "-x", "--tb=short"],
                cwd=self.config.project_root,
                capture_output=True,
                text=True
            )
            
            if result.returncode == 0:
                console.print("✅ Quick tests passed", style="green")
            else:
                console.print("⚠️  Some tests failed", style="yellow")
        except Exception:
            console.print("⚠️  Could not run tests", style="yellow")
    
    def _show_quick_start_info(self):
        """Show quick start information"""
        info_panel = Panel(
            f"🌐 API: {self.config.api_url}\n"
            f"📊 Dashboard: {self.config.dashboard_url}\n"
            f"🔧 Admin: admin / admin123\n"
            f"📚 Docs: {self.config.api_url}/docs\n\n"
            f"Next steps:\n"
            f"• elite-dev test - Run full test suite\n"
            f"• elite-dev logs - View service logs\n"
            f"• elite-dev monitor - Start monitoring\n"
            f"• elite-dev --help - See all commands",
            title="🎉 Elite AI System Ready!",
            border_style="green"
        )
        console.print(info_panel)
    
    def test(self, pattern: Optional[str] = None, coverage: bool = True, 
             parallel: bool = False, verbose: bool = False):
        """Run comprehensive test suite"""
        console.print("🧪 Running Elite AI Test Suite", style="bold cyan")
        
        cmd = ["python", "-m", "pytest"]
        
        if pattern:
            cmd.extend(["-k", pattern])
        else:
            cmd.append("tests/")
        
        if coverage:
            cmd.extend(["--cov=.", "--cov-report=html", "--cov-report=json"])
        
        if parallel:
            cmd.extend(["-n", "auto"])
        
        if verbose:
            cmd.append("-v")
        else:
            cmd.append("--tb=short")
        
        # Add markers for different test types
        cmd.extend(["--strict-markers"])
        
        try:
            result = subprocess.run(cmd, cwd=self.config.project_root)
            
            if result.returncode == 0:
                console.print("✅ All tests passed!", style="bold green")
                
                if coverage:
                    self._show_coverage_summary()
            else:
                console.print("❌ Some tests failed", style="bold red")
                
        except Exception as e:
            console.print(f"❌ Test execution failed: {e}", style="red")
    
    def _show_coverage_summary(self):
        """Show test coverage summary"""
        coverage_file = self.config.project_root / "coverage.json"
        if coverage_file.exists():
            try:
                with open(coverage_file) as f:
                    coverage_data = json.load(f)
                
                total_coverage = coverage_data.get("totals", {}).get("percent_covered", 0)
                
                coverage_panel = Panel(
                    f"📊 Total Coverage: {total_coverage:.1f}%\n"
                    f"📁 HTML Report: htmlcov/index.html\n"
                    f"📄 JSON Report: coverage.json",
                    title="Test Coverage Summary",
                    border_style="green" if total_coverage >= 80 else "yellow"
                )
                console.print(coverage_panel)
            except Exception:
                console.print("⚠️  Could not read coverage report", style="yellow")
    
    def logs(self, service: Optional[str] = None, follow: bool = False, 
             lines: int = 100):
        """View service logs"""
        if not self.docker_client:
            console.print("❌ Docker not available", style="red")
            return
        
        cmd = ["docker-compose", "logs"]
        
        if follow:
            cmd.append("-f")
        
        cmd.extend(["--tail", str(lines)])
        
        if service:
            cmd.append(service)
        
        try:
            subprocess.run(cmd, cwd=self.config.project_root)
        except KeyboardInterrupt:
            console.print("\n👋 Log viewing stopped", style="cyan")
    
    def monitor(self):
        """Start real-time monitoring dashboard"""
        console.print("📊 Starting Elite AI Monitoring...", style="bold cyan")
        
        while True:
            try:
                # Clear screen
                os.system('cls' if os.name == 'nt' else 'clear')
                
                # Get and display status
                status = self.status()
                
                console.print(f"\n🔄 Last updated: {time.strftime('%H:%M:%S')}")
                console.print("Press Ctrl+C to stop monitoring", style="dim")
                
                time.sleep(5)
                
            except KeyboardInterrupt:
                console.print("\n👋 Monitoring stopped", style="cyan")
                break
    
    def benchmark(self):
        """Run performance benchmarks"""
        console.print("⚡ Running Performance Benchmarks", style="bold cyan")
        
        benchmarks = {
            "API Response Time": self._benchmark_api_response,
            "Database Query Speed": self._benchmark_database,
            "Memory Usage": self._benchmark_memory,
            "Concurrent Requests": self._benchmark_concurrent
        }
        
        results = {}
        
        for name, benchmark_func in benchmarks.items():
            console.print(f"Running {name}...", style="cyan")
            try:
                result = benchmark_func()
                results[name] = result
                console.print(f"✅ {name}: {result}", style="green")
            except Exception as e:
                results[name] = f"Error: {e}"
                console.print(f"❌ {name}: {e}", style="red")
        
        # Save results
        benchmark_file = self.config.project_root / "benchmark_results.json"
        with open(benchmark_file, 'w') as f:
            json.dump({
                "timestamp": time.strftime("%Y-%m-%d %H:%M:%S"),
                "results": results
            }, f, indent=2)
        
        console.print(f"📊 Benchmark results saved to {benchmark_file}", style="cyan")
    
    def _benchmark_api_response(self) -> str:
        """Benchmark API response time"""
        times = []
        for _ in range(10):
            start = time.time()
            response = requests.get(f"{self.config.api_url}/health")
            end = time.time()
            if response.status_code == 200:
                times.append(end - start)
        
        if times:
            avg_time = sum(times) / len(times)
            return f"{avg_time:.3f}s average"
        return "Failed"
    
    def _benchmark_database(self) -> str:
        """Benchmark database query speed"""
        try:
            start = time.time()
            response = requests.get(f"{self.config.api_url}/health/database")
            end = time.time()
            
            if response.status_code == 200:
                return f"{(end - start):.3f}s"
            return "Failed"
        except Exception as e:
            return f"Error: {e}"
    
    def _benchmark_memory(self) -> str:
        """Benchmark memory usage"""
        memory = psutil.virtual_memory()
        return f"{memory.percent:.1f}% used ({memory.used // (1024**3):.1f}GB)"
    
    def _benchmark_concurrent(self) -> str:
        """Benchmark concurrent request handling"""
        import concurrent.futures
        import threading
        
        def make_request():
            try:
                response = requests.get(f"{self.config.api_url}/health", timeout=5)
                return response.status_code == 200
            except:
                return False
        
        with concurrent.futures.ThreadPoolExecutor(max_workers=10) as executor:
            futures = [executor.submit(make_request) for _ in range(50)]
            results = [future.result() for future in concurrent.futures.as_completed(futures)]
        
        success_rate = sum(results) / len(results) * 100
        return f"{success_rate:.1f}% success rate (50 concurrent requests)"
    
    def clean(self):
        """Clean up development environment"""
        console.print("🧹 Cleaning Elite AI Development Environment", style="bold cyan")
        
        cleanup_tasks = [
            ("Docker containers", self._clean_docker),
            ("Python cache", self._clean_python_cache),
            ("Test artifacts", self._clean_test_artifacts),
            ("Log files", self._clean_logs)
        ]
        
        for task_name, task_func in cleanup_tasks:
            console.print(f"Cleaning {task_name}...", style="cyan")
            try:
                task_func()
                console.print(f"✅ {task_name} cleaned", style="green")
            except Exception as e:
                console.print(f"⚠️  {task_name}: {e}", style="yellow")
    
    def _clean_docker(self):
        """Clean Docker containers and images"""
        if self.docker_client:
            # Stop and remove containers
            subprocess.run(["docker-compose", "down"], 
                         cwd=self.config.project_root)
            
            # Clean up unused images
            subprocess.run(["docker", "system", "prune", "-f"])
    
    def _clean_python_cache(self):
        """Clean Python cache files"""
        for root, dirs, files in os.walk(self.config.project_root):
            # Remove __pycache__ directories
            if '__pycache__' in dirs:
                import shutil
                pycache_path = os.path.join(root, '__pycache__')
                shutil.rmtree(pycache_path)
            
            # Remove .pyc files
            for file in files:
                if file.endswith('.pyc'):
                    os.remove(os.path.join(root, file))
    
    def _clean_test_artifacts(self):
        """Clean test artifacts"""
        artifacts = [
            ".coverage",
            "htmlcov",
            ".pytest_cache",
            "test_results.json",
            "benchmark_results.json"
        ]
        
        for artifact in artifacts:
            artifact_path = self.config.project_root / artifact
            if artifact_path.exists():
                if artifact_path.is_dir():
                    import shutil
                    shutil.rmtree(artifact_path)
                else:
                    artifact_path.unlink()
    
    def _clean_logs(self):
        """Clean log files"""
        logs_dir = self.config.project_root / "logs"
        if logs_dir.exists():
            for log_file in logs_dir.glob("*.log"):
                if log_file.stat().st_size > 100 * 1024 * 1024:  # > 100MB
                    log_file.unlink()


def main():
    """Main CLI entry point"""
    parser = argparse.ArgumentParser(
        description="Elite AI System - Developer Experience Toolkit",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  elite-dev status          # Show system status
  elite-dev setup           # Quick setup
  elite-dev test            # Run tests
  elite-dev test --pattern auth  # Run auth tests only
  elite-dev logs            # View all logs
  elite-dev logs elite-api  # View API logs
  elite-dev monitor         # Start monitoring
  elite-dev benchmark       # Run benchmarks
  elite-dev clean           # Clean environment
        """
    )
    
    parser.add_argument("command", 
                       choices=["status", "setup", "test", "logs", "monitor", "benchmark", "clean"],
                       help="Command to run")
    
    parser.add_argument("--pattern", 
                       help="Test pattern to match")
    
    parser.add_argument("--service", 
                       help="Service name for logs")
    
    parser.add_argument("--follow", "-f", 
                       action="store_true",
                       help="Follow log output")
    
    parser.add_argument("--lines", 
                       type=int, default=100,
                       help="Number of log lines to show")
    
    parser.add_argument("--no-coverage", 
                       action="store_true",
                       help="Skip coverage reporting")
    
    parser.add_argument("--parallel", 
                       action="store_true",
                       help="Run tests in parallel")
    
    parser.add_argument("--verbose", "-v", 
                       action="store_true",
                       help="Verbose output")
    
    parser.add_argument("--config", 
                       help="Configuration file path")
    
    args = parser.parse_args()
    
    # Initialize configuration
    project_root = Path.cwd()
    config = EliteDevConfig(project_root=project_root)
    
    # Load custom config if provided
    if args.config:
        config_path = Path(args.config)
        if config_path.exists():
            with open(config_path) as f:
                config_data = yaml.safe_load(f)
                for key, value in config_data.items():
                    if hasattr(config, key):
                        setattr(config, key, value)
    
    # Initialize toolkit
    toolkit = EliteDevToolkit(config)
    
    # Execute command
    try:
        if args.command == "status":
            toolkit.status()
        
        elif args.command == "setup":
            toolkit.quick_setup()
        
        elif args.command == "test":
            toolkit.test(
                pattern=args.pattern,
                coverage=not args.no_coverage,
                parallel=args.parallel,
                verbose=args.verbose
            )
        
        elif args.command == "logs":
            toolkit.logs(
                service=args.service,
                follow=args.follow,
                lines=args.lines
            )
        
        elif args.command == "monitor":
            toolkit.monitor()
        
        elif args.command == "benchmark":
            toolkit.benchmark()
        
        elif args.command == "clean":
            toolkit.clean()
        
    except KeyboardInterrupt:
        console.print("\n👋 Operation cancelled", style="cyan")
        sys.exit(1)
    except Exception as e:
        console.print(f"❌ Error: {e}", style="red")
        sys.exit(1)


if __name__ == "__main__":
    main() 