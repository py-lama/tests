#!/bin/bash
set -euo pipefail

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Default values
TEST_TYPE="all"
DOCKER_MODE=false
VERBOSE=false
KEEP_CONTAINERS=false

# Function to display help
show_help() {
    echo "Run DialogChain tests"
    echo ""
    echo "Usage: $0 [options]"
    echo ""
    echo "Options:"
    echo "  -t, --type TYPE       Test type: all, unit, integration, mqtt, http (default: all)"
    echo "  -d, --docker          Run tests in Docker container"
    echo "  -v, --verbose         Show more verbose output"
    echo "  -k, --keep-containers Keep test containers running after tests"
    echo "  -h, --help            Show this help message and exit"
    echo ""
    echo "Examples:"
    echo "  $0 -t mqtt             # Run only MQTT tests"
    echo "  $0 -d -t integration   # Run integration tests in Docker"
    echo "  $0 -v -t http          # Run HTTP tests with verbose output"
}

# Parse command line arguments
while [[ $# -gt 0 ]]; do
    case $1 in
        -t|--type)
            TEST_TYPE="$2"
            shift 2
            ;;
        -d|--docker)
            DOCKER_MODE=true
            shift
            ;;
        -v|--verbose)
            VERBOSE=true
            shift
            ;;
        -k|--keep-containers)
            KEEP_CONTAINERS=true
            shift
            ;;
        -h|--help)
            show_help
            exit 0
            ;;
        *)
            echo "Unknown option: $1"
            show_help
            exit 1
            ;;
    esac
done

# Function to log messages
log() {
    echo -e "${GREEN}[TEST]${NC} $(date '+%Y-%m-%d %H:%M:%S') - $1"
}

# Function to log info messages
info() {
    echo -e "${BLUE}[INFO]${NC} $(date '+%Y-%m-%d %H:%M:%S') - $1"
}

# Function to run tests locally
run_local_tests() {
    # Get the absolute path to the tests directory
    local test_dir="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
    local project_root="$(dirname "$test_dir")"
    
    # Set PYTHONPATH to include the project root
    export PYTHONPATH="${PYTHONPATH:+$PYTHONPATH:}$project_root"
    
    # Change to project root directory
    cd "$project_root" || { echo "Failed to change to project root directory"; exit 1; }
    
    local test_cmd="pytest -v"
    
    if [ "$VERBOSE" = true ]; then
        test_cmd="$test_cmd -s"
    fi
    
    case $TEST_TYPE in
        unit)
            log "Running unit tests..."
            $test_cmd tests/unit/
            ;;
        integration)
            log "Running integration tests..."
            $test_cmd tests/integration/
            ;;
        mqtt)
            log "Running MQTT tests..."
            $test_cmd tests/integration/mqtt/ --log-cli-level=INFO
            ;;
        http)
            log "Running HTTP tests..."
            $test_cmd tests/integration/test_http_connector.py -v
            ;;
        all)
            log "Running all tests..."
            $test_cmd
            ;;
        *)
            echo "Unknown test type: $TEST_TYPE"
            show_help
            exit 1
            ;;
    esac
}

# Function to run tests in Docker
run_docker_tests() {
    local docker_args=("--rm")
    local test_cmd="-t $TEST_TYPE"
    
    if [ "$VERBOSE" = true ]; then
        test_cmd="$test_cmd -v"
    fi
    
    if [ "$KEEP_CONTAINERS" = true ]; then
        docker_args=("--name" "dialogchain-tests")
    fi
    
    # Build the Docker image from the project root
    log "Building test Docker image..."
    cd .. && docker build -t dialogchain-tests -f tests/Dockerfile.test .
    
    log "Running tests in Docker container..."
    docker run "${docker_args[@]}" dialogchain-tests $test_cmd
    
    if [ "$KEEP_CONTAINERS" = true ]; then
        info "Test container kept running with name: dialogchain-tests"
        info "To stop and remove: docker rm -f dialogchain-tests"
        info "To attach: docker exec -it dialogchain-tests /bin/bash"
    fi
}

# Main execution
log "Starting DialogChain test runner"
info "Test type: $TEST_TYPE"
info "Docker mode: $DOCKER_MODE"
info "Verbose: $VERBOSE"

# Install test dependencies if not in Docker
if [ "$DOCKER_MODE" = false ]; then
    log "Installing test dependencies..."
    pip install -e .[test] > /dev/null || {
        echo -e "${RED}Failed to install test dependencies${NC}"
        exit 1
    }
fi

# Run tests
if [ "$DOCKER_MODE" = true ]; then
    run_docker_tests
else
    run_local_tests
fi

log "Tests completed successfully"
exit 0
