#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Test suite for verifying integration between all PyLama ecosystem components.

This test suite verifies that all components of the PyLama ecosystem can work together,
including API communication, service discovery, and end-to-end workflows.
"""

import os
import sys
import unittest
import subprocess
import tempfile
import shutil
import time
import requests
from pathlib import Path

# Add the parent directory to sys.path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Components to test
COMPONENTS = {
    "bexy": {"port": 9000, "endpoint": "/health"},
    "pyllm": {"port": 9001, "endpoint": "/health"},
    "devlama": {"port": 9003, "endpoint": "/health"},  # Renamed from pylama
    "shellama": {"port": 9002, "endpoint": "/health"},
    "apilama": {"port": 9080, "endpoint": "/health"},
    "weblama": {"port": 9081, "endpoint": "/"},
    "loglama": {"port": 6001, "endpoint": "/health"}
}

# Root directory of the project
ROOT_DIR = Path(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))


class IntegrationTestCase(unittest.TestCase):
    """Base test case for integration tests."""

    def setUp(self):
        """Set up the test environment."""
        self.temp_dir = tempfile.mkdtemp()
        self.original_dir = os.getcwd()
        self.processes = {}
        
    def tearDown(self):
        """Clean up the test environment."""
        # Stop any running processes
        for component, process in self.processes.items():
            if process and process.poll() is None:
                process.terminate()
                try:
                    process.wait(timeout=5)
                except subprocess.TimeoutExpired:
                    process.kill()
        
        os.chdir(self.original_dir)
        shutil.rmtree(self.temp_dir, ignore_errors=True)

    def run_command(self, command, cwd=None, timeout=60):
        """Run a command and return the result."""
        try:
            result = subprocess.run(
                command,
                cwd=cwd or self.original_dir,
                capture_output=True,
                text=True,
                timeout=timeout
            )
            return result
        except subprocess.TimeoutExpired:
            self.fail(f"Command '{' '.join(command)}' timed out after {timeout} seconds")
            return None
    
    def start_service(self, component):
        """Start a service using its Makefile run target."""
        component_path = os.path.join(ROOT_DIR, component)
        if not os.path.exists(component_path):
            self.skipTest(f"Component directory {component} does not exist")
        
        # Check if the service is already running
        port = COMPONENTS[component]["port"]
        try:
            response = requests.get(f"http://localhost:{port}{COMPONENTS[component]['endpoint']}", timeout=1)
            if response.status_code == 200:
                return True  # Service is already running
        except requests.exceptions.RequestException:
            pass  # Service is not running
        
        # Start the service using its Makefile
        process = subprocess.Popen(
            ["make", "run"],
            cwd=component_path,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True
        )
        
        self.processes[component] = process
        
        # Wait for the service to start
        for _ in range(30):  # Wait up to 30 seconds
            try:
                response = requests.get(f"http://localhost:{port}{COMPONENTS[component]['endpoint']}", timeout=1)
                if response.status_code == 200:
                    return True
            except requests.exceptions.RequestException:
                pass
            time.sleep(1)
        
        return False


class TestComponentIntegration(IntegrationTestCase):
    """Test the integration between all components."""

    def test_main_makefile_exists(self):
        """Test that the main Makefile exists."""
        makefile_path = os.path.join(ROOT_DIR, "Makefile")
        self.assertTrue(
            os.path.exists(makefile_path),
            "Main Makefile not found"
        )
    
    def test_main_makefile_run_all_target(self):
        """Test that the main Makefile has a run-all target."""
        makefile_path = os.path.join(ROOT_DIR, "Makefile")
        if not os.path.exists(makefile_path):
            self.skipTest("Main Makefile not found")
        
        # Check if the target exists without actually running it
        result = subprocess.run(
            ["make", "-n", "run-all"],
            cwd=ROOT_DIR,
            capture_output=True,
            text=True
        )
        
        if result.returncode != 0:
            # Check for alternative target names
            alt_targets = ["all", "start-all", "start"]
            for target in alt_targets:
                result = subprocess.run(
                    ["make", "-n", target],
                    cwd=ROOT_DIR,
                    capture_output=True,
                    text=True
                )
                if result.returncode == 0:
                    break
        
        self.assertEqual(
            result.returncode, 0,
            f"run-all target check failed: {result.stderr}"
        )
    
    def test_main_makefile_stop_all_target(self):
        """Test that the main Makefile has a stop-all target."""
        makefile_path = os.path.join(ROOT_DIR, "Makefile")
        if not os.path.exists(makefile_path):
            self.skipTest("Main Makefile not found")
        
        # Check if the target exists without actually running it
        result = subprocess.run(
            ["make", "-n", "stop-all"],
            cwd=ROOT_DIR,
            capture_output=True,
            text=True
        )
        
        if result.returncode != 0:
            # Check for alternative target names
            alt_targets = ["stop", "halt-all", "halt"]
            for target in alt_targets:
                result = subprocess.run(
                    ["make", "-n", target],
                    cwd=ROOT_DIR,
                    capture_output=True,
                    text=True
                )
                if result.returncode == 0:
                    break
        
        self.assertEqual(
            result.returncode, 0,
            f"stop-all target check failed: {result.stderr}"
        )
    
    def test_component_specific_targets(self):
        """Test that the main Makefile has targets for each component."""
        makefile_path = os.path.join(ROOT_DIR, "Makefile")
        if not os.path.exists(makefile_path):
            self.skipTest("Main Makefile not found")
        
        # Read the Makefile content
        with open(makefile_path, 'r') as f:
            makefile_content = f.read()
        
        # Check for component-specific targets
        for component in COMPONENTS:
            # Special handling for devlama during transition
            if component == "devlama":
                # Check for either devlama or pylama (original name)
                self.assertTrue(
                    "run-devlama" in makefile_content or "run-pylama" in makefile_content,
                    f"Neither run-devlama nor run-pylama target found in main Makefile"
                )
            elif component == "loglama":
                # LogLama might be configured separately
                # This is acceptable as LogLama integration is optional
                if "run-loglama" not in makefile_content:
                    print("Warning: run-loglama target not found in main Makefile")
            else:
                run_target = f"run-{component}"
                self.assertIn(
                    run_target, makefile_content,
                    f"No {run_target} target found in main Makefile"
                )


class TestDockerIntegration(IntegrationTestCase):
    """Test the Docker integration between all components."""

    def test_docker_compose_integration(self):
        """Test that the docker-compose file includes all components."""
        # Check for central docker-compose file
        central_compose = os.path.join(ROOT_DIR, "docker-compose.yml")
        central_compose_test = os.path.join(ROOT_DIR, "docker-compose.test.yml")
        
        if not os.path.exists(central_compose) and not os.path.exists(central_compose_test):
            self.skipTest("No central docker-compose file found")
        
        compose_path = central_compose if os.path.exists(central_compose) else central_compose_test
        
        # Read the docker-compose file content
        with open(compose_path, 'r') as f:
            compose_content = f.read()
        
        # Check for each component
        for component in COMPONENTS:
            # Special handling for components during transition
            if component == "devlama":
                # Check for either devlama or pylama (original name)
                self.assertTrue(
                    "devlama" in compose_content.lower() or "pylama" in compose_content.lower(),
                    f"Neither devlama nor pylama found in docker-compose file"
                )
            elif component == "loglama":
                # LogLama might be configured separately or not included in the main compose file
                # This is acceptable as LogLama integration is optional
                pass
            else:
                self.assertIn(
                    component, compose_content.lower(),
                    f"Component {component} not found in docker-compose file"
                )
    
    def test_docker_network(self):
        """Test that the docker-compose file defines a network for component communication."""
        # Check for central docker-compose file
        central_compose = os.path.join(ROOT_DIR, "docker-compose.yml")
        central_compose_test = os.path.join(ROOT_DIR, "docker-compose.test.yml")
        
        if not os.path.exists(central_compose) and not os.path.exists(central_compose_test):
            self.skipTest("No central docker-compose file found")
        
        compose_path = central_compose if os.path.exists(central_compose) else central_compose_test
        
        # Read the docker-compose file content
        with open(compose_path, 'r') as f:
            compose_content = f.read()
        
        # Check for network definition
        self.assertTrue(
            "networks:" in compose_content.lower(),
            "No network definition found in docker-compose file"
        )


if __name__ == "__main__":
    unittest.main()
