#!/bin/bash

# Script to test the simplified Docker setup for LogLama

# Define colors for output
GREEN="\033[0;32m"
YELLOW="\033[0;33m"
BLUE="\033[0;34m"
RED="\033[0;31m"
NC="\033[0m" # No Color

# Docker Compose file for testing
DOCKER_COMPOSE_FILE="docker-compose-simple.yml"

# Function to check if Docker is running
check_docker() {
  if ! docker info > /dev/null 2>&1; then
    echo -e "${RED}Error: Docker is not running. Please start Docker and try again.${NC}"
    exit 1
  fi
}

# Function to start LogLama service
start_service() {
  echo -e "${BLUE}Starting LogLama service for testing...${NC}"
  
  # Create logs directory if it doesn't exist
  mkdir -p logs
  
  # Build and start the service
  docker-compose -f $DOCKER_COMPOSE_FILE up -d --build
  
  # Wait for service to be ready
  echo -e "${YELLOW}Waiting for LogLama to start...${NC}"
  sleep 5
  
  # Display service status
  docker-compose -f $DOCKER_COMPOSE_FILE ps
  
  echo -e "\n${GREEN}LogLama started successfully!${NC}"
  echo -e "${GREEN}LogLama web interface: http://localhost:6001${NC}"
  echo -e "${YELLOW}Use 'docker-compose -f $DOCKER_COMPOSE_FILE logs -f' to view logs${NC}"
}

# Function to stop the service
stop_service() {
  echo -e "${BLUE}Stopping LogLama service...${NC}"
  docker-compose -f $DOCKER_COMPOSE_FILE down
  echo -e "${GREEN}LogLama stopped${NC}"
}

# Function to display service status
show_status() {
  echo -e "${BLUE}LogLama Service Status:${NC}"
  docker-compose -f $DOCKER_COMPOSE_FILE ps
  
  echo -e "\n${BLUE}Service URL:${NC}"
  echo -e "${GREEN}LogLama: http://localhost:6001${NC}"
}

# Function to view logs
view_logs() {
  echo -e "${BLUE}Viewing logs for LogLama...${NC}"
  docker-compose -f $DOCKER_COMPOSE_FILE logs -f
}

# Function to open LogLama in browser
open_loglama() {
  echo -e "${BLUE}Opening LogLama in browser...${NC}"
  if command -v xdg-open > /dev/null; then
    xdg-open "http://localhost:6001" &
  elif command -v open > /dev/null; then
    open "http://localhost:6001" &
  else
    python -m webbrowser "http://localhost:6001" &
  fi
}

# Check if Docker is running
check_docker

# Parse command line arguments
case "$1" in
  start)
    start_service
    ;;
  stop)
    stop_service
    ;;
  restart)
    stop_service
    start_service
    ;;
  status)
    show_status
    ;;
  logs)
    view_logs
    ;;
  open)
    open_loglama
    ;;
  *)
    echo -e "${BLUE}LogLama Docker Testing Script${NC}"
    echo -e "${YELLOW}Usage: $0 {start|stop|restart|status|logs|open}${NC}"
    echo -e "  ${GREEN}start        ${NC}- Start LogLama service"
    echo -e "  ${GREEN}stop         ${NC}- Stop LogLama service"
    echo -e "  ${GREEN}restart      ${NC}- Restart LogLama service"
    echo -e "  ${GREEN}status       ${NC}- Show status of LogLama service"
    echo -e "  ${GREEN}logs         ${NC}- View logs for LogLama service"
    echo -e "  ${GREEN}open         ${NC}- Open LogLama in browser"
    ;;
esac

exit 0
