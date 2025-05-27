#!/bin/bash
set -euo pipefail

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Configuration
REPO_URL="${REPO_URL:-https://github.com/dialogchain/python.git}"
BRANCH="${BRANCH:-main}"
MAKE_TARGETS=(${MAKE_TARGETS:-help deps test})
PYTHON_DEPS=(${PYTHON_DEPS:-})
SYSTEM_DEPS=(${SYSTEM_DEPS:-})
TEST_TIMEOUT=${TEST_TIMEOUT:-300}

# Set up SSH configuration to avoid host key verification
setup_ssh() {
    local ssh_dir="${HOME}/.ssh"
    mkdir -p "${ssh_dir}"
    chmod 700 "${ssh_dir}"
    
    # Configure SSH to automatically accept host keys
    cat > "${ssh_dir}/config" <<- 'EOF'
Host *
    StrictHostKeyChecking no
    UserKnownHostsFile=/dev/null
    LogLevel ERROR
EOF
    
    chmod 600 "${ssh_dir}/config"
}

# Function to log messages
log() {
    echo -e "${GREEN}[TEST]${NC} $(date '+%Y-%m-%d %H:%M:%S') - $1"
}

# Function to log info messages
info() {
    echo -e "${BLUE}[INFO]${NC} $(date '+%Y-%m-%d %H:%M:%S') - $1"
}

# Function to log warnings
warn() {
    echo -e "${YELLOW}[WARN]${NC} $(date '+%Y-%m-%d %H:%M:%S') - $1" >&2
}

# Function to log errors and exit
error() {
    echo -e "${RED}[ERROR]${NC} $(date '+%Y-%m-%d %H:%M:%S') - $1" >&2
    exit 1
}

# Function to check if a command exists
command_exists() {
    command -v "$1" >/dev/null 2>&1
}

# Install system dependencies
install_system_deps() {
    if [ ${#SYSTEM_DEPS[@]} -gt 0 ]; then
        log "Installing system dependencies: ${SYSTEM_DEPS[*]}"
        
        # Check if we're root or can use sudo
        if [ "$(id -u)" -eq 0 ]; then
            apt-get update
            if ! DEBIAN_FRONTEND=noninteractive apt-get install -y --no-install-recommends "${SYSTEM_DEPS[@]}"; then
                warn "Failed to install system dependencies as root"
                return 1
            fi
        elif command -v sudo >/dev/null 2>&1; then
            if ! sudo DEBIAN_FRONTEND=noninteractive apt-get update || \
               ! sudo DEBIAN_FRONTEND=noninteractive apt-get install -y --no-install-recommends "${SYSTEM_DEPS[@]}"; then
                warn "Failed to install system dependencies with sudo"
                return 1
            fi
        else
            warn "Cannot install system dependencies - need root access or sudo"
            return 1
        fi
    fi
    return 0
}

# Install Python dependencies in a virtual environment
install_python_deps() {
    if [ ${#PYTHON_DEPS[@]} -gt 0 ]; then
        log "Installing Python dependencies: ${PYTHON_DEPS[*]}"
        
        # Create and activate virtual environment
        python3 -m venv /app/venv
        # shellcheck source=/dev/null
        . /app/venv/bin/activate
        
        # Upgrade pip and setuptools
        pip install --no-cache-dir --upgrade pip setuptools wheel
        
        # Install dependencies
        if ! pip install --no-cache-dir "${PYTHON_DEPS[@]}"; then
            warn "Failed to install some Python dependencies"
            return 1
        fi
    fi
    return 0
}

# Clone the repository with retry logic
clone_repo() {
    local repo_dir="/tmp/repo"
    local max_retries=3
    local retry_delay=5
    
    if [ -d "$repo_dir" ]; then
        log "Repository directory already exists, removing it..."
        rm -rf "$repo_dir"
    fi
    
    log "Cloning repository: $REPO_URL (branch: $BRANCH)"
    
    # Try cloning with retries
    local attempt=1
    while [ $attempt -le $max_retries ]; do
        info "Attempt $attempt of $max_retries: Cloning repository..."
        
        if git clone --depth 1 --branch "$BRANCH" "$REPO_URL" "$repo_dir" 2>/dev/null; then
            cd "$repo_dir" || error "Failed to change to repository directory"
            log "Successfully cloned repository to $repo_dir"
            return 0
        fi
        
        warn "Clone attempt $attempt failed"
        
        if [ $attempt -lt $max_retries ]; then
            info "Retrying in $retry_delay seconds..."
            sleep $retry_delay
        fi
        
        attempt=$((attempt + 1))
    done
    
    error "Failed to clone repository after $max_retries attempts"
}

# Run make targets with timeout
run_make_targets() {
    local start_time
    local elapsed
    
    start_time=$(date +%s)
    
    for target in "${MAKE_TARGETS[@]}"; do
        log "Running make target: $target"
        
        # Check if we've exceeded the timeout
        elapsed=$(( $(date +%s) - start_time ))
        if [ $elapsed -ge $TEST_TIMEOUT ]; then
            error "Test timeout of ${TEST_TIMEOUT}s exceeded"
        fi
        
        # Calculate remaining time
        local remaining_time=$((TEST_TIMEOUT - elapsed))
        
        # Run the target with timeout
        if ! timeout $remaining_time make "$target"; then
            error "Make target '$target' failed"
        fi
    done
}

# Main function
main() {
    # Set up SSH configuration
    setup_ssh
    
    log "Starting test environment setup"
    info "Configuration:"
    info "  REPO_URL: $REPO_URL"
    info "  BRANCH: $BRANCH"
    info "  MAKE_TARGETS: ${MAKE_TARGETS[*]}"
    info "  PYTHON_DEPS: ${PYTHON_DEPS[*]}"
    info "  SYSTEM_DEPS: ${SYSTEM_DEPS[*]}"
    info "  TEST_TIMEOUT: ${TEST_TIMEOUT}s"
    
    # Install system dependencies
    if ! install_system_deps; then
        warn "Some system dependencies failed to install, but continuing..."
    fi
    
    # Install Python dependencies
    if ! install_python_deps; then
        warn "Some Python dependencies failed to install, but continuing..."
    fi
    
    # Clone the repository
    clone_repo
    
    # Install project in development mode if setup.py exists
    if [ -f "setup.py" ]; then
        log "Installing project in development mode..."
        if ! pip install -e .; then
            warn "Failed to install project in development mode"
            return 1
        fi
    else
        warn "No setup.py found, skipping project installation"
    fi
    
    # Run make targets
    run_make_targets
    
    log "All tests completed successfully"
    exit 0
}

# Run the main function
main "$@"
