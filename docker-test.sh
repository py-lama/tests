#!/bin/bash

# Script to manage PyLama Docker Compose setup for testing

# Define colors for output
GREEN="\033[0;32m"
YELLOW="\033[0;33m"
BLUE="\033[0;34m"
RED="\033[0;31m"
NC="\033[0m" # No Color

# Docker Compose file for testing
DOCKER_COMPOSE_FILE="docker-compose-test.yml"

# Function to check if Docker is running
check_docker() {
  if ! docker info > /dev/null 2>&1; then
    echo -e "${RED}Error: Docker is not running. Please start Docker and try again.${NC}"
    exit 1
  fi
}

# Function to start all services
start_services() {
  echo -e "${BLUE}Starting PyLama ecosystem with LogLama integration for testing...${NC}"
  
  # Create logs directory if it doesn't exist
  mkdir -p logs
  
  # Build and start all services
  docker-compose -f $DOCKER_COMPOSE_FILE up -d --build
  
  # Wait for services to be ready
  echo -e "${YELLOW}Waiting for services to start...${NC}"
  sleep 5
  
  # Display service status
  docker-compose -f $DOCKER_COMPOSE_FILE ps
  
  echo -e "\n${GREEN}All services started successfully!${NC}"
  echo -e "${GREEN}LogLama web interface: http://localhost:6001${NC}"
  echo -e "${GREEN}BEXY API: http://localhost:9000${NC}"
  echo -e "${GREEN}PyLLM API: http://localhost:9001${NC}"
  echo -e "${GREEN}SheLLama API: http://localhost:9002${NC}"
  echo -e "${GREEN}PyLama API: http://localhost:9003${NC}"
  echo -e "${GREEN}APILama API: http://localhost:9080${NC}"
  echo -e "${GREEN}WebLama interface: http://localhost:9084${NC}"
  echo -e "${YELLOW}Use 'docker-compose -f $DOCKER_COMPOSE_FILE logs -f' to view logs${NC}"
}

# Function to stop all services
stop_services() {
  echo -e "${BLUE}Stopping PyLama ecosystem...${NC}"
  docker-compose -f $DOCKER_COMPOSE_FILE down
  echo -e "${GREEN}All services stopped${NC}"
}

# Function to display service status
show_status() {
  echo -e "${BLUE}PyLama Ecosystem Status:${NC}"
  docker-compose -f $DOCKER_COMPOSE_FILE ps
  
  echo -e "\n${BLUE}Service URLs:${NC}"
  echo -e "${GREEN}LogLama: http://localhost:5001${NC}"
  echo -e "${GREEN}BEXY: http://localhost:8000${NC}"
  echo -e "${GREEN}PyLLM: http://localhost:8001${NC}"
  echo -e "${GREEN}SheLLama: http://localhost:8002${NC}"
  echo -e "${GREEN}PyLama: http://localhost:8003${NC}"
  echo -e "${GREEN}APILama: http://localhost:8080${NC}"
  echo -e "${GREEN}WebLama: http://localhost:8084${NC}"
}

# Function to view logs
view_logs() {
  service=$1
  if [ -z "$service" ]; then
    echo -e "${BLUE}Viewing logs for all services...${NC}"
    docker-compose -f $DOCKER_COMPOSE_FILE logs -f
  else
    echo -e "${BLUE}Viewing logs for $service...${NC}"
    docker-compose -f $DOCKER_COMPOSE_FILE logs -f $service
  fi
}

# Function to open LogLama in browser
open_loglama() {
  echo -e "${BLUE}Opening LogLama in browser...${NC}"
  if command -v xdg-open > /dev/null; then
    xdg-open "http://localhost:5001" &
  elif command -v open > /dev/null; then
    open "http://localhost:5001" &
  else
    python -m webbrowser "http://localhost:5001" &
  fi
}

# Function to open WebLama in browser
open_weblama() {
  echo -e "${BLUE}Opening WebLama in browser...${NC}"
  if command -v xdg-open > /dev/null; then
    xdg-open "http://localhost:8084" &
  elif command -v open > /dev/null; then
    open "http://localhost:8084" &
  else
    python -m webbrowser "http://localhost:8084" &
  fi
}

# Function to run tests
run_tests() {
  echo -e "${BLUE}Running tests against the Docker services...${NC}"
  
  # Check if services are running
  if ! docker-compose -f $DOCKER_COMPOSE_FILE ps | grep -q "Up"; then
    echo -e "${RED}Error: Services are not running. Please start them first with './docker-test.sh start'${NC}"
    exit 1
  fi
  
  # Run tests for each service
  echo -e "${YELLOW}Testing LogLama...${NC}"
  curl -s http://localhost:5001/api/health | grep -q "healthy" && \
    echo -e "${GREEN}LogLama is healthy!${NC}" || \
    echo -e "${RED}LogLama health check failed!${NC}"
  
  echo -e "${YELLOW}Testing BEXY...${NC}"
  curl -s http://localhost:8000/health | grep -q "healthy" && \
    echo -e "${GREEN}BEXY is healthy!${NC}" || \
    echo -e "${RED}BEXY health check failed!${NC}"
  
  echo -e "${YELLOW}Testing PyLLM...${NC}"
  curl -s http://localhost:8001/health | grep -q "healthy" && \
    echo -e "${GREEN}PyLLM is healthy!${NC}" || \
    echo -e "${RED}PyLLM health check failed!${NC}"
  
  echo -e "${YELLOW}Testing SheLLama...${NC}"
  curl -s http://localhost:8002/health | grep -q "healthy" && \
    echo -e "${GREEN}SheLLama is healthy!${NC}" || \
    echo -e "${RED}SheLLama health check failed!${NC}"
  
  echo -e "${YELLOW}Testing PyLama...${NC}"
  curl -s http://localhost:8003/health | grep -q "healthy" && \
    echo -e "${GREEN}PyLama is healthy!${NC}" || \
    echo -e "${RED}PyLama health check failed!${NC}"
  
  echo -e "${YELLOW}Testing APILama...${NC}"
  curl -s http://localhost:8080/health | grep -q "healthy" && \
    echo -e "${GREEN}APILama is healthy!${NC}" || \
    echo -e "${RED}APILama health check failed!${NC}"
  
  echo -e "${YELLOW}Testing WebLama...${NC}"
  curl -s -I http://localhost:8084 | grep -q "200 OK" && \
    echo -e "${GREEN}WebLama is responding!${NC}" || \
    echo -e "${RED}WebLama check failed!${NC}"
  
  echo -e "\n${GREEN}Tests completed!${NC}"
}

# Check if Docker is running
check_docker

# Parse command line arguments
case "$1" in
  start)
    start_services
    ;;
  stop)
    stop_services
    ;;
  restart)
    stop_services
    start_services
    ;;
  status)
    show_status
    ;;
  logs)
    view_logs $2
    ;;
  open-loglama)
    open_loglama
    ;;
  open-weblama)
    open_weblama
    ;;
  open)
    open_loglama
    open_weblama
    ;;
  test)
    run_tests
    ;;
  *)
    echo -e "${BLUE}PyLama Docker Testing Script${NC}"
    echo -e "${YELLOW}Usage: $0 {start|stop|restart|status|logs|open-loglama|open-weblama|open|test}${NC}"
    echo -e "  ${GREEN}start        ${NC}- Start all PyLama services with LogLama integration"
    echo -e "  ${GREEN}stop         ${NC}- Stop all PyLama services"
    echo -e "  ${GREEN}restart      ${NC}- Restart all PyLama services"
    echo -e "  ${GREEN}status       ${NC}- Show status of all services"
    echo -e "  ${GREEN}logs [service]${NC}- View logs for all or specific service"
    echo -e "  ${GREEN}open-loglama ${NC}- Open LogLama in browser"
    echo -e "  ${GREEN}open-weblama ${NC}- Open WebLama in browser"
    echo -e "  ${GREEN}open         ${NC}- Open both LogLama and WebLama in browser"
    echo -e "  ${GREEN}test         ${NC}- Run tests against the running services"
    ;;
esac

exit 0
