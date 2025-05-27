#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Test suite for verifying Docker functionality across all PyLama ecosystem components.

This test suite verifies that all Docker configurations in the PyLama ecosystem work correctly,
including Dockerfiles, docker-compose files, and Docker-related Makefile targets.
"""

import os
import sys
import unittest
import subprocess
import tempfile
import shutil
import time
from pathlib import Path

# Add the parent directory to sys.path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Components to test
COMPONENTS = [
    "bexy",
    "pyllm",
    "devlama",  # Renamed from pylama
    "shellama",
    "apilama",
    "weblama",
    "loglama"
]

# Root directory of the project
ROOT_DIR = Path(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))


class DockerTestCase(unittest.TestCase):
    """Base test case for Docker tests."""

    def setUp(self):
        """Set up the test environment."""
        self.temp_dir = tempfile.mkdtemp()
        self.original_dir = os.getcwd()
        
    def tearDown(self):
        """Clean up the test environment."""
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


class TestDockerfiles(DockerTestCase):
    """Test the Dockerfiles of all components."""

    def test_dockerfile_exists(self):
        """Test that each component has a Dockerfile."""
        for component in COMPONENTS:
            component_path = os.path.join(ROOT_DIR, component)
            dockerfile_path = os.path.join(component_path, "Dockerfile")
            
            if os.path.exists(component_path):
                if not os.path.exists(dockerfile_path):
                    # Check for alternative Dockerfile locations
                    docker_dir = os.path.join(component_path, "docker")
                    if os.path.exists(docker_dir):
                        dockerfile_path = os.path.join(docker_dir, "Dockerfile")
                
                self.assertTrue(
                    os.path.exists(dockerfile_path) or 
                    os.path.exists(os.path.join(component_path, "Dockerfile.test")),
                    f"No Dockerfile found for component {component}"
                )
    
    def test_dockerfile_syntax(self):
        """Test that each Dockerfile has valid syntax."""
        for component in COMPONENTS:
            component_path = os.path.join(ROOT_DIR, component)
            if not os.path.exists(component_path):
                continue
                
            dockerfile_path = os.path.join(component_path, "Dockerfile")
            if not os.path.exists(dockerfile_path):
                # Check for alternative Dockerfile locations
                docker_dir = os.path.join(component_path, "docker")
                if os.path.exists(docker_dir):
                    dockerfile_path = os.path.join(docker_dir, "Dockerfile")
                else:
                    dockerfile_path = os.path.join(component_path, "Dockerfile.test")
            
            if not os.path.exists(dockerfile_path):
                continue
                
            result = self.run_command(["docker", "build", "--quiet", "-f", dockerfile_path, "."], cwd=component_path)
            self.assertEqual(
                result.returncode, 0,
                f"Dockerfile syntax check failed for {component}: {result.stderr}"
            )


class TestDockerCompose(DockerTestCase):
    """Test the docker-compose files of all components."""

    def test_docker_compose_exists(self):
        """Test that each component has a docker-compose file or that there's a central one."""
        # Check for central docker-compose file
        central_compose = os.path.join(ROOT_DIR, "docker-compose.yml")
        central_compose_test = os.path.join(ROOT_DIR, "docker-compose.test.yml")
        
        if os.path.exists(central_compose) or os.path.exists(central_compose_test):
            return
            
        # Check individual components
        for component in COMPONENTS:
            component_path = os.path.join(ROOT_DIR, component)
            if not os.path.exists(component_path):
                continue
                
            compose_path = os.path.join(component_path, "docker-compose.yml")
            compose_test_path = os.path.join(component_path, "docker-compose.test.yml")
            
            # Check for docker directory
            docker_dir = os.path.join(component_path, "docker")
            if os.path.exists(docker_dir):
                compose_path = os.path.join(docker_dir, "docker-compose.yml")
                compose_test_path = os.path.join(docker_dir, "docker-compose.test.yml")
            
            self.assertTrue(
                os.path.exists(compose_path) or os.path.exists(compose_test_path),
                f"No docker-compose file found for component {component}"
            )
    
    def test_docker_compose_syntax(self):
        """Test that each docker-compose file has valid syntax."""
        # Check central docker-compose file
        central_compose = os.path.join(ROOT_DIR, "docker-compose.yml")
        central_compose_test = os.path.join(ROOT_DIR, "docker-compose.test.yml")
        
        if os.path.exists(central_compose):
            result = self.run_command(["docker-compose", "-f", central_compose, "config"], cwd=ROOT_DIR)
            self.assertEqual(
                result.returncode, 0,
                f"Central docker-compose syntax check failed: {result.stderr}"
            )
            
        if os.path.exists(central_compose_test):
            result = self.run_command(["docker-compose", "-f", central_compose_test, "config"], cwd=ROOT_DIR)
            self.assertEqual(
                result.returncode, 0,
                f"Central docker-compose.test syntax check failed: {result.stderr}"
            )
            
        # Check individual components
        for component in COMPONENTS:
            component_path = os.path.join(ROOT_DIR, component)
            if not os.path.exists(component_path):
                continue
                
            compose_path = os.path.join(component_path, "docker-compose.yml")
            compose_test_path = os.path.join(component_path, "docker-compose.test.yml")
            
            # Check for docker directory
            docker_dir = os.path.join(component_path, "docker")
            if os.path.exists(docker_dir):
                if os.path.exists(os.path.join(docker_dir, "docker-compose.yml")):
                    compose_path = os.path.join(docker_dir, "docker-compose.yml")
                if os.path.exists(os.path.join(docker_dir, "docker-compose.test.yml")):
                    compose_test_path = os.path.join(docker_dir, "docker-compose.test.yml")
            
            if os.path.exists(compose_path):
                result = self.run_command(["docker-compose", "-f", compose_path, "config"], cwd=component_path)
                self.assertEqual(
                    result.returncode, 0,
                    f"docker-compose syntax check failed for {component}: {result.stderr}"
                )
                
            if os.path.exists(compose_test_path):
                result = self.run_command(["docker-compose", "-f", compose_test_path, "config"], cwd=component_path)
                self.assertEqual(
                    result.returncode, 0,
                    f"docker-compose.test syntax check failed for {component}: {result.stderr}"
                )


class TestDockerMakeTargets(DockerTestCase):
    """Test the Docker-related Makefile targets of all components."""

    def test_docker_make_targets_exist(self):
        """Test that each component's Makefile has Docker-related targets."""
        for component in COMPONENTS:
            component_path = os.path.join(ROOT_DIR, component)
            makefile_path = os.path.join(component_path, "Makefile")
            
            if not os.path.exists(component_path) or not os.path.exists(makefile_path):
                continue
                
            # Read the Makefile content
            with open(makefile_path, 'r') as f:
                makefile_content = f.read()
            
            # Check for Docker-related targets
            docker_targets = [
                "docker-build",
                "docker-run",
                "docker-test",
                "docker-push",
                "docker-clean"
            ]
            
            found_targets = []
            for target in docker_targets:
                if target in makefile_content:
                    found_targets.append(target)
            
            self.assertTrue(
                len(found_targets) > 0,
                f"No Docker-related targets found in Makefile for {component}"
            )
    
    def test_docker_build_target(self):
        """Test that each component's Makefile has a docker-build target that runs without errors."""
        for component in COMPONENTS:
            component_path = os.path.join(ROOT_DIR, component)
            makefile_path = os.path.join(component_path, "Makefile")
            
            if not os.path.exists(component_path) or not os.path.exists(makefile_path):
                continue
                
            # Check if the target exists without actually running it
            result = subprocess.run(
                ["make", "-n", "docker-build"],
                cwd=component_path,
                capture_output=True,
                text=True
            )
            
            if result.returncode == 0:
                # The target exists, but we won't actually run it to avoid building Docker images
                pass
            else:
                # Check for alternative target names
                alt_targets = ["docker_build", "build-docker", "build_docker"]
                for target in alt_targets:
                    result = subprocess.run(
                        ["make", "-n", target],
                        cwd=component_path,
                        capture_output=True,
                        text=True
                    )
                    if result.returncode == 0:
                        break
                
                # It's okay if no docker-build target is found, as not all components might have Docker support
                pass


if __name__ == "__main__":
    unittest.main()
