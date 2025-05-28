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

echo -e "${BLUE}Comprehensive testing of all PyLama projects${NC}\n"

# First run the setup script to ensure the test environment is ready
if [ -f "./setup_test_env.sh" ]; then
    echo -e "${YELLOW}Setting up test environment...${NC}"
    ./setup_test_env.sh
else
    echo -e "${RED}Warning: setup_test_env.sh not found. Some tests may fail.${NC}"
fi

# Function to run tests for a Python project
run_python_tests() {
    local project=$1
    local project_dir="$ROOT_DIR/$project"
    
    echo -e "${BLUE}Running Python tests for $project...${NC}"
    
    # Check if project has a pytest.ini file
    if [ -f "$project_dir/pytest.ini" ]; then
        cd "$project_dir"
        python -m pytest
        TEST_RESULT=$?
        cd - > /dev/null
    # Check if project has a pyproject.toml file
    elif [ -f "$project_dir/pyproject.toml" ]; then
        # Check if poetry is used
        if grep -q "\[tool.poetry\]" "$project_dir/pyproject.toml"; then
            cd "$project_dir"
            if command -v poetry &> /dev/null; then
                poetry run pytest
                TEST_RESULT=$?
            else
                python -m pytest
                TEST_RESULT=$?
            fi
            cd - > /dev/null
        else
            cd "$project_dir"
            python -m pytest
            TEST_RESULT=$?
            cd - > /dev/null
        fi
    else
        cd "$project_dir"
        python -m pytest
        TEST_RESULT=$?
        cd - > /dev/null
    fi
    
    return $TEST_RESULT
}

# Function to run tests for a JavaScript project
run_js_tests() {
    local project=$1
    local project_dir="$ROOT_DIR/$project"
    
    echo -e "${BLUE}Running JavaScript tests for $project...${NC}"
    
    cd "$project_dir"
    
    # Check if npm is available
    if command -v npm &> /dev/null; then
        # Run tests with reduced output to avoid overwhelming logs
        npm test -- --silent
        TEST_RESULT=$?
    else
        echo -e "${RED}npm not found, skipping JavaScript tests${NC}"
        TEST_RESULT=2
    fi
    
    cd - > /dev/null
    return $TEST_RESULT
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
    
    # Check if project has tests
    if [ -d "$ROOT_DIR/$project/tests" ] || [ -d "$ROOT_DIR/$project/test" ]; then
        # Determine project type and run appropriate tests
        if [ -f "$ROOT_DIR/$project/package.json" ]; then
            # JavaScript project
            run_js_tests "$project"
            TEST_RESULT=$?
        else
            # Python project
            run_python_tests "$project"
            TEST_RESULT=$?
        fi
        
        # Check test result
        if [ $TEST_RESULT -eq 0 ]; then
            echo -e "${GREEN}✓ Tests passed for $project${NC}"
            PASSED=$((PASSED+1))
        elif [ $TEST_RESULT -eq 2 ]; then
            echo -e "${YELLOW}⚠ Tests skipped for $project${NC}"
            SKIPPED=$((SKIPPED+1))
        else
            echo -e "${RED}✗ Tests failed for $project${NC}"
            FAILED=$((FAILED+1))
        fi
    else
        echo -e "${YELLOW}⚠ No tests directory found for $project${NC}"
        SKIPPED=$((SKIPPED+1))
    fi
done

# Print test summary
echo -e "\n${BLUE}Test Summary:${NC}"
echo -e "${GREEN}✓ Passed: $PASSED${NC}"
echo -e "${RED}✗ Failed: $FAILED${NC}"
echo -e "${YELLOW}⚠ Skipped: $SKIPPED${NC}"

# Return appropriate exit code
if [ $FAILED -gt 0 ]; then
    echo -e "\n${RED}Some tests failed. Please fix the issues before proceeding.${NC}"
    exit 1
else
    echo -e "\n${GREEN}All executed tests passed successfully!${NC}"
    exit 0
fi
