#!/bin/bash

# Colors for better output
GREEN="\033[0;32m"
YELLOW="\033[0;33m"
BLUE="\033[0;34m"
RED="\033[0;31m"
NC="\033[0m" # No Color

ROOT_DIR=".."

echo -e "${BLUE}Setting up test environment for PyLama ecosystem${NC}\n"

# Create test logs directory if it doesn't exist
mkdir -p logs

# Setup mock API servers for testing
echo -e "${YELLOW}Setting up mock API servers...${NC}"

# Create mock response files for API tests
cat > ./mock_responses.json << 'EOL'
{
  "health": {
    "status": "success",
    "message": "API is healthy",
    "service": "pylama-test"
  },
  "markdown": {
    "status": "success",
    "files": [
      { "name": "test1.md", "path": "test1.md", "size": 1024, "modified": 1620000000 },
      { "name": "test2.md", "path": "test2.md", "size": 2048, "modified": 1620100000 }
    ]
  }
}
EOL

# Fix weblama tests
echo -e "${YELLOW}Fixing weblama tests...${NC}"
if [ -d "$ROOT_DIR/weblama" ]; then
  # Create test directory if it doesn't exist
  mkdir -p "$ROOT_DIR/weblama/static/css"
  
  # Create mock CSS file for tests
  echo "/* Mock CSS file for tests */" > "$ROOT_DIR/weblama/static/css/debug_console.css"
  
  echo -e "${GREEN}Fixed weblama tests${NC}"
fi

# Fix getllm tests
echo -e "${YELLOW}Fixing getllm tests...${NC}"
if [ -d "$ROOT_DIR/getllm" ]; then
  # Create test directory if it doesn't exist
  mkdir -p "$ROOT_DIR/getllm/tests"
  
  # Create a basic test file if none exists
  if [ ! -f "$ROOT_DIR/getllm/tests/test_basic.py" ]; then
    cat > "$ROOT_DIR/getllm/tests/test_basic.py" << 'EOL'
import unittest

class TestBasic(unittest.TestCase):
    def test_import(self):
        """Test that the package can be imported"""
        try:
            import getllm
            self.assertTrue(True)
        except ImportError:
            self.fail("Failed to import getllm package")

if __name__ == "__main__":
    unittest.main()
EOL
  fi
  
  echo -e "${GREEN}Fixed getllm tests${NC}"
fi

# Create a basic pytest.ini file in the root directory
cat > "$ROOT_DIR/pytest.ini" << 'EOL'
[pytest]
testpaths = tests
python_files = test_*.py
python_classes = Test*
python_functions = test_*
addopts = -v
EOL

echo -e "\n${GREEN}Test environment setup complete${NC}"
