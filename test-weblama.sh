#!/bin/bash

# Test WebLama with APILama
# This script starts only the WebLama frontend and APILama backend for testing

# Set default ports
APILAMA_PORT=9095
WEBLAMA_PORT=9086

# Set default host
HOST=127.0.0.1

# Create logs directory if it doesn't exist
mkdir -p logs

# Function to check if a port is in use
port_in_use() {
  lsof -i:"$1" >/dev/null 2>&1
  return $?
}

# Start APILama
start_apilama() {
  echo "Starting APILama on port $APILAMA_PORT..."
  
  if port_in_use "$APILAMA_PORT"; then
    echo "Warning: Port $APILAMA_PORT is already in use. APILama may not start correctly."
  fi
  
  # Create a simple HTTP server that responds to API requests
  cd /home/tom/github/py-lama/apilama
  python3 -m http.server $APILAMA_PORT > ../logs/apilama.log 2>&1 &
  
  # Store the PID
  echo $! > "../logs/apilama.pid"
  
  echo "APILama started with PID $(cat "../logs/apilama.pid")"
  echo "Logs available at logs/apilama.log"
}

# Start WebLama
start_weblama() {
  echo "Starting WebLama on port $WEBLAMA_PORT..."
  
  if port_in_use "$WEBLAMA_PORT"; then
    echo "Warning: Port $WEBLAMA_PORT is already in use. WebLama may not start correctly."
  fi
  
  cd /home/tom/github/py-lama/weblama
  node ./bin/weblama-cli.js start --port $WEBLAMA_PORT --api-url http://$HOST:$APILAMA_PORT > ../logs/weblama.log 2>&1 &
  
  # Store the PID
  echo $! > "../logs/weblama.pid"
  
  echo "WebLama started with PID $(cat "../logs/weblama.pid")"
  echo "Logs available at logs/weblama.log"
}

# Function to stop a service
stop_service() {
  local name=$1
  
  if [ -f "logs/$name.pid" ]; then
    local pid=$(cat "logs/$name.pid")
    echo "Stopping $name (PID: $pid)..."
    kill "$pid" 2>/dev/null || true
    rm -f "logs/$name.pid"
    echo "$name stopped"
  else
    echo "$name is not running"
  fi
}

# Function to stop all services
stop_all() {
  echo "Stopping all services..."
  stop_service "apilama"
  stop_service "weblama"
  echo "All services stopped"
}

# Handle command line arguments
case "$1" in
  start)
    # Start services
    start_apilama
    sleep 2
    start_weblama
    
    echo "Services started. Access WebLama at http://$HOST:$WEBLAMA_PORT"
    ;;
    
  stop)
    stop_all
    ;;
    
  restart)
    stop_all
    sleep 2
    "$0" start
    ;;
    
  status)
    echo "Test Services Status:"
    for service in apilama weblama; do
      if [ -f "logs/$service.pid" ]; then
        pid=$(cat "logs/$service.pid")
        if kill -0 "$pid" 2>/dev/null; then
          echo "$service: Running (PID: $pid)"
        else
          echo "$service: Not running (stale PID file)"
        fi
      else
        echo "$service: Not running"
      fi
    done
    ;;
    
  logs)
    service=$2
    if [ -z "$service" ]; then
      echo "Usage: $0 logs [service]"
      echo "Available services: apilama, weblama"
      exit 1
    fi
    
    if [ -f "logs/$service.log" ]; then
      tail -f "logs/$service.log"
    else
      echo "Log file for $service not found"
      exit 1
    fi
    ;;
    
  open)
    echo "Opening WebLama in browser..."
    cd weblama && node ./bin/weblama-cli.js start --open
    ;;
    
  *)
    echo "Usage: $0 {start|stop|restart|status|logs|open}"
    echo "  start   - Start test services"
    echo "  stop    - Stop test services"
    echo "  restart - Restart test services"
    echo "  status  - Show status of test services"
    echo "  logs    - View logs for a specific service"
    echo "  open    - Open WebLama in browser"
    exit 1
    ;;
esac

exit 0
