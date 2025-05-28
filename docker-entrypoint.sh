#!/bin/bash
set -e

# Function to check if Ollama is running
check_ollama() {
    if command -v ollama >/dev/null 2>&1; then
        echo "Ollama is installed"
        # Try to start ollama server if not already running
        ollama serve &>/dev/null &
        echo "Started Ollama server"
    else
        echo "WARNING: Ollama is not installed. Some tests may fail."
    fi
}

# Function to run tests with pytest
run_pytest() {
    echo "Running tests with pytest..."
    pytest "$@"
}

# Function to run tests with tox
run_tox() {
    echo "Running tests with tox..."
    tox "$@"
}

# Function to run Ansible playbook tests
run_ansible_tests() {
    echo "Running Ansible playbook tests..."
    cd /app/tests/ansible
    ansible-playbook test_getllm.yml -v
}

# Function to run CLI tests
run_cli_tests() {
    echo "Running CLI tests..."
    
    echo "Testing --help:"
    getllm --help
    
    echo "Testing list command:"
    getllm list
    
    echo "Testing search command:"
    getllm --search llama 2>&1 | tee /tmp/search_output.log
    
    echo "Testing version:"
    getllm --version 2>&1 || echo "Version flag not supported"
    
    echo "CLI tests completed"
}

# Main execution
case "$1" in
    pytest)
        shift
        run_pytest "$@"
        ;;
    tox)
        shift
        run_tox "$@"
        ;;
    ansible)
        run_ansible_tests
        ;;
    cli)
        check_ollama
        run_cli_tests
        ;;
    shell)
        exec /bin/bash
        ;;
    *)
        # Default: run all tests
        check_ollama
        run_pytest
        run_cli_tests
        echo "All tests completed"
        ;;
esac
