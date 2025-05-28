#!/bin/bash

# Test script for WebLama microservices deployment
echo "Starting WebLama microservices test..."

# Check if Docker is running
if ! docker info > /dev/null 2>&1; then
  echo "Error: Docker is not running or not installed."
  exit 1
fi

# Build and start the services
echo "Building and starting services..."
docker-compose up -d --build

# Wait for services to start
echo "Waiting for services to start..."
sleep 10

# Test BEXY API
echo "\nTesting BEXY API..."
BEXY_HEALTH=$(curl -s http://localhost:8000/health)
if [[ $BEXY_HEALTH == *"healthy"* ]]; then
  echo "✅ BEXY API is running"
else
  echo "❌ BEXY API is not responding correctly"
fi

# Test PyLLM API
echo "\nTesting PyLLM API..."
GETLLM_HEALTH=$(curl -s http://localhost:8001/health)
if [[ $GETLLM_HEALTH == *"healthy"* ]]; then
  echo "✅ PyLLM API is running"
else
  echo "❌ PyLLM API is not responding correctly"
fi

# Test PyLama API
echo "\nTesting PyLama API..."
DEVLAMA_HEALTH=$(curl -s http://localhost:8002/health)
if [[ $DEVLAMA_HEALTH == *"healthy"* ]]; then
  echo "✅ PyLama API is running"
else
  echo "❌ PyLama API is not responding correctly"
fi

# Test WebLama Web App
echo "\nTesting WebLama Web App..."
WEBLAMA_RESPONSE=$(curl -s http://localhost:5000/)
if [[ $WEBLAMA_RESPONSE == *"WebLama"* ]]; then
  echo "✅ WebLama Web App is running"
else
  echo "❌ WebLama Web App is not responding correctly"
fi

echo "\nTest complete. You can access the WebLama UI at http://localhost:5000"
echo "To stop the services, run: docker-compose down"
