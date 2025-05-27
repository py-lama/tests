#!/bin/bash

# PyLama Ecosystem Management Script
# This script manages all components of the PyLama ecosystem

# Set default ports
PYLAMA_PORT=7003
APILAMA_PORT=7080
SHELLAMA_PORT=7002
BEXY_PORT=7000
PYLLM_PORT=7001
WEBLAMA_PORT=6081

# Set default host
HOST=127.0.0.1

# Create logs directory if it doesn't exist
mkdir -p logs

# Colors for better output
RED="\033[0;31m"
GREEN="\033[0;32m"
YELLOW="\033[0;33m"
BLUE="\033[0;34m"
NC="\033[0m" # No Color

# Function to check if a port is in use
port_in_use() {
  lsof -i:"$1" >/dev/null 2>&1
  return $?
}

# Function to check if Docker is running
docker_running() {
  docker info >/dev/null 2>&1
  return $?
}

# Function to check if a virtual environment exists
check_venv() {
  local dir=$1
  if [ -d "$dir/venv" ] && [ -f "$dir/venv/bin/activate" ]; then
    return 0  # venv exists
  elif [ -d "$dir/.venv" ] && [ -f "$dir/.venv/bin/activate" ]; then
    return 0  # .venv exists
  else
    return 1  # venv doesn't exist
  fi
}

# Function to get the correct venv path
get_venv_path() {
  local dir=$1
  if [ -d "$dir/venv" ] && [ -f "$dir/venv/bin/activate" ]; then
    echo "venv"
  elif [ -d "$dir/.venv" ] && [ -f "$dir/.venv/bin/activate" ]; then
    echo ".venv"
  else
    echo ""
  fi
}

# Function to install dependencies for a service
install_dependencies() {
  local name=$1
  local dir=$2
  
  echo -e "${BLUE}Installing dependencies for $name...${NC}"
  
  cd "$dir" || { echo -e "${RED}Error: Directory $dir not found${NC}"; return 1; }
  
  # Check if requirements.txt exists
  if [ -f "requirements.txt" ]; then
    if check_venv "."; then
      venv_path=$(get_venv_path ".")
      echo -e "${BLUE}Installing dependencies from requirements.txt...${NC}"
      . "$venv_path/bin/activate" && pip install -r requirements.txt
      deactivate
    else
      echo -e "${YELLOW}Warning: No virtual environment found for $name. Skipping dependency installation.${NC}"
      return 1
    fi
  else
    echo -e "${YELLOW}Warning: No requirements.txt found for $name. Skipping dependency installation.${NC}"
  fi
  
  # Return to the original directory
  cd - > /dev/null
  return 0
}

# Function to start a service
start_service() {
  local name=$1
  local dir=$2
  local port=$3
  local cmd=$4
  
  echo -e "${BLUE}Starting $name on port $port...${NC}"
  
  if port_in_use "$port"; then
    echo -e "${YELLOW}Warning: Port $port is already in use. $name may not start correctly.${NC}"
  fi
  
  cd "$dir" || { echo -e "${RED}Error: Directory $dir not found${NC}"; return 1; }
  
  # Install dependencies if needed
  if [ "$name" != "weblama" ]; then  # Skip for weblama as it's Node.js
    if check_venv "."; then
      venv_path=$(get_venv_path ".")
      . "$venv_path/bin/activate" && pip install -e . 2>/dev/null
      deactivate
    fi
  fi
  
  # Start the service in the background
  eval "$cmd" > "../logs/$name.log" 2>&1 &
  
  # Store the PID
  echo $! > "../logs/$name.pid"
  
  # Return to the original directory
  cd - > /dev/null
  
  echo -e "${GREEN}$name started with PID $(cat "logs/$name.pid")${NC}"
  echo -e "${BLUE}Logs available at logs/$name.log${NC}"
  return 0
}

# Function to stop a service
stop_service() {
  local name=$1
  
  if [ -f "logs/$name.pid" ]; then
    local pid=$(cat "logs/$name.pid")
    echo -e "${BLUE}Stopping $name (PID: $pid)...${NC}"
    kill "$pid" 2>/dev/null || true
    rm -f "logs/$name.pid"
    echo -e "${GREEN}$name stopped${NC}"
  else
    echo -e "${YELLOW}$name is not running${NC}"
  fi
}

# Function to stop all services
stop_all() {
  echo -e "${BLUE}Stopping all services...${NC}"
  stop_service "bexy"
  stop_service "pyllm"
  stop_service "shellama"
  stop_service "apilama"
  stop_service "pylama"
  stop_service "weblama"
  echo -e "${GREEN}All services stopped${NC}"
}

# Function to start services using Docker
start_docker() {
  if ! docker_running; then
    echo -e "${RED}Error: Docker is not running. Please start Docker first.${NC}"
    return 1
  fi
  
  echo -e "${BLUE}Starting PyLama ecosystem using Docker...${NC}"
  docker-compose up -d
  echo -e "${GREEN}Docker containers started. Access WebLama at http://localhost:8081${NC}"
}

# Function to stop Docker containers
stop_docker() {
  if ! docker_running; then
    echo -e "${RED}Error: Docker is not running.${NC}"
    return 1
  fi
  
  echo -e "${BLUE}Stopping PyLama ecosystem Docker containers...${NC}"
  docker-compose down
  echo -e "${GREEN}Docker containers stopped${NC}"
}

# Handle command line arguments
case "$1" in
  start)
    # Check if Docker mode is requested
    if [ "$2" = "--docker" ]; then
      start_docker
      exit $?
    fi
    
    # Install dependencies for all services first
    echo -e "${BLUE}Installing dependencies for all services...${NC}"
    for service in bexy pyllm shellama apilama pylama; do
      install_dependencies "$service" "$service"
    done
    
    # Install Node.js dependencies for WebLama
    if [ -d "weblama" ]; then
      echo -e "${BLUE}Installing dependencies for WebLama...${NC}"
      cd weblama && npm install --silent && cd - > /dev/null
    fi
    
    # Start all services in the correct order
    
    # BEXY
    if check_venv "bexy"; then
      venv_path=$(get_venv_path "bexy")
      start_service "bexy" "bexy" "$BEXY_PORT" ". $venv_path/bin/activate && python -m bexy.app --port $BEXY_PORT --host $HOST"
    else
      echo -e "${YELLOW}Warning: BEXY virtual environment not found. Using system Python.${NC}"
      start_service "bexy" "bexy" "$BEXY_PORT" "python -m bexy.app --port $BEXY_PORT --host $HOST 2>/dev/null || python3 -m bexy.app --port $BEXY_PORT --host $HOST 2>/dev/null || echo 'Failed to start BEXY'"
    fi
    sleep 2
    
    # PyLLM
    if check_venv "pyllm"; then
      venv_path=$(get_venv_path "pyllm")
      start_service "pyllm" "pyllm" "$PYLLM_PORT" ". $venv_path/bin/activate && python -m pyllm.app --port $PYLLM_PORT --host $HOST"
    else
      echo -e "${YELLOW}Warning: PyLLM virtual environment not found. Using system Python.${NC}"
      start_service "pyllm" "pyllm" "$PYLLM_PORT" "python -m pyllm.app --port $PYLLM_PORT --host $HOST 2>/dev/null || python3 -m pyllm.app --port $PYLLM_PORT --host $HOST 2>/dev/null || echo 'Failed to start PyLLM'"
    fi
    sleep 2
    
    # SheLLama
    if check_venv "shellama"; then
      venv_path=$(get_venv_path "shellama")
      start_service "shellama" "shellama" "$SHELLAMA_PORT" ". $venv_path/bin/activate && python -m shellama.app --port $SHELLAMA_PORT --host $HOST"
    else
      echo -e "${YELLOW}Warning: SheLLama virtual environment not found. Using system Python.${NC}"
      start_service "shellama" "shellama" "$SHELLAMA_PORT" "python -m shellama.app --port $SHELLAMA_PORT --host $HOST 2>/dev/null || python3 -m shellama.app --port $SHELLAMA_PORT --host $HOST 2>/dev/null || echo 'Failed to start SheLLama'"
    fi
    sleep 2
    
    # APILama
    if check_venv "apilama"; then
      venv_path=$(get_venv_path "apilama")
      start_service "apilama" "apilama" "$APILAMA_PORT" ". $venv_path/bin/activate && python -m apilama.app --port $APILAMA_PORT --host $HOST"
    else
      echo -e "${YELLOW}Warning: APILama virtual environment not found. Using system Python.${NC}"
      start_service "apilama" "apilama" "$APILAMA_PORT" "python -m apilama.app --port $APILAMA_PORT --host $HOST 2>/dev/null || python3 -m apilama.app --port $APILAMA_PORT --host $HOST 2>/dev/null || echo 'Failed to start APILama'"
    fi
    sleep 2
    
    # PyLama
    if check_venv "pylama"; then
      venv_path=$(get_venv_path "pylama")
      start_service "pylama" "pylama" "$PYLAMA_PORT" ". $venv_path/bin/activate && python -m pylama.app --port $PYLAMA_PORT --host $HOST"
    else
      echo -e "${YELLOW}Warning: PyLama virtual environment not found. Using system Python.${NC}"
      start_service "pylama" "pylama" "$PYLAMA_PORT" "python -m pylama.app --port $PYLAMA_PORT --host $HOST 2>/dev/null || python3 -m pylama.app --port $PYLAMA_PORT --host $HOST 2>/dev/null || echo 'Failed to start PyLama'"
    fi
    sleep 2
    
    # WebLama (no virtual environment needed)
    start_service "weblama" "weblama" "$WEBLAMA_PORT" "node ./bin/weblama-cli.js start --port $WEBLAMA_PORT --api-url http://$HOST:$APILAMA_PORT"
    
    echo -e "${GREEN}All services started. Access WebLama at http://$HOST:$WEBLAMA_PORT${NC}"
    echo -e "${BLUE}To open in browser: node weblama/bin/weblama-cli.js start --open${NC}"
    ;;
    
  stop)
    # Check if Docker mode is requested
    if [ "$2" = "--docker" ]; then
      stop_docker
      exit $?
    fi
    
    stop_all
    ;;
    
  restart)
    # Check if Docker mode is requested
    if [ "$2" = "--docker" ]; then
      stop_docker
      sleep 2
      start_docker
      exit $?
    fi
    
    stop_all
    sleep 2
    "$0" start
    ;;
    
  status)
    echo -e "${BLUE}PyLama Ecosystem Status:${NC}"
    for service in bexy pyllm shellama apilama pylama weblama; do
      if [ -f "logs/$service.pid" ]; then
        pid=$(cat "logs/$service.pid")
        if kill -0 "$pid" 2>/dev/null; then
          echo -e "${GREEN}$service: Running (PID: $pid)${NC}"
        else
          echo -e "${YELLOW}$service: Not running (stale PID file)${NC}"
        fi
      else
        echo -e "${RED}$service: Not running${NC}"
      fi
    done
    
    # Check Docker status if Docker is running
    if docker_running; then
      echo -e "\n${BLUE}Docker Container Status:${NC}"
      docker-compose ps
    fi
    ;;
    
  logs)
    service=$2
    if [ -z "$service" ]; then
      echo -e "${YELLOW}Usage: $0 logs [service]${NC}"
      echo -e "${BLUE}Available services: bexy, pyllm, shellama, apilama, pylama, weblama${NC}"
      exit 1
    fi
    
    # Check if Docker mode is requested
    if [ "$3" = "--docker" ]; then
      if ! docker_running; then
        echo -e "${RED}Error: Docker is not running.${NC}"
        exit 1
      fi
      
      echo -e "${BLUE}Showing logs for $service container...${NC}"
      docker-compose logs -f "$service"
      exit $?
    fi
    
    # Create logs directory if it doesn't exist
    mkdir -p logs
    
    # Create an empty log file if it doesn't exist
    touch "logs/$service.log"
    
    # Display the log file
    echo -e "${BLUE}=== Showing logs for $service ===${NC}"
    echo -e "${YELLOW}Press Ctrl+C to exit${NC}"
    
    # Stay in the current directory and just tail the log file
    # This avoids any issues with trying to change directory or activate virtual environments
    tail -f "logs/$service.log"
    ;;
    
  open)
    echo -e "${BLUE}Opening WebLama in browser...${NC}"
    cd weblama && node ./bin/weblama-cli.js start --open
    ;;
    
  setup)
    echo -e "${BLUE}Setting up PyLama ecosystem...${NC}"
    
    # Create virtual environments for each service
    for service in bexy pyllm shellama apilama pylama; do
      echo -e "${BLUE}Setting up $service...${NC}"
      if [ -d "$service" ]; then
        cd "$service" || continue
        
        # Create virtual environment if it doesn't exist
        if [ ! -d "venv" ] && [ ! -d ".venv" ]; then
          echo -e "${BLUE}Creating virtual environment for $service...${NC}"
          python -m venv venv || python3 -m venv venv || { echo -e "${RED}Failed to create virtual environment for $service${NC}"; cd - > /dev/null; continue; }
        fi
        
        # Activate virtual environment and install dependencies
        venv_path=$(get_venv_path .)
        if [ -n "$venv_path" ]; then
          echo -e "${BLUE}Installing dependencies for $service...${NC}"
          . "$venv_path/bin/activate" && pip install -e . && pip install -r requirements.txt 2>/dev/null
          deactivate
          echo -e "${GREEN}$service setup complete${NC}"
        else
          echo -e "${RED}Failed to find virtual environment for $service${NC}"
        fi
        
        cd - > /dev/null
      else
        echo -e "${RED}Directory $service not found${NC}"
      fi
    done
    
    # Set up WebLama (Node.js)
    echo -e "${BLUE}Setting up WebLama...${NC}"
    if [ -d "weblama" ]; then
      cd weblama || exit 1
      npm install
      chmod +x ./bin/weblama-cli.js
      cd - > /dev/null
      echo -e "${GREEN}WebLama setup complete${NC}"
    else
      echo -e "${RED}Directory weblama not found${NC}"
    fi
    
    echo -e "${GREEN}PyLama ecosystem setup complete${NC}"
    ;;
    
  docker)
    echo -e "${BLUE}Managing PyLama Docker containers...${NC}"
    
    case "$2" in
      build)
        echo -e "${BLUE}Building Docker images...${NC}"
        docker-compose build
        echo -e "${GREEN}Docker images built${NC}"
        ;;
        
      up)
        echo -e "${BLUE}Starting Docker containers...${NC}"
        docker-compose up -d
        echo -e "${GREEN}Docker containers started${NC}"
        ;;
        
      down)
        echo -e "${BLUE}Stopping Docker containers...${NC}"
        docker-compose down
        echo -e "${GREEN}Docker containers stopped${NC}"
        ;;
        
      logs)
        service=$3
        if [ -z "$service" ]; then
          echo -e "${BLUE}Showing logs for all containers...${NC}"
          docker-compose logs -f
        else
          echo -e "${BLUE}Showing logs for $service container...${NC}"
          docker-compose logs -f "$service"
        fi
        ;;
        
      *)
        echo -e "${YELLOW}Usage: $0 docker {build|up|down|logs [service]}${NC}"
        exit 1
        ;;
    esac
    ;;
    
  *)
    echo -e "${BLUE}PyLama Ecosystem Management Script${NC}"
    echo -e "${YELLOW}Usage: $0 {start|stop|restart|status|logs|open|setup|docker}${NC}"
    echo -e "  ${GREEN}start   ${NC}- Start all PyLama services"
    echo -e "  ${GREEN}stop    ${NC}- Stop all PyLama services"
    echo -e "  ${GREEN}restart ${NC}- Restart all PyLama services"
    echo -e "  ${GREEN}status  ${NC}- Show status of all services"
    echo -e "  ${GREEN}logs    ${NC}- View logs for a specific service"
    echo -e "  ${GREEN}open    ${NC}- Open WebLama in browser"
    echo -e "  ${GREEN}setup   ${NC}- Set up virtual environments and install dependencies"
    echo -e "  ${GREEN}docker  ${NC}- Manage Docker containers"
    echo -e "\n${BLUE}Docker Options:${NC}"
    echo -e "  ${GREEN}--docker${NC} - Use Docker mode with start, stop, restart, or logs commands"
    echo -e "    Example: $0 start --docker"
    exit 1
    ;;
esac

exit 0
