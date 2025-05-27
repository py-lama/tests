#!/bin/bash

# Script to run PyLama with LogLama and WebLama with proper log collection

# Define colors for output
GREEN="\033[0;32m"
YELLOW="\033[0;33m"
BLUE="\033[0;34m"
RED="\033[0;31m"
NC="\033[0m" # No Color

# Default ports
LOGLAMA_PORT=5001
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
      echo -e "${RED}Unknown option: $1${NC}"
      exit 1
      ;;
  esac
done

# Function to check if a port is in use
function is_port_in_use() {
  lsof -i:"$1" >/dev/null 2>&1
  return $?
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

# Create logs directory if it doesn't exist
mkdir -p logs

# Step 1: Reset LogLama database to ensure proper schema
echo -e "\n${BLUE}Step 1: Resetting LogLama database...${NC}"
rm -f logs/loglama.db
echo -e "${GREEN}LogLama database reset${NC}"

# Step 2: Start LogLama
echo -e "\n${BLUE}Step 2: Starting LogLama...${NC}"
cd loglama
python -m loglama.cli.main web --port $LOGLAMA_PORT --host 127.0.0.1 --db ../logs/loglama.db &
LOGLAMA_PID=$!
cd ..

# Wait for LogLama to be available
wait_for_service $LOGLAMA_PORT "LogLama"
if [ $? -ne 0 ]; then
  echo -e "${RED}Failed to start LogLama. Exiting.${NC}"
  kill $LOGLAMA_PID 2>/dev/null
  exit 1
fi

# Step 3: Start the log collector
echo -e "\n${BLUE}Step 3: Starting log collector...${NC}"
cd loglama
python -m loglama.cli.main collect-daemon --background
cd ..

# Step 4: Start WebLama with log collection enabled
echo -e "\n${BLUE}Step 4: Starting WebLama with log collection...${NC}"
cd weblama
PORT=$WEBLAMA_PORT HOST=127.0.0.1 COLLECT=1 make web &
WEBLAMA_PID=$!
cd ..

# Wait for WebLama to be available
wait_for_service $WEBLAMA_PORT "WebLama"
if [ $? -ne 0 ]; then
  echo -e "${RED}Failed to start WebLama. Exiting.${NC}"
  kill $LOGLAMA_PID $WEBLAMA_PID 2>/dev/null
  exit 1
fi

# Step 5: Open LogLama in the browser
echo -e "\n${BLUE}Step 5: Opening LogLama in browser...${NC}"
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

# Step 6: Open WebLama in the browser
echo -e "\n${BLUE}Step 6: Opening WebLama in browser...${NC}"

# Open WebLama in the default browser
if command -v xdg-open &> /dev/null; then
  xdg-open "http://localhost:$WEBLAMA_PORT" &
elif command -v open &> /dev/null; then
  open "http://localhost:$WEBLAMA_PORT" &
elif command -v python &> /dev/null; then
  python -m webbrowser "http://localhost:$WEBLAMA_PORT" &
else
  echo -e "${YELLOW}Please open WebLama manually at: http://localhost:$WEBLAMA_PORT${NC}"
fi

echo -e "\n${GREEN}Setup complete!${NC}"
echo -e "LogLama is running at: http://localhost:$LOGLAMA_PORT"
echo -e "WebLama is running at: http://localhost:$WEBLAMA_PORT"
echo -e "\nPress Ctrl+C to stop all services"

# Wait for user to press Ctrl+C
trap "echo -e '\n${YELLOW}Stopping services...${NC}' && kill $LOGLAMA_PID $WEBLAMA_PID 2>/dev/null" INT
wait
