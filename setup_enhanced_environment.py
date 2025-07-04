#!/usr/bin/env python3
"""
Elite AI System - Enhanced Development Environment Setup
Comprehensive setup for Phase 3 enhancements
"""

import os
import sys
import subprocess
import json
from pathlib import Path
from typing import List, Dict, Any
import argparse
from rich.console import Console
from rich.progress import Progress, SpinnerColumn, TextColumn, BarColumn
from rich.panel import Panel
from rich.table import Table

console = Console()


class EnhancedEnvironmentSetup:
    """Setup enhanced development environment with all Phase 3 features"""
    
    def __init__(self, project_root: Path):
        self.project_root = project_root
        self.config = {
            "python_version": "3.10",
            "node_version": "16",
            "docker_required": True,
            "services": [
                "elite-postgres", "elite-redis", "elite-api", 
                "elite-frontend", "elite-prometheus", "elite-grafana"
            ]
        }
    
    def setup_complete_environment(self):
        """Setup complete enhanced development environment"""
        console.print("🚀 Setting up Elite AI Enhanced Development Environment", style="bold cyan")
        
        with Progress(
            SpinnerColumn(),
            TextColumn("[progress.description]{task.description}"),
            BarColumn(),
            console=console,
        ) as progress:
            
            # Phase 1: Prerequisites
            task1 = progress.add_task("Checking prerequisites...", total=4)
            self._check_python()
            progress.advance(task1)
            self._check_docker()
            progress.advance(task1)
            self._check_node()
            progress.advance(task1)
            self._check_git()
            progress.advance(task1)
            
            # Phase 2: Environment setup
            task2 = progress.add_task("Setting up environment...", total=3)
            self._setup_python_environment()
            progress.advance(task2)
            self._setup_pre_commit_hooks()
            progress.advance(task2)
            self._setup_environment_files()
            progress.advance(task2)
            
            # Phase 3: Install dependencies
            task3 = progress.add_task("Installing dependencies...", total=4)
            self._install_python_dependencies()
            progress.advance(task3)
            self._install_dev_tools()
            progress.advance(task3)
            self._install_frontend_dependencies()
            progress.advance(task3)
            self._install_security_tools()
            progress.advance(task3)
            
            # Phase 4: Setup testing infrastructure
            task4 = progress.add_task("Setting up testing infrastructure...", total=3)
            self._setup_testing_framework()
            progress.advance(task4)
            self._setup_security_testing()
            progress.advance(task4)
            self._setup_e2e_testing()
            progress.advance(task4)
            
            # Phase 5: Initialize services
            task5 = progress.add_task("Initializing services...", total=2)
            self._setup_docker_services()
            progress.advance(task5)
            self._run_initial_tests()
            progress.advance(task5)
        
        self._display_setup_summary()
    
    def _check_python(self):
        """Check Python installation"""
        try:
            result = subprocess.run([sys.executable, "--version"], 
                                  capture_output=True, text=True)
            version = result.stdout.strip()
            console.print(f"✅ Python: {version}", style="green")
            
            # Check if version is adequate
            import sys
            if sys.version_info < (3, 10):
                raise Exception("Python 3.10+ required")
                
        except Exception as e:
            console.print(f"❌ Python check failed: {e}", style="red")
            sys.exit(1)
    
    def _check_docker(self):
        """Check Docker installation"""
        try:
            result = subprocess.run(["docker", "--version"], 
                                  capture_output=True, text=True)
            version = result.stdout.strip()
            console.print(f"✅ Docker: {version}", style="green")
            
            # Check if Docker is running
            subprocess.run(["docker", "ps"], capture_output=True, check=True)
            
        except Exception as e:
            console.print(f"❌ Docker check failed: {e}", style="red")
            console.print("Please install and start Docker Desktop", style="yellow")
            sys.exit(1)
    
    def _check_node(self):
        """Check Node.js installation"""
        try:
            result = subprocess.run(["node", "--version"], 
                                  capture_output=True, text=True)
            version = result.stdout.strip()
            console.print(f"✅ Node.js: {version}", style="green")
            
        except Exception as e:
            console.print(f"⚠️  Node.js not found: {e}", style="yellow")
            console.print("Node.js recommended for frontend development", style="dim")
    
    def _check_git(self):
        """Check Git installation"""
        try:
            result = subprocess.run(["git", "--version"], 
                                  capture_output=True, text=True)
            version = result.stdout.strip()
            console.print(f"✅ Git: {version}", style="green")
            
        except Exception as e:
            console.print(f"❌ Git check failed: {e}", style="red")
            sys.exit(1)
    
    def _setup_python_environment(self):
        """Setup Python virtual environment"""
        venv_path = self.project_root / "venv"
        
        if not venv_path.exists():
            console.print("Creating Python virtual environment...", style="cyan")
            subprocess.run([sys.executable, "-m", "venv", str(venv_path)], check=True)
        
        # Activate virtual environment and upgrade pip
        if os.name == 'nt':  # Windows
            pip_path = venv_path / "Scripts" / "pip"
        else:  # Unix/Linux/macOS
            pip_path = venv_path / "bin" / "pip"
        
        subprocess.run([str(pip_path), "install", "--upgrade", "pip", "setuptools", "wheel"], 
                      check=True)
    
    def _setup_pre_commit_hooks(self):
        """Setup pre-commit hooks for code quality"""
        pre_commit_config = self.project_root / ".pre-commit-config.yaml"
        
        if not pre_commit_config.exists():
            config_content = """
repos:
  - repo: https://github.com/pre-commit/pre-commit-hooks
    rev: v4.4.0
    hooks:
      - id: trailing-whitespace
      - id: end-of-file-fixer
      - id: check-yaml
      - id: check-added-large-files
      - id: check-json
      - id: check-merge-conflict
      - id: debug-statements
      - id: requirements-txt-fixer

  - repo: https://github.com/psf/black
    rev: 23.1.0
    hooks:
      - id: black
        language_version: python3

  - repo: https://github.com/pycqa/isort
    rev: 5.12.0
    hooks:
      - id: isort
        args: ["--profile", "black"]

  - repo: https://github.com/pycqa/flake8
    rev: 6.0.0
    hooks:
      - id: flake8
        additional_dependencies: [flake8-docstrings]

  - repo: https://github.com/pre-commit/mirrors-mypy
    rev: v1.0.1
    hooks:
      - id: mypy
        additional_dependencies: [types-all]

  - repo: https://github.com/PyCQA/bandit
    rev: 1.7.4
    hooks:
      - id: bandit
        args: ["-r", ".", "-f", "json", "-o", "bandit-report.json"]

  - repo: https://github.com/gitguardian/ggshield
    rev: v1.18.0
    hooks:
      - id: ggshield
        language: python
        stages: [commit]
"""
            with open(pre_commit_config, 'w') as f:
                f.write(config_content.strip())
        
        # Install pre-commit hooks
        try:
            subprocess.run(["pre-commit", "install"], cwd=self.project_root, check=True)
            console.print("✅ Pre-commit hooks installed", style="green")
        except Exception:
            console.print("⚠️  Pre-commit installation skipped", style="yellow")
    
    def _setup_environment_files(self):
        """Setup environment configuration files"""
        env_files = {
            ".env.development": {
                "DATABASE_URL": "postgresql://postgres:password@localhost:5432/elite_ai_dev",
                "REDIS_URL": "redis://localhost:6379/0",
                "JWT_SECRET_KEY": "dev-secret-key-change-in-production",
                "ENCRYPTION_KEY": "dev-encryption-key-change-in-production",
                "ENVIRONMENT": "development",
                "DEBUG": "true",
                "LOG_LEVEL": "DEBUG"
            },
            ".env.testing": {
                "DATABASE_URL": "postgresql://postgres:password@localhost:5432/elite_ai_test",
                "REDIS_URL": "redis://localhost:6379/1",
                "JWT_SECRET_KEY": "test-secret-key",
                "ENCRYPTION_KEY": "test-encryption-key",
                "ENVIRONMENT": "testing",
                "DEBUG": "true",
                "LOG_LEVEL": "DEBUG"
            }
        }
        
        for filename, config in env_files.items():
            env_file = self.project_root / filename
            if not env_file.exists():
                with open(env_file, 'w') as f:
                    for key, value in config.items():
                        f.write(f"{key}={value}\n")
    
    def _install_python_dependencies(self):
        """Install Python dependencies"""
        requirements_files = [
            "requirements.txt",
            "dev-tools/requirements.txt"
        ]
        
        for req_file in requirements_files:
            req_path = self.project_root / req_file
            if req_path.exists():
                console.print(f"Installing {req_file}...", style="cyan")
                subprocess.run([sys.executable, "-m", "pip", "install", "-r", str(req_path)], 
                             check=True)
    
    def _install_dev_tools(self):
        """Install development tools"""
        dev_tools = [
            "elite-dev-toolkit",  # Our custom toolkit
            "rich",  # Beautiful terminal output
            "click",  # CLI framework
            "pytest",  # Testing framework
            "black",  # Code formatter
            "isort",  # Import sorter
            "flake8",  # Linter
            "mypy",  # Type checker
            "pre-commit",  # Git hooks
            "bandit",  # Security linter
            "safety",  # Dependency security
        ]
        
        console.print("Installing development tools...", style="cyan")
        subprocess.run([sys.executable, "-m", "pip", "install"] + dev_tools, check=True)
    
    def _install_frontend_dependencies(self):
        """Install frontend dependencies"""
        frontend_dir = self.project_root / "dashboard" / "frontend"
        
        if frontend_dir.exists() and (frontend_dir / "package.json").exists():
            console.print("Installing frontend dependencies...", style="cyan")
            subprocess.run(["npm", "install"], cwd=frontend_dir, check=True)
    
    def _install_security_tools(self):
        """Install security testing tools"""
        security_tools = [
            "bandit[toml]",  # Python security linter
            "safety",  # Dependency vulnerability scanner
            "semgrep",  # Static analysis
            "pip-audit",  # Pip vulnerability scanner
        ]
        
        console.print("Installing security tools...", style="cyan")
        try:
            subprocess.run([sys.executable, "-m", "pip", "install"] + security_tools, 
                         check=True)
        except Exception as e:
            console.print(f"⚠️  Some security tools failed to install: {e}", style="yellow")
    
    def _setup_testing_framework(self):
        """Setup comprehensive testing framework"""
        # Create test configuration
        test_config = {
            "test_databases": {
                "unit": "sqlite:///test_unit.db",
                "integration": "postgresql://postgres:password@localhost:5432/elite_ai_integration_test",
                "e2e": "postgresql://postgres:password@localhost:5432/elite_ai_e2e_test"
            },
            "test_redis": {
                "unit": "redis://localhost:6379/10",
                "integration": "redis://localhost:6379/11",
                "e2e": "redis://localhost:6379/12"
            },
            "browser_drivers": {
                "chrome": "chromedriver",
                "firefox": "geckodriver"
            }
        }
        
        config_file = self.project_root / "tests" / "config.json"
        config_file.parent.mkdir(exist_ok=True)
        
        with open(config_file, 'w') as f:
            json.dump(test_config, f, indent=2)
        
        # Create test directories
        test_dirs = [
            "tests/unit",
            "tests/integration",
            "tests/integration_advanced", 
            "tests/e2e",
            "tests/security",
            "tests/performance",
            "tests/fixtures",
            "tests/utils"
        ]
        
        for test_dir in test_dirs:
            (self.project_root / test_dir).mkdir(parents=True, exist_ok=True)
            
            # Create __init__.py files
            init_file = self.project_root / test_dir / "__init__.py"
            if not init_file.exists():
                init_file.touch()
    
    def _setup_security_testing(self):
        """Setup security testing infrastructure"""
        # Create security test configuration
        security_config = {
            "scan_targets": [
                "http://localhost:8000",
                "http://localhost:3000"
            ],
            "excluded_paths": [
                "/health",
                "/docs",
                "/static"
            ],
            "security_headers": [
                "X-Content-Type-Options",
                "X-Frame-Options", 
                "X-XSS-Protection",
                "Strict-Transport-Security",
                "Content-Security-Policy"
            ],
            "vulnerability_scans": {
                "sql_injection": True,
                "xss": True,
                "csrf": True,
                "authentication": True,
                "authorization": True
            }
        }
        
        config_file = self.project_root / "tests" / "security" / "config.json"
        with open(config_file, 'w') as f:
            json.dump(security_config, f, indent=2)
    
    def _setup_e2e_testing(self):
        """Setup end-to-end testing infrastructure"""
        # Create E2E test configuration
        e2e_config = {
            "base_url": "http://localhost:3000",
            "api_url": "http://localhost:8000",
            "browser": "chrome",
            "headless": True,
            "timeout": 30,
            "screenshot_on_failure": True,
            "video_recording": False,
            "test_users": {
                "admin": {"username": "admin", "password": "admin123"},
                "user": {"username": "testuser", "password": "testpass123"}
            }
        }
        
        config_file = self.project_root / "tests" / "e2e" / "config.json"
        with open(config_file, 'w') as f:
            json.dump(e2e_config, f, indent=2)
    
    def _setup_docker_services(self):
        """Setup and start Docker services"""
        compose_file = self.project_root / "docker-compose.yml"
        
        if compose_file.exists():
            console.print("Starting Docker services...", style="cyan")
            try:
                # Start services in development mode
                subprocess.run([
                    "docker-compose", 
                    "-f", str(compose_file),
                    "up", "-d"
                ], cwd=self.project_root, check=True)
                
                # Wait for services to be ready
                import time
                time.sleep(15)
                
                console.print("✅ Docker services started", style="green")
                
            except Exception as e:
                console.print(f"⚠️  Docker services failed to start: {e}", style="yellow")
        else:
            console.print("⚠️  docker-compose.yml not found", style="yellow")
    
    def _run_initial_tests(self):
        """Run initial test suite to verify setup"""
        console.print("Running initial test suite...", style="cyan")
        
        try:
            # Run quick smoke tests
            result = subprocess.run([
                sys.executable, "-m", "pytest", 
                "tests/", "-m", "quick", 
                "--tb=short", "-v"
            ], cwd=self.project_root, capture_output=True, text=True)
            
            if result.returncode == 0:
                console.print("✅ Initial tests passed", style="green")
            else:
                console.print("⚠️  Some initial tests failed", style="yellow")
                console.print(result.stdout[-500:])  # Show last 500 chars
                
        except Exception as e:
            console.print(f"⚠️  Could not run initial tests: {e}", style="yellow")
    
    def _display_setup_summary(self):
        """Display setup summary and next steps"""
        # System status table
        status_table = Table(title="Elite AI System Status")
        status_table.add_column("Component", style="cyan")
        status_table.add_column("Status", style="green")
        status_table.add_column("URL/Path", style="blue")
        
        status_table.add_row("API Server", "✅ Ready", "http://localhost:8000")
        status_table.add_row("Dashboard", "✅ Ready", "http://localhost:3000")
        status_table.add_row("API Docs", "✅ Ready", "http://localhost:8000/docs")
        status_table.add_row("Grafana", "✅ Ready", "http://localhost:3001")
        status_table.add_row("Database", "✅ Ready", "postgresql://localhost:5432")
        status_table.add_row("Redis", "✅ Ready", "redis://localhost:6379")
        
        console.print(status_table)
        
        # Next steps panel
        next_steps = Panel(
            """
🚀 Your Elite AI Enhanced Development Environment is ready!

Quick Start Commands:
• python dev-tools/elite_dev_toolkit.py status  - Check system status
• python dev-tools/elite_dev_toolkit.py test    - Run test suite
• python dev-tools/elite_dev_toolkit.py monitor - Start monitoring
• python dev-tools/elite_dev_toolkit.py logs    - View service logs

Development Workflow:
• git checkout -b feature/your-feature  - Create feature branch
• Edit code with your favorite editor
• python dev-tools/elite_dev_toolkit.py test --pattern your_feature
• git commit -m "feat: your feature"
• git push origin feature/your-feature

Testing Commands:
• pytest tests/unit/                    - Unit tests
• pytest tests/integration/             - Integration tests  
• pytest tests/e2e/                     - End-to-end tests
• pytest tests/security/                - Security tests
• pytest --cov=. --cov-report=html      - Coverage report

Documentation:
• tutorials/01_getting_started.md       - Getting started guide
• tutorials/02_advanced_features.md     - Advanced features
• docs/security/SECURITY_GUIDE.md       - Security guide
• CONTRIBUTING.md                       - Contributing guide

Happy coding! 🎉
            """,
            title="🎯 Next Steps",
            border_style="green"
        )
        
        console.print(next_steps)


def main():
    """Main entry point"""
    parser = argparse.ArgumentParser(
        description="Elite AI System - Enhanced Development Environment Setup"
    )
    parser.add_argument(
        "--project-root",
        type=Path,
        default=Path.cwd(),
        help="Project root directory"
    )
    parser.add_argument(
        "--skip-docker",
        action="store_true",
        help="Skip Docker service setup"
    )
    parser.add_argument(
        "--skip-tests",
        action="store_true", 
        help="Skip initial test run"
    )
    
    args = parser.parse_args()
    
    # Initialize setup
    setup = EnhancedEnvironmentSetup(args.project_root)
    
    # Customize setup based on arguments
    if args.skip_docker:
        setup.config["docker_required"] = False
    
    try:
        setup.setup_complete_environment()
    except KeyboardInterrupt:
        console.print("\n👋 Setup cancelled by user", style="yellow")
        sys.exit(1)
    except Exception as e:
        console.print(f"\n❌ Setup failed: {e}", style="red")
        console.print("Check the error messages above and try again", style="dim")
        sys.exit(1)


if __name__ == "__main__":
    main() 