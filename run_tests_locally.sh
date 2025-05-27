#!/bin/bash
set -e

# Configuration
REPO_URL="${REPO_URL:-$(git remote get-url origin 2>/dev/null || echo "https://github.com/dialogchain/python.git")}"
BRANCH="${BRANCH:-$(git branch --show-current 2>/dev/null || echo "main")}"
MAKE_TARGETS="${MAKE_TARGETS:-help deps test}"
PYTHON_DEPS="${PYTHON_DEPS:-pytest coverage}"
SYSTEM_DEPS="${SYSTEM_DEPS:-}"

# Build the Docker image
echo "Building Docker image..."
cd tests && docker build -f Dockerfile -t make-test-env .

# Run the tests
echo "Running tests..."
docker run --rm -it \
  -e "REPO_URL=$REPO_URL" \
  -e "BRANCH=$BRANCH" \
  -e "MAKE_TARGETS=$MAKE_TARGETS" \
  -e "PYTHON_DEPS=$PYTHON_DEPS" \
  -e "SYSTEM_DEPS=$SYSTEM_DEPS" \
  -v "$(pwd):/home/testuser/app" \
  make-test-env

echo "Tests completed successfully!"
