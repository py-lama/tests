#!/bin/bash

# Colors for better output
GREEN="\033[0;32m"
YELLOW="\033[0;33m"
BLUE="\033[0;34m"
RED="\033[0;31m"
NC="\033[0m" # No Color

ROOT_DIR=".."
JS_PROJECTS=("weblama" "jsbox" "jslama")

echo -e "${BLUE}Installing dependencies for JavaScript projects...${NC}\n"

for project in "${JS_PROJECTS[@]}"; do
  echo -e "${YELLOW}Installing dependencies for $project...${NC}"
  
  # Check if project directory exists
  if [ ! -d "$ROOT_DIR/$project" ]; then
    echo -e "${RED}Error: Project directory $ROOT_DIR/$project not found${NC}"
    continue
  fi
  
  # Check if package.json exists
  if [ ! -f "$ROOT_DIR/$project/package.json" ]; then
    echo -e "${RED}Error: package.json not found in $ROOT_DIR/$project${NC}"
    continue
  fi
  
  # Install dependencies
  cd "$ROOT_DIR/$project"
  echo -e "${BLUE}Running npm install...${NC}"
  npm install --no-fund --no-audit --loglevel=error
  
  # Install Jest globally if it's not already installed
  if ! command -v jest &> /dev/null; then
    echo -e "${BLUE}Installing Jest globally...${NC}"
    npm install -g jest
  fi
  
  # Add missing dependencies if needed
  echo -e "${BLUE}Adding missing dependencies...${NC}"
  npm install --save-dev jest jsdom cors express body-parser --no-fund --no-audit --loglevel=error
  
  cd - > /dev/null
done

echo -e "\n${GREEN}Dependencies installed successfully!${NC}"
