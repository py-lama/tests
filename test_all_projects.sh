#!/bin/bash

# Colors for better output
GREEN="\033[0;32m"
YELLOW="\033[0;33m"
BLUE="\033[0;34m"
RED="\033[0;31m"
NC="\033[0m" # No Color

ROOT_DIR=".."
PROJECTS=("getllm" "devlama" "loglama" "apilama" "bexy" "shellama" "weblama" "jsbox" "jslama")

echo -e "${BLUE}Testing all PyLama projects${NC}\n"

for project in "${PROJECTS[@]}"; do
    echo -e "\n${YELLOW}Testing $project...${NC}"
    
    # Check if project directory exists
    if [ ! -d "$ROOT_DIR/$project" ]; then
        echo -e "${RED}Error: Project directory $ROOT_DIR/$project not found${NC}"
        continue
    fi
    
    # Check if project has tests
    if [ -d "$ROOT_DIR/$project/tests" ]; then
        echo -e "${BLUE}Running tests for $project...${NC}"
        cd "$ROOT_DIR/$project"
        
        # Check if project has a pytest.ini file
        if [ -f "pytest.ini" ]; then
            python -m pytest
        # Check if project has a pyproject.toml file
        elif [ -f "pyproject.toml" ]; then
            # Check if poetry is used
            if grep -q "\[tool.poetry\]" pyproject.toml; then
                echo "Using poetry for testing"
                poetry run pytest
            else
                python -m pytest
            fi
        # Check if project has a package.json file (for JS projects)
        elif [ -f "package.json" ]; then
            echo "Using npm for testing"
            npm test
        else
            echo -e "${YELLOW}No test configuration found for $project${NC}"
        fi
        
        cd "$OLDPWD"
    else
        echo -e "${YELLOW}No tests directory found for $project${NC}"
    fi
    
    echo -e "${GREEN}Finished testing $project${NC}"
done

echo -e "\n${GREEN}All tests completed${NC}"
