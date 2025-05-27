#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Main script to run all tests for the PyLama ecosystem.

This script runs all the test suites for the PyLama ecosystem components,
including Makefile tests, Docker tests, integration tests, and LogLama integration tests.
"""

import os
import sys
import unittest
import argparse
import time
from pathlib import Path

# Add the parent directory to sys.path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Import test modules
import test_makefiles
import test_docker
import test_integration
import test_loglama_integration

# Define test suites
def makefile_suite():
    """Return a test suite for Makefile tests."""
    suite = unittest.TestSuite()
    suite.addTest(unittest.defaultTestLoader.loadTestsFromTestCase(test_makefiles.TestMakefiles))
    return suite

def docker_suite():
    """Return a test suite for Docker tests."""
    suite = unittest.TestSuite()
    suite.addTest(unittest.makeSuite(test_docker.TestDockerfiles))
    suite.addTest(unittest.makeSuite(test_docker.TestDockerCompose))
    suite.addTest(unittest.makeSuite(test_docker.TestDockerMakeTargets))
    return suite

def integration_suite():
    """Return a test suite for integration tests."""
    suite = unittest.TestSuite()
    suite.addTest(unittest.makeSuite(test_integration.TestComponentIntegration))
    suite.addTest(unittest.makeSuite(test_integration.TestDockerIntegration))
    return suite

def loglama_suite():
    """Return a test suite for LogLama integration tests."""
    suite = unittest.TestSuite()
    suite.addTest(unittest.makeSuite(test_loglama_integration.TestLogLamaFiles))
    suite.addTest(unittest.makeSuite(test_loglama_integration.TestLogLamaScripts))
    suite.addTest(unittest.makeSuite(test_loglama_integration.TestLogLamaCollector))
    suite.addTest(unittest.makeSuite(test_loglama_integration.TestDockerLogLamaIntegration))
    return suite

def all_tests_suite():
    """Return a test suite for all tests."""
    suite = unittest.TestSuite()
    suite.addTest(makefile_suite())
    suite.addTest(docker_suite())
    suite.addTest(integration_suite())
    suite.addTest(loglama_suite())
    return suite

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Run tests for the PyLama ecosystem")
    parser.add_argument("--makefiles", action="store_true", help="Run Makefile tests")
    parser.add_argument("--docker", action="store_true", help="Run Docker tests")
    parser.add_argument("--integration", action="store_true", help="Run integration tests")
    parser.add_argument("--loglama", action="store_true", help="Run LogLama integration tests")
    parser.add_argument("--all", action="store_true", help="Run all tests")
    parser.add_argument("--verbose", "-v", action="store_true", help="Verbose output")
    args = parser.parse_args()

    # Set verbosity
    verbosity = 2 if args.verbose else 1

    # Run tests
    runner = unittest.TextTestRunner(verbosity=verbosity)
    
    if args.all or not (args.makefiles or args.docker or args.integration or args.loglama):
        print("Running all tests...")
        start_time = time.time()
        result = runner.run(all_tests_suite())
        end_time = time.time()
        print(f"All tests completed in {end_time - start_time:.2f} seconds")
        sys.exit(0 if result.wasSuccessful() else 1)
    
    if args.makefiles:
        print("Running Makefile tests...")
        start_time = time.time()
        result_makefiles = runner.run(makefile_suite())
        end_time = time.time()
        print(f"Makefile tests completed in {end_time - start_time:.2f} seconds")
    
    if args.docker:
        print("Running Docker tests...")
        start_time = time.time()
        result_docker = runner.run(docker_suite())
        end_time = time.time()
        print(f"Docker tests completed in {end_time - start_time:.2f} seconds")
    
    if args.integration:
        print("Running integration tests...")
        start_time = time.time()
        result_integration = runner.run(integration_suite())
        end_time = time.time()
        print(f"Integration tests completed in {end_time - start_time:.2f} seconds")
    
    if args.loglama:
        print("Running LogLama integration tests...")
        start_time = time.time()
        result_loglama = runner.run(loglama_suite())
        end_time = time.time()
        print(f"LogLama integration tests completed in {end_time - start_time:.2f} seconds")
    
    # Check if any tests failed
    failed = False
    if args.makefiles and not result_makefiles.wasSuccessful():
        failed = True
    if args.docker and not result_docker.wasSuccessful():
        failed = True
    if args.integration and not result_integration.wasSuccessful():
        failed = True
    if args.loglama and not result_loglama.wasSuccessful():
        failed = True
    
    sys.exit(1 if failed else 0)
