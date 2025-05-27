#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Test APILama Service

This script tests that the APILama service can start correctly.
"""

import os
import sys
import time
import requests
import subprocess
import signal
import atexit

# Configuration
API_PORT = 8080  # This should match what's in the README
API_HOST = '127.0.0.1'

# Process tracking
process = None


def cleanup():
    """Clean up the started process."""
    global process
    print("\nCleaning up...")
    if process and process.poll() is None:  # Process is still running
        print("Stopping APILama...")
        try:
            process.terminate()
            process.wait(timeout=5)
        except subprocess.TimeoutExpired:
            print("Killing APILama...")
            process.kill()


# Register the cleanup function to be called on exit
atexit.register(cleanup)


def main():
    """Main function."""
    global process
    try:
        # Start the APILama service
        print("Starting APILama service...")
        env = os.environ.copy()
        env['PORT'] = str(API_PORT)
        env['HOST'] = API_HOST
        
        # Use a more explicit command with arguments
        process = subprocess.Popen(
            ["python", "-m", "apilama.app", "--port", str(API_PORT), "--host", API_HOST],
            cwd="apilama",
            env=env,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
            shell=False
        )
        
        # Wait for the service to start
        print("Waiting for APILama to start...")
        time.sleep(3)  # Give it a bit more time to start
        
        # Check if the process is still running
        if process.poll() is not None:
            print(f"Process exited with code {process.returncode}")
            stdout_data = process.stdout.read() if process.stdout else ""
            stderr_data = process.stderr.read() if process.stderr else ""
            if stdout_data:
                print(f"\nStdout:\n{stdout_data}")
            if stderr_data:
                print(f"\nStderr:\n{stderr_data}")
            return
        
        # Try to read some output without blocking indefinitely
        stdout_data, stderr_data = "", ""
        if process.stdout:
            stdout_data = process.stdout.read(1024)  # Read up to 1KB
        if process.stderr:
            stderr_data = process.stderr.read(1024)  # Read up to 1KB
        if stdout_data:
            print(f"\nStdout:\n{stdout_data}")
        if stderr_data:
            print(f"\nStderr:\n{stderr_data}")
        
        # Check if the service is running
        try:
            response = requests.get(f"http://{API_HOST}:{API_PORT}/api/health")
            print(f"\nAPILama health check: {response.status_code} {response.json()}")
            
            # Check the SheLLama service health
            response = requests.get(f"http://{API_HOST}:{API_PORT}/api/shellama/health")
            print(f"SheLLama health check: {response.status_code} {response.json()}")
            
            print("\nTest successful!")
        except requests.exceptions.ConnectionError as e:
            print(f"\nFailed to connect to APILama: {str(e)}")
    except Exception as e:
        print(f"\nError: {str(e)}")
    finally:
        cleanup()


if __name__ == "__main__":
    main()
