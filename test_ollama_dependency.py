#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Test script for verifying the Ollama dependency handling in getllm.
"""

import sys
import os
import subprocess
import tempfile
import shutil
import argparse

def test_ollama_installed():
    """Test if Ollama is installed on the system."""
    try:
        # Use which command to check if Ollama is in PATH
        if os.name == 'nt':  # Windows
            which_cmd = 'where'
        else:  # Unix/Linux/MacOS
            which_cmd = 'which'
            
        result = subprocess.run(
            [which_cmd, 'ollama'],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
            check=False
        )
        
        return result.returncode == 0
    except Exception:
        return False

def run_getllm_command(cmd, env=None):
    """Run a getllm command and return the output."""
    try:
        result = subprocess.run(
            cmd,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
            check=False,
            env=env
        )
        return {
            'returncode': result.returncode,
            'stdout': result.stdout,
            'stderr': result.stderr
        }
    except Exception as e:
        return {
            'returncode': -1,
            'stdout': '',
            'stderr': str(e)
        }

def test_ollama_dependency_handling():
    """Test how getllm handles the Ollama dependency."""
    print("\n=== Testing Ollama Dependency Handling ===")
    
    # Check if Ollama is installed
    ollama_installed = test_ollama_installed()
    print(f"Ollama installed: {ollama_installed}")
    
    # Create a temporary directory for testing
    temp_dir = tempfile.mkdtemp()
    print(f"Created temporary directory: {temp_dir}")
    
    try:
        # Create a modified PATH that doesn't include Ollama
        env = os.environ.copy()
        if ollama_installed:
            # If Ollama is installed, modify PATH to exclude it
            ollama_path = subprocess.run(
                ['which', 'ollama'],
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True,
                check=False
            ).stdout.strip()
            
            ollama_dir = os.path.dirname(ollama_path)
            env['PATH'] = ':'.join([p for p in env['PATH'].split(':') if p != ollama_dir])
            print(f"Modified PATH to exclude Ollama directory: {ollama_dir}")
        
        # Test 1: Run getllm --search without Ollama
        print("\nTest 1: Running 'getllm --search bielik' without Ollama")
        result = run_getllm_command(['getllm', '--search', 'bielik'], env=env)
        
        # Check if the error message about Ollama not being installed is present
        if "Ollama is not installed" in result['stdout'] or "Ollama is not installed" in result['stderr']:
            print("✅ Test 1 PASSED: Error message about Ollama not being installed is displayed")
        else:
            print("❌ Test 1 FAILED: Error message about Ollama not being installed is not displayed")
            print(f"Output: {result['stdout']}")
            print(f"Error: {result['stderr']}")
        
        # Test 2: Run getllm --mock --search
        print("\nTest 2: Running 'getllm --mock --search bielik'")
        result = run_getllm_command(['getllm', '--mock', '--search', 'bielik'], env=env)
        
        # Check if mock mode works without Ollama
        if "Using mock mode" in result['stdout'] or result['returncode'] == 0:
            print("✅ Test 2 PASSED: Mock mode works without Ollama")
        else:
            print("❌ Test 2 FAILED: Mock mode doesn't work without Ollama")
            print(f"Output: {result['stdout']}")
            print(f"Error: {result['stderr']}")
        
    finally:
        # Clean up the temporary directory
        shutil.rmtree(temp_dir)
        print(f"Removed temporary directory: {temp_dir}")

def main():
    """Main entry point for the test script."""
    parser = argparse.ArgumentParser(description="Test Ollama dependency handling in getllm")
    args = parser.parse_args()
    
    test_ollama_dependency_handling()
    
    return 0

if __name__ == "__main__":
    sys.exit(main())
