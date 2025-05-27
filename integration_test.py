#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
PyLama Ecosystem Integration Test

This script tests the integration between the different components of the PyLama ecosystem.
"""

import os
import sys
import json
import requests
import time
import subprocess
import signal
import atexit

# Add the necessary paths to import the packages
sys.path.append(os.path.abspath('shellama'))
sys.path.append(os.path.abspath('apilama'))

from shellama import file_ops, dir_ops, shell

# Configuration
API_PORT = 8080
SHELLAMA_PORT = 8002
PYLAMA_PORT = 8003
PYBOX_PORT = 8000
PYLLM_PORT = 8001

# Process tracking
processes = []


def start_service(name, command, cwd=None, env=None):
    """Start a service and return the process."""
    print(f"Starting {name}...")
    
    if env is None:
        env = os.environ.copy()
    
    process = subprocess.Popen(
        command,
        cwd=cwd,
        env=env,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True,
        shell=True
    )
    
    processes.append((name, process))
    return process


def cleanup():
    """Clean up all started processes."""
    print("\nCleaning up...")
    for name, process in processes:
        if process.poll() is None:  # Process is still running
            print(f"Stopping {name}...")
            try:
                process.terminate()
                process.wait(timeout=5)
            except subprocess.TimeoutExpired:
                print(f"Killing {name}...")
                process.kill()


# Register the cleanup function to be called on exit
atexit.register(cleanup)


def test_shellama_directly():
    """Test the SheLLama package directly."""
    print("\n=== Testing SheLLama Package Directly ===")
    
    # Create a test directory
    test_dir = os.path.join(os.getcwd(), 'test_integration')
    print(f"Creating test directory: {test_dir}")
    dir_ops.create_directory(test_dir)
    
    # Create a test file
    test_file = os.path.join(test_dir, 'test.md')
    test_content = "# Test File\n\nThis is a test file created by the integration test."
    print(f"Creating test file: {test_file}")
    file_ops.write_file(test_file, test_content)
    
    # Read the test file
    print(f"Reading test file: {test_file}")
    content = file_ops.read_file(test_file)
    print(f"Content:\n{content}")
    
    # List files in the test directory
    print(f"Listing files in: {test_dir}")
    files = file_ops.list_files(test_dir)
    print(f"Files: {json.dumps(files, indent=2)}")
    
    # Execute a shell command
    print("Executing shell command: ls -la")
    result = shell.execute_command("ls -la", cwd=test_dir)
    print(f"Command result:\n{result['stdout']}")
    
    # Clean up
    print(f"Deleting test file: {test_file}")
    file_ops.delete_file(test_file)
    print(f"Deleting test directory: {test_dir}")
    dir_ops.delete_directory(test_dir)


def test_apilama_shellama_integration():
    """Test the integration between APILama and SheLLama."""
    print("\n=== Testing APILama and SheLLama Integration ===")
    
    # Start the APILama service
    api_env = os.environ.copy()
    api_env['PORT'] = str(API_PORT)
    api_env['HOST'] = '127.0.0.1'
    api_process = start_service(
        "APILama",
        "python -m apilama.app",
        cwd="apilama",
        env=api_env
    )
    
    # Wait for the service to start
    print("Waiting for APILama to start...")
    time.sleep(2)
    
    # Check if the service is running
    try:
        response = requests.get(f"http://127.0.0.1:{API_PORT}/api/health")
        print(f"APILama health check: {response.status_code} {response.json()}")
    except requests.exceptions.ConnectionError:
        print("Failed to connect to APILama")
        return
    
    # Check the SheLLama service health
    try:
        response = requests.get(f"http://127.0.0.1:{API_PORT}/api/shellama/health")
        print(f"SheLLama health check: {response.status_code} {response.json()}")
    except requests.exceptions.ConnectionError:
        print("Failed to connect to SheLLama through APILama")
        return
    
    # Create a test directory through the API
    test_dir = os.path.join(os.getcwd(), 'api_test_integration')
    print(f"Creating test directory through API: {test_dir}")
    response = requests.post(
        f"http://127.0.0.1:{API_PORT}/api/shellama/directory",
        json={"path": test_dir}
    )
    print(f"Create directory response: {response.status_code} {response.json()}")
    
    # Create a test file through the API
    test_file = os.path.join(test_dir, 'api_test.md')
    test_content = "# API Test File\n\nThis is a test file created through the API."
    print(f"Creating test file through API: {test_file}")
    response = requests.post(
        f"http://127.0.0.1:{API_PORT}/api/shellama/file",
        json={"path": test_file, "content": test_content}
    )
    print(f"Create file response: {response.status_code} {response.json()}")
    
    # List files through the API
    print(f"Listing files through API in: {test_dir}")
    response = requests.get(
        f"http://127.0.0.1:{API_PORT}/api/shellama/files",
        params={"directory": test_dir, "pattern": "*.*"}
    )
    print(f"List files response: {response.status_code} {response.json()}")
    
    # Read the test file through the API
    print(f"Reading test file through API: {test_file}")
    response = requests.get(
        f"http://127.0.0.1:{API_PORT}/api/shellama/file",
        params={"filename": test_file}
    )
    print(f"Read file response: {response.status_code} {response.json()}")
    
    # Execute a shell command through the API
    print("Executing shell command through API: ls -la")
    response = requests.post(
        f"http://127.0.0.1:{API_PORT}/api/shellama/shell",
        json={"command": "ls -la", "cwd": test_dir}
    )
    print(f"Execute command response: {response.status_code}")
    print(f"Command output:\n{response.json().get('stdout', '')}")
    
    # Clean up through the API
    print(f"Deleting test file through API: {test_file}")
    response = requests.delete(
        f"http://127.0.0.1:{API_PORT}/api/shellama/file",
        params={"filename": test_file}
    )
    print(f"Delete file response: {response.status_code} {response.json()}")
    
    print(f"Deleting test directory through API: {test_dir}")
    response = requests.delete(
        f"http://127.0.0.1:{API_PORT}/api/shellama/directory",
        params={"directory": test_dir, "recursive": "true"}
    )
    print(f"Delete directory response: {response.status_code} {response.json()}")


def main():
    """Main function."""
    try:
        # Test the SheLLama package directly
        test_shellama_directly()
        
        # Test the integration between APILama and SheLLama
        test_apilama_shellama_integration()
        
        print("\n=== All tests completed successfully ===")
    except Exception as e:
        print(f"\nError: {str(e)}")
    finally:
        cleanup()


if __name__ == "__main__":
    main()
