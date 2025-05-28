#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Main test runner for the PyLama ecosystem.

This script runs all tests for the PyLama ecosystem components, including:
- Unit tests for each component
- Makefile tests
- Docker tests
- Integration tests
- LogLama integration tests

It generates HTML reports for all test results.
"""

import os
import sys
import unittest
import argparse
import time
import datetime
import importlib
from pathlib import Path
import subprocess
import shutil

# Root directory of the project
ROOT_DIR = Path(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

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

def run_component_tests(component, html_dir, verbosity=1):
    """Run tests for a specific component."""
    component_path = os.path.join(ROOT_DIR, component)
    if not os.path.exists(component_path):
        print(f"Component {component} not found, skipping tests.")
        return True
    
    tests_path = os.path.join(component_path, "tests")
    if not os.path.exists(tests_path):
        print(f"No tests directory found for {component}, skipping tests.")
        return True
    
    # Add the component directory to sys.path
    sys.path.insert(0, component_path)
    
    # Create HTML report directory
    os.makedirs(html_dir, exist_ok=True)
    html_report = os.path.join(html_dir, f"{component}_tests.html")
    
    print(f"Running tests for {component}...")
    start_time = time.time()
    
    # Use unittest discover to find and run tests
    test_suite = unittest.defaultTestLoader.discover(tests_path, pattern="test_*.py")
    
    # Run tests with HTML report
    try:
        import HtmlTestRunner
        runner = HtmlTestRunner.HTMLTestRunner(
            output=html_dir,
            report_name=f"{component}_tests",
            combine_reports=True,
            verbosity=verbosity
        )
        result = runner.run(test_suite)
        success = result.wasSuccessful()
    except ImportError:
        # Fall back to TextTestRunner if HtmlTestRunner is not available
        print("HtmlTestRunner not available, using TextTestRunner instead.")
        runner = unittest.TextTestRunner(verbosity=verbosity)
        result = runner.run(test_suite)
        success = result.wasSuccessful()
    
    end_time = time.time()
    print(f"{component} tests completed in {end_time - start_time:.2f} seconds")
    
    # Remove the component directory from sys.path
    sys.path.remove(component_path)
    
    return success

def run_makefile_tests(html_dir, verbosity=1):
    """Run Makefile tests."""
    # Add the makefile_tests directory to sys.path
    makefile_tests_path = os.path.join(ROOT_DIR, "tests", "makefile_tests")
    sys.path.insert(0, makefile_tests_path)
    
    # Create HTML report directory
    os.makedirs(html_dir, exist_ok=True)
    html_report = os.path.join(html_dir, "makefile_tests.html")
    
    print("Running Makefile tests...")
    start_time = time.time()
    
    # Import the run_tests module
    try:
        sys.path.insert(0, os.path.join(ROOT_DIR, "tests", "makefile_tests"))
        from makefile_tests import run_tests
        success = run_tests.main(["--all", "--html", html_dir])
    except (ImportError, AttributeError):
        # Fall back to running the script directly
        result = subprocess.run(
            [sys.executable, os.path.join(makefile_tests_path, "run_tests.py"), "--all"],
            cwd=ROOT_DIR,
            capture_output=True,
            text=True
        )
        success = result.returncode == 0
        if not success:
            print(f"Makefile tests failed with output:\n{result.stdout}\n{result.stderr}")
    
    end_time = time.time()
    print(f"Makefile tests completed in {end_time - start_time:.2f} seconds")
    
    # Remove the makefile_tests directory from sys.path
    sys.path.remove(makefile_tests_path)
    
    return success

def run_docker_tests(html_dir, verbosity=1):
    """Run Docker tests."""
    # Add the makefile_tests directory to sys.path
    makefile_tests_path = os.path.join(ROOT_DIR, "tests", "makefile_tests")
    sys.path.insert(0, makefile_tests_path)
    
    # Create HTML report directory
    os.makedirs(html_dir, exist_ok=True)
    html_report = os.path.join(html_dir, "docker_tests.html")
    
    print("Running Docker tests...")
    start_time = time.time()
    
    # Import the run_tests module
    try:
        sys.path.insert(0, os.path.join(ROOT_DIR, "tests", "makefile_tests"))
        from makefile_tests import run_tests
        success = run_tests.main(["--docker", "--html", html_dir])
    except (ImportError, AttributeError):
        # Fall back to running the script directly
        result = subprocess.run(
            [sys.executable, os.path.join(makefile_tests_path, "run_tests.py"), "--docker"],
            cwd=ROOT_DIR,
            capture_output=True,
            text=True
        )
        success = result.returncode == 0
        if not success:
            print(f"Docker tests failed with output:\n{result.stdout}\n{result.stderr}")
    
    end_time = time.time()
    print(f"Docker tests completed in {end_time - start_time:.2f} seconds")
    
    # Remove the makefile_tests directory from sys.path
    sys.path.remove(makefile_tests_path)
    
    return success

def run_integration_tests(html_dir, verbosity=1):
    """Run integration tests."""
    # Add the makefile_tests directory to sys.path
    makefile_tests_path = os.path.join(ROOT_DIR, "tests", "makefile_tests")
    sys.path.insert(0, makefile_tests_path)
    
    # Create HTML report directory
    os.makedirs(html_dir, exist_ok=True)
    html_report = os.path.join(html_dir, "integration_tests.html")
    
    print("Running integration tests...")
    start_time = time.time()
    
    # Import the run_tests module
    try:
        sys.path.insert(0, os.path.join(ROOT_DIR, "tests", "makefile_tests"))
        from makefile_tests import run_tests
        success = run_tests.main(["--integration", "--html", html_dir])
    except (ImportError, AttributeError):
        # Fall back to running the script directly
        result = subprocess.run(
            [sys.executable, os.path.join(makefile_tests_path, "run_tests.py"), "--integration"],
            cwd=ROOT_DIR,
            capture_output=True,
            text=True
        )
        success = result.returncode == 0
        if not success:
            print(f"Integration tests failed with output:\n{result.stdout}\n{result.stderr}")
    
    end_time = time.time()
    print(f"Integration tests completed in {end_time - start_time:.2f} seconds")
    
    # Remove the makefile_tests directory from sys.path
    sys.path.remove(makefile_tests_path)
    
    return success

def run_loglama_tests(html_dir, verbosity=1):
    """Run LogLama integration tests."""
    # Add the makefile_tests directory to sys.path
    makefile_tests_path = os.path.join(ROOT_DIR, "tests", "makefile_tests")
    sys.path.insert(0, makefile_tests_path)
    
    # Create HTML report directory
    os.makedirs(html_dir, exist_ok=True)
    html_report = os.path.join(html_dir, "loglama_tests.html")
    
    print("Running LogLama integration tests...")
    start_time = time.time()
    
    # Import the run_tests module
    try:
        sys.path.insert(0, os.path.join(ROOT_DIR, "tests", "makefile_tests"))
        from makefile_tests import run_tests
        success = run_tests.main(["--loglama", "--html", html_dir])
    except (ImportError, AttributeError):
        # Fall back to running the script directly
        result = subprocess.run(
            [sys.executable, os.path.join(makefile_tests_path, "run_tests.py"), "--loglama"],
            cwd=ROOT_DIR,
            capture_output=True,
            text=True
        )
        success = result.returncode == 0
        if not success:
            print(f"LogLama tests failed with output:\n{result.stdout}\n{result.stderr}")
    
    end_time = time.time()
    print(f"LogLama integration tests completed in {end_time - start_time:.2f} seconds")
    
    # Remove the makefile_tests directory from sys.path
    sys.path.remove(makefile_tests_path)
    
    return success

def run_ansible_tests(html_dir, verbosity=1):
    """Run Ansible tests."""
    # Check if ansible_tests directory exists
    ansible_tests_path = os.path.join(ROOT_DIR, "ansible_tests")
    if not os.path.exists(ansible_tests_path):
        print("No ansible_tests directory found, skipping Ansible tests.")
        return True
    
    # Create HTML report directory
    os.makedirs(html_dir, exist_ok=True)
    html_report = os.path.join(html_dir, "ansible_tests.html")
    
    print("Running Ansible tests...")
    start_time = time.time()
    
    # Run Ansible tests
    result = subprocess.run(
        ["ansible-playbook", "test_all.yml", "-v"],
        cwd=ansible_tests_path,
        capture_output=True,
        text=True
    )
    
    success = result.returncode == 0
    if not success:
        print(f"Ansible tests failed with output:\n{result.stdout}\n{result.stderr}")
    
    # Save the output to an HTML file
    with open(html_report, "w") as f:
        f.write("<html><head><title>Ansible Tests</title></head><body>")
        f.write("<h1>Ansible Tests</h1>")
        f.write("<pre>")
        f.write(result.stdout)
        f.write("</pre>")
        if result.stderr:
            f.write("<h2>Errors</h2>")
            f.write("<pre>")
            f.write(result.stderr)
            f.write("</pre>")
        f.write("</body></html>")
    
    end_time = time.time()
    print(f"Ansible tests completed in {end_time - start_time:.2f} seconds")
    
    return success

def main():
    """Main function to run all tests."""
    parser = argparse.ArgumentParser(description="Run tests for the PyLama ecosystem")
    parser.add_argument("--components", action="store_true", help="Run component tests")
    parser.add_argument("--makefiles", action="store_true", help="Run Makefile tests")
    parser.add_argument("--docker", action="store_true", help="Run Docker tests")
    parser.add_argument("--integration", action="store_true", help="Run integration tests")
    parser.add_argument("--loglama", action="store_true", help="Run LogLama integration tests")
    parser.add_argument("--ansible", action="store_true", help="Run Ansible tests")
    parser.add_argument("--all", action="store_true", help="Run all tests")
    parser.add_argument("--verbose", "-v", action="store_true", help="Verbose output")
    parser.add_argument("--html-dir", default="test-reports", help="Directory for HTML reports")
    args = parser.parse_args()
    
    # Set verbosity
    verbosity = 2 if args.verbose else 1
    
    # Create HTML report directory
    html_dir = os.path.join(ROOT_DIR, args.html_dir)
    os.makedirs(html_dir, exist_ok=True)
    
    # Track overall success
    overall_success = True
    
    # Run tests
    if args.all or not (args.components or args.makefiles or args.docker or args.integration or args.loglama or args.ansible):
        print("Running all tests...")
        start_time = time.time()
        
        # Run component tests
        for component in COMPONENTS:
            success = run_component_tests(component, html_dir, verbosity)
            overall_success = overall_success and success
        
        # Run Makefile tests
        success = run_makefile_tests(html_dir, verbosity)
        overall_success = overall_success and success
        
        # Run Docker tests
        success = run_docker_tests(html_dir, verbosity)
        overall_success = overall_success and success
        
        # Run integration tests
        success = run_integration_tests(html_dir, verbosity)
        overall_success = overall_success and success
        
        # Run LogLama integration tests
        success = run_loglama_tests(html_dir, verbosity)
        overall_success = overall_success and success
        
        # Run Ansible tests
        success = run_ansible_tests(html_dir, verbosity)
        overall_success = overall_success and success
        
        end_time = time.time()
        print(f"All tests completed in {end_time - start_time:.2f} seconds")
    else:
        if args.components:
            for component in COMPONENTS:
                success = run_component_tests(component, html_dir, verbosity)
                overall_success = overall_success and success
        
        if args.makefiles:
            success = run_makefile_tests(html_dir, verbosity)
            overall_success = overall_success and success
        
        if args.docker:
            success = run_docker_tests(html_dir, verbosity)
            overall_success = overall_success and success
        
        if args.integration:
            success = run_integration_tests(html_dir, verbosity)
            overall_success = overall_success and success
        
        if args.loglama:
            success = run_loglama_tests(html_dir, verbosity)
            overall_success = overall_success and success
        
        if args.ansible:
            success = run_ansible_tests(html_dir, verbosity)
            overall_success = overall_success and success
    
    # Create index.html
    index_path = os.path.join(html_dir, "index.html")
    with open(index_path, "w") as f:
        f.write("<html><head><title>PyLama Ecosystem Test Results</title></head><body>")
        f.write("<h1>PyLama Ecosystem Test Results</h1>")
        f.write(f"<p>Tests run at: {datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}</p>")
        
        f.write("<h2>Test Reports</h2>")
        f.write("<ul>")
        
        # List all HTML reports
        for html_file in os.listdir(html_dir):
            if html_file.endswith(".html") and html_file != "index.html":
                f.write(f'<li><a href="{html_file}">{html_file}</a></li>')
        
        f.write("</ul>")
        
        # Overall result
        f.write("<h2>Overall Result</h2>")
        if overall_success:
            f.write('<p style="color: green; font-weight: bold;">All tests passed!</p>')
        else:
            f.write('<p style="color: red; font-weight: bold;">Some tests failed. See individual reports for details.</p>')
        
        f.write("</body></html>")
    
    print(f"Test reports generated in {html_dir}")
    print(f"Open {index_path} to view the results")
    
    return 0 if overall_success else 1

if __name__ == "__main__":
    sys.exit(main())
