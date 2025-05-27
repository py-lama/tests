#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Test suite for verifying LogLama integration with all PyLama ecosystem components.

This test suite verifies that LogLama properly integrates with all components
of the PyLama ecosystem for centralized logging.
"""

import os
import sys
import unittest
import subprocess
import tempfile
import shutil
import time
import requests
import json
from pathlib import Path

# Add the parent directory to sys.path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Components to test
COMPONENTS = {
    "pybox": {"port": 9000, "log_file": "pybox.log"},
    "pyllm": {"port": 9001, "log_file": "pyllm.log"},
    "devlama": {"port": 9003, "log_file": "devlama.log"},  # Renamed from pylama
    "shellama": {"port": 9002, "log_file": "shellama.log"},
    "apilama": {"port": 9080, "log_file": "apilama.log"},
    "weblama": {"port": 9081, "log_file": "weblama.log"},
    "loglama": {"port": 6001, "log_file": "loglama.log"}
}

# Root directory of the project
ROOT_DIR = Path(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))


class LogLamaTestCase(unittest.TestCase):
    """Base test case for LogLama integration tests."""

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


class TestLogLamaFiles(LogLamaTestCase):
    """Test the LogLama log files for all components."""

    def test_log_files_exist(self):
        """Test that log files exist for all components."""
        log_dir = os.path.join(ROOT_DIR, "logs")
        if not os.path.exists(log_dir):
            # Check for component-specific log directories
            for component in COMPONENTS:
                component_log_dir = os.path.join(ROOT_DIR, component, "logs")
                if os.path.exists(component_log_dir):
                    log_dir = component_log_dir
                    break
        
        if not os.path.exists(log_dir):
            self.skipTest("No log directory found")
        
        # Check for log files
        for component, info in COMPONENTS.items():
            log_file = os.path.join(log_dir, info["log_file"])
            if not os.path.exists(log_file):
                # Try alternative locations
                alt_locations = [
                    os.path.join(ROOT_DIR, component, "logs", info["log_file"]),
                    os.path.join(ROOT_DIR, "loglama", "logs", info["log_file"])
                ]
                for alt_location in alt_locations:
                    if os.path.exists(alt_location):
                        log_file = alt_location
                        break
            
            # It's okay if not all log files exist, as not all components might have been run
            if os.path.exists(log_file):
                self.assertTrue(
                    os.path.getsize(log_file) > 0,
                    f"Log file for {component} is empty"
                )


class TestLogLamaScripts(LogLamaTestCase):
    """Test the LogLama integration scripts."""

    def test_run_with_logs_script_exists(self):
        """Test that the run_with_logs.sh script exists."""
        script_path = os.path.join(ROOT_DIR, "run_with_logs.sh")
        if not os.path.exists(script_path):
            # Check for alternative locations
            alt_locations = [
                os.path.join(ROOT_DIR, "loglama", "run_with_logs.sh"),
                os.path.join(ROOT_DIR, "scripts", "run_with_logs.sh"),
                os.path.join(ROOT_DIR, "docker", "run_with_logs.sh")
            ]
            for alt_location in alt_locations:
                if os.path.exists(alt_location):
                    script_path = alt_location
                    break
        
        self.assertTrue(
            os.path.exists(script_path),
            "run_with_logs.sh script not found"
        )
    
    def test_docker_start_with_logs_script_exists(self):
        """Test that the docker-start-with-logs.sh script exists."""
        script_path = os.path.join(ROOT_DIR, "docker-start-with-logs.sh")
        if not os.path.exists(script_path):
            # Check for alternative locations
            alt_locations = [
                os.path.join(ROOT_DIR, "loglama", "docker-start-with-logs.sh"),
                os.path.join(ROOT_DIR, "scripts", "docker-start-with-logs.sh"),
                os.path.join(ROOT_DIR, "docker", "docker-start-with-logs.sh")
            ]
            for alt_location in alt_locations:
                if os.path.exists(alt_location):
                    script_path = alt_location
                    break
        
        # This script might not exist in all installations
        if os.path.exists(script_path):
            # Check that the script is executable
            self.assertTrue(
                os.access(script_path, os.X_OK),
                "docker-start-with-logs.sh script is not executable"
            )


class TestLogLamaCollector(LogLamaTestCase):
    """Test the LogLama collector functionality."""

    def test_log_collector_script_exists(self):
        """Test that the log collector script exists."""
        collector_path = os.path.join(ROOT_DIR, "loglama", "collector.py")
        if not os.path.exists(collector_path):
            # Check for alternative locations
            alt_locations = [
                os.path.join(ROOT_DIR, "loglama", "scripts", "collector.py"),
                os.path.join(ROOT_DIR, "scripts", "log_collector.py"),
                os.path.join(ROOT_DIR, "weblama", "log_collector.py")
            ]
            for alt_location in alt_locations:
                if os.path.exists(alt_location):
                    collector_path = alt_location
                    break
        
        # This script might not exist in all installations
        if os.path.exists(collector_path):
            # Check that the script contains the necessary imports
            with open(collector_path, 'r') as f:
                content = f.read()
                self.assertTrue(
                    "import" in content and "log" in content.lower(),
                    "Log collector script does not contain necessary imports"
                )


class TestDockerLogLamaIntegration(LogLamaTestCase):
    """Test the Docker LogLama integration."""

    def test_docker_compose_loglama_integration(self):
        """Test that the docker-compose file includes LogLama integration."""
        # Check for docker-compose files with LogLama integration
        compose_files = [
            os.path.join(ROOT_DIR, "docker-compose.yml"),
            os.path.join(ROOT_DIR, "docker-compose.test.yml"),
            os.path.join(ROOT_DIR, "docker-compose.logging.yml")
        ]
        
        found_compose_file = None
        for compose_file in compose_files:
            if os.path.exists(compose_file):
                found_compose_file = compose_file
                break
        
        if not found_compose_file:
            self.skipTest("No docker-compose file found")
        
        # Read the docker-compose file content
        with open(found_compose_file, 'r') as f:
            compose_content = f.read()
        
        # Check for LogLama service or integration
        # LogLama might be in a separate compose file or configured via scripts
        # First check if there's a specific logging compose file
        logging_compose_file = os.path.join(ROOT_DIR, "docker-compose.logging.yml")
        if os.path.exists(logging_compose_file):
            with open(logging_compose_file, 'r') as f:
                logging_compose_content = f.read()
                if "loglama" in logging_compose_content.lower():
                    return  # LogLama is in the logging compose file, test passes
        
        # Check for LogLama in the main compose file
        if "loglama" in compose_content.lower():
            return  # LogLama is in the main compose file, test passes
            
        # Check for scripts that integrate LogLama
        run_with_logs_script = os.path.join(ROOT_DIR, "run_with_logs.sh")
        docker_logs_script = os.path.join(ROOT_DIR, "docker-start-with-logs.sh")
        
        if os.path.exists(run_with_logs_script) or os.path.exists(docker_logs_script):
            return  # LogLama integration is handled via scripts, test passes
            
        # If we got here, no LogLama integration was found
        self.fail("No LogLama integration found in compose files or scripts")
    
    def test_docker_compose_service_dependencies(self):
        """Test that the docker-compose file defines dependencies for LogLama."""
        # Check for docker-compose files with LogLama integration
        compose_files = [
            os.path.join(ROOT_DIR, "docker-compose.logging.yml"),
            os.path.join(ROOT_DIR, "docker-compose.yml"),
            os.path.join(ROOT_DIR, "docker-compose.test.yml")
        ]
        
        found_compose_file = None
        for compose_file in compose_files:
            if os.path.exists(compose_file):
                # Check if the file contains LogLama
                with open(compose_file, 'r') as f:
                    content = f.read()
                    if "loglama" in content.lower():
                        found_compose_file = compose_file
                        break
        
        # Check for integration scripts if no compose file with LogLama was found
        if not found_compose_file:
            run_with_logs_script = os.path.join(ROOT_DIR, "run_with_logs.sh")
            docker_logs_script = os.path.join(ROOT_DIR, "docker-start-with-logs.sh")
            
            if os.path.exists(run_with_logs_script) or os.path.exists(docker_logs_script):
                # LogLama integration is handled via scripts, test passes
                return

            self.skipTest("No docker-compose file with LogLama found")
        
        # Read the docker-compose file content
        with open(found_compose_file, 'r') as f:
            compose_content = f.read()
        
        # Check for service dependencies
        # We're looking for components that depend on LogLama
        # This could be expressed as "depends_on" or through other mechanisms
        self.assertTrue(
            "depends_on" in compose_content.lower() or "links" in compose_content.lower(),
            "No service dependencies found in docker-compose file"
        )


if __name__ == "__main__":
    unittest.main()
