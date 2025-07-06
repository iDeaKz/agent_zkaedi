#!/bin/bash

# 🚀 ZKAEDI Ultimate Performance Optimization Suite - Quick Start Script
# One-command deployment for maximum performance

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
PURPLE='\033[0;35m'
CYAN='\033[0;36m'
WHITE='\033[1;37m'
NC='\033[0m' # No Color

# ASCII Art Header
echo -e "${PURPLE}"
cat << "EOF"
 ███████╗██╗  ██╗ █████╗ ███████╗██████╗ ██╗    
 ╚══███╔╝██║ ██╔╝██╔══██╗██╔════╝██╔══██╗██║    
   ███╔╝ █████╔╝ ███████║█████╗  ██║  ██║██║    
  ███╔╝  ██╔═██╗ ██╔══██║██╔══╝  ██║  ██║██║    
 ███████╗██║  ██╗██║  ██║███████╗██████╔╝██║    
 ╚══════╝╚═╝  ╚═╝╚═╝  ╚═╝╚══════╝╚═════╝ ╚═╝    
                                                
 ULTIMATE PERFORMANCE OPTIMIZATION SUITE        
EOF
echo -e "${NC}"

echo -e "${WHITE}🎯 Target: 2000+ ops/sec | <1ms latency | Intel Iris Xe GPU + 64GB RAM${NC}"
echo -e "${CYAN}============================================================${NC}"

# Function to print colored output
print_status() {
    echo -e "${GREEN}[INFO]${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}[WARN]${NC} $1"
}

print_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

print_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

print_step() {
    echo -e "${BLUE}[STEP]${NC} $1"
}

# Function to check if command exists
command_exists() {
    command -v "$1" >/dev/null 2>&1
}

# Function to check Python version
check_python() {
    if command_exists python3; then
        PYTHON_CMD="python3"
    elif command_exists python; then
        PYTHON_CMD="python"
    else
        print_error "Python is not installed. Please install Python 3.8+ first."
        exit 1
    fi
    
    PYTHON_VERSION=$($PYTHON_CMD --version 2>&1 | cut -d' ' -f2)
    print_status "Found Python $PYTHON_VERSION"
    
    # Check if version is 3.8 or higher
    if ! $PYTHON_CMD -c "import sys; exit(0 if sys.version_info >= (3, 8) else 1)"; then
        print_error "Python 3.8+ is required. Found: $PYTHON_VERSION"
        exit 1
    fi
}

# Function to detect system information
detect_system() {
    print_step "Detecting system configuration..."
    
    OS=$(uname -s)
    ARCH=$(uname -m)
    CPU_CORES=$(nproc 2>/dev/null || sysctl -n hw.ncpu 2>/dev/null || echo "4")
    
    if [[ "$OS" == "Linux" ]]; then
        MEMORY_GB=$(free -g | awk '/^Mem:/{print $2}')
        if command_exists lscpu; then
            CPU_INFO=$(lscpu | grep "Model name" | cut -d':' -f2 | xargs)
        else
            CPU_INFO="Unknown CPU"
        fi
    elif [[ "$OS" == "Darwin" ]]; then
        MEMORY_GB=$(( $(sysctl -n hw.memsize) / 1024 / 1024 / 1024 ))
        CPU_INFO=$(sysctl -n machdep.cpu.brand_string)
    else
        MEMORY_GB="Unknown"
        CPU_INFO="Unknown CPU"
    fi
    
    print_status "System: $OS $ARCH"
    print_status "CPU: $CPU_INFO ($CPU_CORES cores)"
    print_status "Memory: ${MEMORY_GB}GB"
    
    # Detect GPU
    if [[ "$OS" == "Linux" ]]; then
        if lspci 2>/dev/null | grep -i "intel.*graphics" >/dev/null; then
            print_status "🎮 Intel GPU detected"
            INTEL_GPU=true
        else
            print_warning "Intel GPU not detected"
            INTEL_GPU=false
        fi
    else
        print_warning "GPU detection not supported on this platform"
        INTEL_GPU=false
    fi
}

# Function to set environment variables for optimal performance
setup_environment() {
    print_step "Setting up performance environment variables..."
    
    export OMP_NUM_THREADS=$CPU_CORES
    export MKL_NUM_THREADS=$CPU_CORES
    export NUMBA_NUM_THREADS=$CPU_CORES
    export JIT=1
    export PYTHONPATH="${PWD}:${PYTHONPATH}"
    
    print_status "Environment configured for $CPU_CORES cores"
    
    # Create temporary environment file
    cat > .env_performance << EOF
# ZKAEDI Performance Environment
export OMP_NUM_THREADS=$CPU_CORES
export MKL_NUM_THREADS=$CPU_CORES
export NUMBA_NUM_THREADS=$CPU_CORES
export JIT=1
export PYTHONPATH="${PWD}:\${PYTHONPATH}"
EOF
    
    print_status "Performance environment saved to .env_performance"
}

# Function to install dependencies
install_dependencies() {
    print_step "Installing dependencies with Ultimate Dependency Installer..."
    
    if [ ! -f "install_ultimate_dependencies.py" ]; then
        print_error "install_ultimate_dependencies.py not found!"
        exit 1
    fi
    
    print_status "Running dependency installer..."
    $PYTHON_CMD install_ultimate_dependencies.py
    
    if [ $? -eq 0 ]; then
        print_success "Dependencies installed successfully!"
    else
        print_error "Dependency installation failed!"
        exit 1
    fi
}

# Function to run performance benchmark
run_benchmark() {
    print_step "Running performance benchmark suite..."
    
    if [ ! -f "zkaedi_ultimate_optimizer.py" ]; then
        print_error "zkaedi_ultimate_optimizer.py not found!"
        exit 1
    fi
    
    print_status "Starting benchmark with 1000 iterations..."
    
    # Run benchmark and capture output
    BENCHMARK_OUTPUT=$($PYTHON_CMD -c "
import asyncio
import json
from zkaedi_ultimate_optimizer import get_optimizer

async def run_benchmark():
    optimizer = get_optimizer()
    try:
        results = await optimizer.run_benchmark_suite(1000)
        print(json.dumps(results['benchmark_summary'], indent=2))
        return results
    finally:
        optimizer.cleanup()

if __name__ == '__main__':
    asyncio.run(run_benchmark())
" 2>&1)
    
    if [ $? -eq 0 ]; then
        print_success "Benchmark completed successfully!"
        echo -e "${CYAN}Benchmark Results:${NC}"
        echo "$BENCHMARK_OUTPUT"
        
        # Extract key metrics
        THROUGHPUT=$(echo "$BENCHMARK_OUTPUT" | grep -o '"throughput_ops_per_sec": [0-9.]*' | cut -d':' -f2 | xargs)
        LATENCY=$(echo "$BENCHMARK_OUTPUT" | grep -o '"average_latency_ms": [0-9.]*' | cut -d':' -f2 | xargs)
        
        if [ ! -z "$THROUGHPUT" ] && [ ! -z "$LATENCY" ]; then
            echo -e "${WHITE}Key Performance Metrics:${NC}"
            echo -e "  🚀 Throughput: ${GREEN}${THROUGHPUT}${NC} ops/sec"
            echo -e "  ⚡ Latency: ${GREEN}${LATENCY}${NC} ms"
            
            # Check if targets are met
            if (( $(echo "$THROUGHPUT > 100" | bc -l) )); then
                print_success "🏆 Speed Demon badge earned! (100+ ops/sec)"
            fi
            
            if (( $(echo "$LATENCY < 1.0" | bc -l) )); then
                print_success "🏆 Latency Destroyer badge earned! (<1ms latency)"
            fi
            
            if (( $(echo "$THROUGHPUT > 500" | bc -l) )); then
                print_success "🏆 Performance Master badge earned! (500+ ops/sec)"
            fi
            
            if (( $(echo "$THROUGHPUT > 1000" | bc -l) )); then
                print_success "🏆 Ultimate Completionist badge earned! (1000+ ops/sec)"
            fi
        fi
    else
        print_error "Benchmark failed!"
        echo "$BENCHMARK_OUTPUT"
        exit 1
    fi
}

# Function to launch dashboard
launch_dashboard() {
    print_step "Launching performance dashboard..."
    
    if [ ! -f "zkaedi_performance_dashboard.html" ]; then
        print_error "zkaedi_performance_dashboard.html not found!"
        exit 1
    fi
    
    # Try to open dashboard in browser
    DASHBOARD_PATH="$(pwd)/zkaedi_performance_dashboard.html"
    
    if command_exists xdg-open; then
        xdg-open "file://$DASHBOARD_PATH" >/dev/null 2>&1 &
        print_success "Dashboard opened in default browser"
    elif command_exists open; then
        open "file://$DASHBOARD_PATH" >/dev/null 2>&1 &
        print_success "Dashboard opened in default browser"
    elif command_exists python3 && python3 -c "import webbrowser" 2>/dev/null; then
        python3 -c "import webbrowser; webbrowser.open('file://$DASHBOARD_PATH')" >/dev/null 2>&1 &
        print_success "Dashboard opened in default browser"
    else
        print_warning "Could not auto-open dashboard. Please open manually:"
        echo -e "  ${CYAN}file://$DASHBOARD_PATH${NC}"
    fi
    
    # Start simple HTTP server for real-time updates (optional)
    if command_exists $PYTHON_CMD; then
        print_status "Starting HTTP server on port 8000..."
        $PYTHON_CMD -m http.server 8000 >/dev/null 2>&1 &
        HTTP_PID=$!
        echo "$HTTP_PID" > .dashboard_server.pid
        print_status "Dashboard also available at: http://localhost:8000/zkaedi_performance_dashboard.html"
    fi
}

# Function to generate system report
generate_report() {
    print_step "Generating system optimization report..."
    
    REPORT_FILE="zkaedi_optimization_report.txt"
    
    cat > "$REPORT_FILE" << EOF
🚀 ZKAEDI Ultimate Performance Optimization Report
Generated: $(date)

=== SYSTEM CONFIGURATION ===
OS: $OS $ARCH
CPU: $CPU_INFO
Cores: $CPU_CORES
Memory: ${MEMORY_GB}GB
Intel GPU: $([ "$INTEL_GPU" = true ] && echo "Detected" || echo "Not detected")

=== OPTIMIZATION SETTINGS ===
OMP_NUM_THREADS: $CPU_CORES
MKL_NUM_THREADS: $CPU_CORES
NUMBA_NUM_THREADS: $CPU_CORES
JIT: Enabled

=== PERFORMANCE TARGETS ===
Target Throughput: 2000+ ops/sec
Target Latency: <1ms
Target Hardware: Intel Iris Xe GPU + 64GB RAM + 8TB NVMe SSD

=== INSTALLATION STATUS ===
Dependencies: $([ -f "zkaedi_installation_report.json" ] && echo "✅ Installed" || echo "❌ Failed")
Core Optimizer: $([ -f "zkaedi_ultimate_optimizer.py" ] && echo "✅ Ready" || echo "❌ Missing")
Dashboard: $([ -f "zkaedi_performance_dashboard.html" ] && echo "✅ Ready" || echo "❌ Missing")

=== NEXT STEPS ===
1. Monitor performance using the dashboard
2. Run additional benchmarks to validate performance
3. Optimize system settings based on workload
4. Consider hardware upgrades if targets not met

=== USAGE COMMANDS ===
# Load performance environment
source .env_performance

# Run optimizer directly
python zkaedi_ultimate_optimizer.py

# Install additional dependencies
python install_ultimate_dependencies.py

# Open dashboard
Open: file://$(pwd)/zkaedi_performance_dashboard.html
EOF
    
    print_success "System report generated: $REPORT_FILE"
}

# Function to cleanup resources
cleanup() {
    print_step "Cleaning up temporary resources..."
    
    # Kill dashboard server if running
    if [ -f ".dashboard_server.pid" ]; then
        PID=$(cat .dashboard_server.pid)
        if kill -0 "$PID" 2>/dev/null; then
            kill "$PID" 2>/dev/null
            print_status "Stopped dashboard server"
        fi
        rm -f .dashboard_server.pid
    fi
}

# Function to show help
show_help() {
    echo -e "${WHITE}ZKAEDI Ultimate Performance Optimization Suite - Quick Start${NC}"
    echo ""
    echo -e "${CYAN}Usage:${NC}"
    echo "  $0 [options]"
    echo ""
    echo -e "${CYAN}Options:${NC}"
    echo "  -h, --help     Show this help message"
    echo "  -s, --skip-deps Skip dependency installation"
    echo "  -b, --benchmark-only Run benchmark only"
    echo "  -d, --dashboard-only Launch dashboard only"
    echo "  -q, --quiet    Quiet mode (less verbose output)"
    echo ""
    echo -e "${CYAN}Examples:${NC}"
    echo "  $0                    # Full installation and setup"
    echo "  $0 --skip-deps       # Skip dependency installation"
    echo "  $0 --benchmark-only  # Run benchmark only"
    echo "  $0 --dashboard-only  # Launch dashboard only"
}

# Parse command line arguments
SKIP_DEPS=false
BENCHMARK_ONLY=false
DASHBOARD_ONLY=false
QUIET=false

while [[ $# -gt 0 ]]; do
    case $1 in
        -h|--help)
            show_help
            exit 0
            ;;
        -s|--skip-deps)
            SKIP_DEPS=true
            shift
            ;;
        -b|--benchmark-only)
            BENCHMARK_ONLY=true
            shift
            ;;
        -d|--dashboard-only)
            DASHBOARD_ONLY=true
            shift
            ;;
        -q|--quiet)
            QUIET=true
            shift
            ;;
        *)
            print_error "Unknown option: $1"
            show_help
            exit 1
            ;;
    esac
done

# Trap for cleanup
trap cleanup EXIT

# Main execution
main() {
    echo -e "${WHITE}🚀 ZKAEDI Ultimate Performance Optimization Suite${NC}"
    echo -e "${WHITE}Starting quick deployment...${NC}"
    echo ""
    
    # Basic checks
    check_python
    detect_system
    setup_environment
    
    if [ "$DASHBOARD_ONLY" = true ]; then
        launch_dashboard
        print_success "Dashboard launched successfully!"
        return
    fi
    
    if [ "$BENCHMARK_ONLY" = true ]; then
        run_benchmark
        return
    fi
    
    # Full installation
    if [ "$SKIP_DEPS" = false ]; then
        install_dependencies
    else
        print_warning "Skipping dependency installation"
    fi
    
    # Run benchmark
    run_benchmark
    
    # Launch dashboard
    launch_dashboard
    
    # Generate report
    generate_report
    
    echo ""
    echo -e "${GREEN}🎉 ZKAEDI Ultimate Performance Optimization Suite deployed successfully!${NC}"
    echo ""
    echo -e "${WHITE}Performance Dashboard:${NC} file://$(pwd)/zkaedi_performance_dashboard.html"
    echo -e "${WHITE}HTTP Server:${NC} http://localhost:8000/zkaedi_performance_dashboard.html"
    echo -e "${WHITE}System Report:${NC} $(pwd)/zkaedi_optimization_report.txt"
    echo ""
    echo -e "${CYAN}🎯 Next Steps:${NC}"
    echo -e "  1. Monitor real-time performance in the dashboard"
    echo -e "  2. Run additional benchmarks to validate optimization"
    echo -e "  3. Adjust system settings based on workload requirements"
    echo -e "  4. Achieve ultimate performance targets: 2000+ ops/sec, <1ms latency"
    echo ""
    echo -e "${YELLOW}💡 Pro Tips:${NC}"
    echo -e "  • Use 'source .env_performance' to load optimization environment"
    echo -e "  • Monitor CPU/GPU temperatures during intensive workloads"
    echo -e "  • Consider Intel OneAPI toolkit for maximum GPU acceleration"
    echo -e "  • Use SSD caching for improved I/O performance"
    echo ""
    print_success "Ultimate Completionist status: Ready to achieve! 🏆👑"
}

# Check if script is being sourced or executed
if [[ "${BASH_SOURCE[0]}" == "${0}" ]]; then
    main "$@"
fi