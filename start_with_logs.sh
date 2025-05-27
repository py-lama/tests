#!/bin/bash

# Script to start LogLama first, then WebLama, and ensure logs are properly collected
# This script also installs required dependencies if they're missing

echo "Starting PyLama ecosystem with log collection..."

# Define colors for output
GREEN="\033[0;32m"
YELLOW="\033[0;33m"
BLUE="\033[0;34m"
RED="\033[0;31m"
NC="\033[0m" # No Color

# Find the root directory
ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$ROOT_DIR"

# Function to check and install Python dependencies
function check_and_install_dependencies() {
  local package=$1
  local package_name=${2:-$package}
  
  echo -e "${YELLOW}Checking for $package_name...${NC}"
  
  # Check if package is installed
  python -c "import $package" 2>/dev/null
  if [ $? -ne 0 ]; then
    echo -e "${YELLOW}Installing $package_name...${NC}"
    pip install $package_name
    if [ $? -ne 0 ]; then
      echo -e "${RED}Failed to install $package_name. Please install it manually.${NC}"
      return 1
    fi
    echo -e "${GREEN}$package_name installed successfully.${NC}"
  else
    echo -e "${GREEN}$package_name is already installed.${NC}"
  fi
  
  return 0
}

# Set default ports
LOGLAMA_PORT=5000
WEBLAMA_PORT=8084

# Parse command line arguments
while [[ $# -gt 0 ]]; do
  case $1 in
    --loglama-port=*)
      LOGLAMA_PORT="${1#*=}"
      shift
      ;;
    --weblama-port=*)
      WEBLAMA_PORT="${1#*=}"
      shift
      ;;
    *)
      echo "Unknown option: $1"
      exit 1
      ;;
  esac
done

# Function to check if a port is in use
function is_port_in_use() {
  if command -v nc &> /dev/null; then
    nc -z localhost $1 &> /dev/null
    return $?
  elif command -v lsof &> /dev/null; then
    lsof -i:$1 &> /dev/null
    return $?
  else
    # Fallback to a simple socket connection
    (echo > /dev/tcp/localhost/$1) &> /dev/null
    return $?
  fi
}

# Function to wait for a service to be available
function wait_for_service() {
  local port=$1
  local service_name=$2
  local max_attempts=30
  local attempt=1

  echo -e "${YELLOW}Waiting for $service_name to be available on port $port...${NC}"
  
  while ! is_port_in_use $port; do
    if [ $attempt -ge $max_attempts ]; then
      echo -e "${RED}$service_name did not start within the expected time.${NC}"
      return 1
    fi
    
    echo -n "."
    sleep 1
    ((attempt++))
  done
  
  echo -e "\n${GREEN}$service_name is now available on port $port!${NC}"
  return 0
}

# Step 0: Install required dependencies
echo -e "\n${BLUE}Step 0: Installing required dependencies...${NC}"

# Define required dependencies
REQUIRED_DEPS=(
  "structlog"
  "python-dateutil"
  "flask"
)

# Install all required dependencies
for dep in "${REQUIRED_DEPS[@]}"; do
  check_and_install_dependencies "$dep"
  if [ $? -ne 0 ]; then
    echo -e "${RED}Failed to install required dependencies. Exiting.${NC}"
    exit 1
  fi
done

# Step 1: Start LogLama
echo -e "\n${BLUE}Step 1: Starting LogLama...${NC}"
cd "$ROOT_DIR/loglama"
python -m loglama.cli.main web --port $LOGLAMA_PORT &
LOGLAMA_PID=$!

# Wait for LogLama to be available
wait_for_service $LOGLAMA_PORT "LogLama"
if [ $? -ne 0 ]; then
  echo "Failed to start LogLama. Exiting."
  exit 1
fi

# Step 2: Start the log collector
echo -e "\n${BLUE}Step 2: Starting log collector...${NC}"
python -m loglama.cli.main collect-daemon --background

# Step 3: Start WebLama
echo -e "\n${BLUE}Step 3: Starting WebLama...${NC}"
cd "$ROOT_DIR/weblama"
make web PORT=$WEBLAMA_PORT COLLECT=1 &
WEBLAMA_PID=$!

# Wait for WebLama to be available
wait_for_service $WEBLAMA_PORT "WebLama"
if [ $? -ne 0 ]; then
  echo "Failed to start WebLama. Exiting."
  exit 1
fi

# Step 4: Open LogLama in the browser
echo -e "\n${BLUE}Step 4: Opening LogLama in browser...${NC}"
sleep 2 # Give a moment for everything to stabilize

# Open LogLama in the default browser
if command -v xdg-open &> /dev/null; then
  xdg-open "http://localhost:$LOGLAMA_PORT" &
elif command -v open &> /dev/null; then
  open "http://localhost:$LOGLAMA_PORT" &
elif command -v python &> /dev/null; then
  python -m webbrowser "http://localhost:$LOGLAMA_PORT" &
else
  echo -e "${YELLOW}Please open LogLama manually at: http://localhost:$LOGLAMA_PORT${NC}"
fi

echo -e "\n${GREEN}Setup complete!${NC}"
echo -e "LogLama is running at: http://localhost:$LOGLAMA_PORT"
echo -e "WebLama is running at: http://localhost:$WEBLAMA_PORT"
echo -e "\nPress Ctrl+C to stop all services"

# Wait for user to press Ctrl+C
trap "echo -e '\n${YELLOW}Stopping services...${NC}' && kill $LOGLAMA_PID $WEBLAMA_PID 2>/dev/null" INT
wait
