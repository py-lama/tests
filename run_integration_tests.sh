#!/bin/bash

# Exit on error
set -e

# Set Python path to include the dialogchain package
export PYTHONPATH=$PYTHONPATH:/home/tom/github/dialogchain/python/src

# Function to check if a command exists
command_exists() {
    command -v "$1" >/dev/null 2>&1
}

# Function to start MQTT broker
start_mqtt_broker() {
    if ! command_exists mosquitto; then
        echo "Mosquitto MQTT broker is not installed. Please install it first."
        exit 1
    fi
    
    # Check if mosquitto is already running
    if ! pgrep -x "mosquitto" > /dev/null; then
        echo "Starting MQTT broker..."
        mosquitto -c /etc/mosquitto/mosquitto.conf &
        MQTT_PID=$!
        # Give it a moment to start
        sleep 2
    else
        echo "MQTT broker is already running."
        MQTT_PID=""
    fi
}

# Function to stop MQTT broker
stop_mqtt_broker() {
    if [ ! -z "$MQTT_PID" ]; then
        echo "Stopping MQTT broker..."
        kill $MQTT_PID
    fi
}

# Function to start HTTP server
start_http_server() {
    echo "Starting HTTP server..."
    cd /home/tom/github/dialogchain/endpoints/http/docker
    python app.py &
    HTTP_PID=$!
    # Give it a moment to start
    sleep 2
}

# Function to stop HTTP server
stop_http_server() {
    if [ ! -z "$HTTP_PID" ]; then
        echo "Stopping HTTP server..."
        kill $HTTP_PID
    fi
}

# Main execution
main() {
    # Start MQTT broker if not already running
    start_mqtt_broker
    
    # Start HTTP server
    start_http_server
    
    # Run the tests
    echo "Running integration tests..."
    cd /home/tom/github/dialogchain
    
    # Run HTTP tests
    echo "\n=== Running HTTP Tests ==="
    pytest -v tests/integration/http/
    
    # Run MQTT tests
    echo "\n=== Running MQTT Tests ==="
    pytest -v tests/integration/mqtt/
    
    # Clean up
    stop_http_server
    stop_mqtt_broker
    
    echo "\n=== All tests completed ==="
}

# Run the main function
main "$@"
