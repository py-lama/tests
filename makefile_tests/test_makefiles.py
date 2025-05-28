#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Test suite for verifying Makefile functionality across all PyLama ecosystem components.

This test suite verifies that all Makefiles in the PyLama ecosystem work correctly,
including their setup, run, and test targets.
"""

import os
import sys
import unittest
import subprocess
import tempfile
import shutil
from pathlib import Path

# Add the parent directory to sys.path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Components to test
COMPONENTS = [
    "bexy",
    "getllm",
    "devlama",  # Renamed from pylama
    "shellama",
    "apilama",
    "weblama",
    "loglama"
]

# Root directory of the project
ROOT_DIR = Path(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))


class MakefileTestCase(unittest.TestCase):
    """Base test case for Makefile tests."""

    def setUp(self):
        """Set up the test environment."""
        self.temp_dir = tempfile.mkdtemp()
        self.original_dir = os.getcwd()
        
    def tearDown(self):
        """Clean up the test environment."""
        os.chdir(self.original_dir)
        shutil.rmtree(self.temp_dir, ignore_errors=True)

    def run_make_command(self, component_dir, target, timeout=30):
        """Run a make command in the given directory."""
        component_path = os.path.join(ROOT_DIR, component_dir)
        if not os.path.exists(component_path):
            self.skipTest(f"Component directory {component_dir} does not exist")
            
        os.chdir(component_path)
        
        try:
            result = subprocess.run(
                ["make", target],
                capture_output=True,
                text=True,
                timeout=timeout
            )
            return result
        except subprocess.TimeoutExpired:
            self.fail(f"Command 'make {target}' timed out after {timeout} seconds")
            return None


class TestMakefiles(MakefileTestCase):
    """Test the Makefiles of all components."""

    def test_makefile_exists(self):
        """Test that each component has a Makefile."""
        for component in COMPONENTS:
            component_path = os.path.join(ROOT_DIR, component)
            makefile_path = os.path.join(component_path, "Makefile")
            
            if os.path.exists(component_path):
                self.assertTrue(
                    os.path.exists(makefile_path),
                    f"Makefile not found for component {component}"
                )
    
    def test_makefile_help_target(self):
        """Test that each Makefile has a help target that runs without errors."""
        for component in COMPONENTS:
            component_path = os.path.join(ROOT_DIR, component)
            if not os.path.exists(component_path):
                continue
                
            result = self.run_make_command(component, "help")
            self.assertEqual(
                result.returncode, 0,
                f"Help target failed for {component}: {result.stderr}"
            )
            self.assertIn(
                "help", result.stdout.lower(),
                f"Help output does not contain 'help' for {component}"
            )
    
    def test_makefile_setup_target(self):
        """Test that each Makefile has a setup target."""
        for component in COMPONENTS:
            component_path = os.path.join(ROOT_DIR, component)
            if not os.path.exists(component_path):
                continue
                
            # Just check if the target exists without actually running it
            result = subprocess.run(
                ["make", "-n", "setup"],
                cwd=component_path,
                capture_output=True,
                text=True
            )
            self.assertEqual(
                result.returncode, 0,
                f"Setup target check failed for {component}: {result.stderr}"
            )
    
    def test_makefile_clean_target(self):
        """Test that each Makefile has a clean target that runs without errors."""
        for component in COMPONENTS:
            component_path = os.path.join(ROOT_DIR, component)
            if not os.path.exists(component_path):
                continue
                
            result = self.run_make_command(component, "clean")
            self.assertEqual(
                result.returncode, 0,
                f"Clean target failed for {component}: {result.stderr}"
            )
    
    def test_makefile_run_target_exists(self):
        """Test that each Makefile has a run target."""
        for component in COMPONENTS:
            component_path = os.path.join(ROOT_DIR, component)
            if not os.path.exists(component_path):
                continue
                
            # Just check if the target exists without actually running it
            result = subprocess.run(
                ["make", "-n", "run"],
                cwd=component_path,
                capture_output=True,
                text=True
            )
            self.assertEqual(
                result.returncode, 0,
                f"Run target check failed for {component}: {result.stderr}"
            )
    
    def test_makefile_test_target_exists(self):
        """Test that each Makefile has a test target."""
        for component in COMPONENTS:
            component_path = os.path.join(ROOT_DIR, component)
            if not os.path.exists(component_path):
                continue
                
            # Just check if the target exists without actually running it
            result = subprocess.run(
                ["make", "-n", "test"],
                cwd=component_path,
                capture_output=True,
                text=True
            )
            self.assertEqual(
                result.returncode, 0,
                f"Test target check failed for {component}: {result.stderr}"
            )


if __name__ == "__main__":
    unittest.main()
