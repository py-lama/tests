#!/bin/bash

# Script to manage PyLama Docker Compose setup with LogLama integration

# Define colors for output
GREEN="\033[0;32m"
YELLOW="\033[0;33m"
BLUE="\033[0;34m"
RED="\033[0;31m"
NC="\033[0m" # No Color

# Docker Compose file with LogLama integration
DOCKER_COMPOSE_FILE="docker-compose.logging.yml"

# Function to check if Docker is running
check_docker() {
  if ! docker info > /dev/null 2>&1; then
    echo -e "${RED}Error: Docker is not running. Please start Docker and try again.${NC}"
    exit 1
  fi
}

# Function to start all services
start_services() {
  echo -e "${BLUE}Starting PyLama ecosystem with LogLama integration...${NC}"
  
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
  echo -e "${GREEN}LogLama web interface: http://localhost:5001${NC}"
  echo -e "${GREEN}WebLama interface: http://localhost:9081${NC}"
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
  echo -e "${GREEN}PyBox: http://localhost:9000${NC}"
  echo -e "${GREEN}PyLLM: http://localhost:9001${NC}"
  echo -e "${GREEN}SheLLama: http://localhost:9002${NC}"
  echo -e "${GREEN}PyLama: http://localhost:9003${NC}"
  echo -e "${GREEN}APILama: http://localhost:9080${NC}"
  echo -e "${GREEN}WebLama: http://localhost:9081${NC}"
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
    xdg-open "http://localhost:9081" &
  elif command -v open > /dev/null; then
    open "http://localhost:9081" &
  else
    python -m webbrowser "http://localhost:9081" &
  fi
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
  *)
    echo -e "${BLUE}PyLama Docker Management Script${NC}"
    echo -e "${YELLOW}Usage: $0 {start|stop|restart|status|logs|open-loglama|open-weblama|open}${NC}"
    echo -e "  ${GREEN}start        ${NC}- Start all PyLama services with LogLama integration"
    echo -e "  ${GREEN}stop         ${NC}- Stop all PyLama services"
    echo -e "  ${GREEN}restart      ${NC}- Restart all PyLama services"
    echo -e "  ${GREEN}status       ${NC}- Show status of all services"
    echo -e "  ${GREEN}logs [service]${NC}- View logs for all or specific service"
    echo -e "  ${GREEN}open-loglama ${NC}- Open LogLama in browser"
    echo -e "  ${GREEN}open-weblama ${NC}- Open WebLama in browser"
    echo -e "  ${GREEN}open         ${NC}- Open both LogLama and WebLama in browser"
    ;;
esac

exit 0
