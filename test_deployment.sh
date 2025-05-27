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

# Test PyBox API
echo "\nTesting PyBox API..."
PYBOX_HEALTH=$(curl -s http://localhost:8000/health)
if [[ $PYBOX_HEALTH == *"healthy"* ]]; then
  echo "✅ PyBox API is running"
else
  echo "❌ PyBox API is not responding correctly"
fi

# Test PyLLM API
echo "\nTesting PyLLM API..."
PYLLM_HEALTH=$(curl -s http://localhost:8001/health)
if [[ $PYLLM_HEALTH == *"healthy"* ]]; then
  echo "✅ PyLLM API is running"
else
  echo "❌ PyLLM API is not responding correctly"
fi

# Test PyLama API
echo "\nTesting PyLama API..."
PYLAMA_HEALTH=$(curl -s http://localhost:8002/health)
if [[ $PYLAMA_HEALTH == *"healthy"* ]]; then
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
