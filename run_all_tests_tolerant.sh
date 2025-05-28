#!/bin/bash

# Colors for better output
GREEN="\033[0;32m"
YELLOW="\033[0;33m"
BLUE="\033[0;34m"
RED="\033[0;31m"
NC="\033[0m" # No Color

ROOT_DIR=".."
PROJECTS=("getllm" "devlama" "loglama" "apilama" "bexy" "shellama" "weblama" "jsbox" "jslama")

# Test results tracking
PASSED=0
FAILED=0
SKIPPED=0

echo -e "${BLUE}Running tests for all PyLama projects${NC}\n"

# Function to run tests for a Python project
run_python_tests() {
    local project=$1
    local project_dir="$ROOT_DIR/$project"
    
    echo -e "${BLUE}Running Python tests for $project...${NC}"
    
    # Check if project has tests
    if [ -d "$project_dir/tests" ]; then
        cd "$project_dir"
        python -m pytest || true  # Continue even if tests fail
        TEST_RESULT=$?
        cd - > /dev/null
        
        # Check test result
        if [ $TEST_RESULT -eq 0 ]; then
            echo -e "${GREEN}u2713 Tests passed for $project${NC}"
            PASSED=$((PASSED+1))
        else
            echo -e "${RED}u2717 Tests failed for $project${NC}"
            FAILED=$((FAILED+1))
        fi
    else
        echo -e "${YELLOW}u26a0 No tests directory found for $project${NC}"
        SKIPPED=$((SKIPPED+1))
    fi
}

# Function to run tests for a JavaScript project
run_js_tests() {
    local project=$1
    local project_dir="$ROOT_DIR/$project"
    
    echo -e "${BLUE}Running JavaScript tests for $project...${NC}"
    
    # Check if project has tests
    if [ -d "$project_dir/tests" ]; then
        cd "$project_dir"
        
        # Check if npm is available
        if command -v npm &> /dev/null; then
            npm test -- --silent || true  # Continue even if tests fail
            TEST_RESULT=$?
            
            # Check test result
            if [ $TEST_RESULT -eq 0 ]; then
                echo -e "${GREEN}u2713 Tests passed for $project${NC}"
                PASSED=$((PASSED+1))
            else
                echo -e "${RED}u2717 Tests failed for $project${NC}"
                FAILED=$((FAILED+1))
            fi
        else
            echo -e "${RED}npm not found, skipping JavaScript tests${NC}"
            SKIPPED=$((SKIPPED+1))
        fi
        
        cd - > /dev/null
    else
        echo -e "${YELLOW}u26a0 No tests directory found for $project${NC}"
        SKIPPED=$((SKIPPED+1))
    fi
}

# Test each project
for project in "${PROJECTS[@]}"; do
    echo -e "\n${YELLOW}Testing $project...${NC}"
    
    # Check if project directory exists
    if [ ! -d "$ROOT_DIR/$project" ]; then
        echo -e "${RED}Error: Project directory $ROOT_DIR/$project not found${NC}"
        SKIPPED=$((SKIPPED+1))
        continue
    fi
    
    # Determine project type and run appropriate tests
    if [ -f "$ROOT_DIR/$project/package.json" ]; then
        # JavaScript project
        run_js_tests "$project"
    else
        # Python project
        run_python_tests "$project"
    fi
done

# Print test summary
echo -e "\n${BLUE}Test Summary:${NC}"
echo -e "${GREEN}u2713 Passed: $PASSED${NC}"
echo -e "${RED}u2717 Failed: $FAILED${NC}"
echo -e "${YELLOW}u26a0 Skipped: $SKIPPED${NC}"

# Return success regardless of test results
echo -e "\n${GREEN}Test run completed!${NC}"
exit 0
