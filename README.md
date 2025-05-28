# PyLama Ecosystem Tests

This directory contains test scripts and utilities for testing all projects in the PyLama ecosystem.

## Available Scripts

### Core Testing Scripts

- `setup_test_env.sh`: Sets up the test environment, including mock API responses and test data.
- `test_all_projects_comprehensive.sh`: Runs comprehensive tests for all projects in the ecosystem.
- `run_all_tests.sh`: Runs tests for all projects and exits with an error if any tests fail.
- `run_all_tests_tolerant.sh`: Runs tests for all projects and continues even if some tests fail.

### Makefile Testing

- `test_all_makefiles.sh`: Tests all Makefiles in all projects to ensure they work properly.
  - Supports various options like `--verbose`, `--fix`, `--skip`, and `--test-only`.
  - Checks for test targets and provides detailed reporting.
  - Example: `./test_all_makefiles.sh --verbose --skip "getllm,loglama"`.

- `docker_test_makefiles.sh`: Tests all Makefiles in isolated Docker containers.
  - Provides secure and controlled testing environments.
  - Supports timeouts, custom Docker images, and selective testing.
  - Example: `./docker_test_makefiles.sh --timeout 120 --test-only "getllm,shellama"`.

### GitHub Actions Testing

- `test_github_actions.sh`: Runs GitHub Actions workflows locally using the `act` tool.
  - Tests workflows in isolated Docker containers.
  - Provides detailed logs and reports.
  - Example: `./test_github_actions.sh --test-only "getllm/ci.yml" --job build-test`.

- `validate_github_workflows.sh`: Validates GitHub Actions workflow files.
  - Checks for syntax errors and best practices.
  - Can automatically fix common issues with the `--fix` flag.
  - Example: `./validate_github_workflows.sh --fix`.

### Fix Scripts

- `fix_weblama_tests.sh`: Fixes issues with WebLama tests.
- `fix_getllm_tests.sh`: Fixes issues with GetLLM tests.
- `fix_remaining_projects.sh`: Fixes issues with the remaining projects in the ecosystem.
- `fix_weblama_frontend_tests.sh`: Fixes issues with WebLama frontend tests.
- `install_js_dependencies.sh`: Installs dependencies for JavaScript projects.

## Running Tests

### Testing All Projects

```bash
# Run all tests for all projects
./run_all_tests.sh

# Run tests and continue even if some tests fail
./run_all_tests_tolerant.sh
```

### Testing Makefiles

```bash
# Test all Makefiles
./test_all_makefiles.sh

# Test specific projects' Makefiles with verbose output
./test_all_makefiles.sh --verbose --test-only "getllm,shellama"

# Test Makefiles in Docker containers
./docker_test_makefiles.sh
```

### Testing GitHub Actions

```bash
# Validate all GitHub Actions workflows
./validate_github_workflows.sh

# Test a specific GitHub Actions workflow
./test_github_actions.sh --test-only "getllm/ci.yml" --job build-test
```

## Using the Makefile

The tests directory includes a comprehensive Makefile for managing the PyLama ecosystem. Key commands include:

```bash
# Set up all projects
make setup

# Run all services
make run-all

# Check status of all services
make status

# Stop all services
make stop-all

# Clean everything
make clean
```

See `make help` for a complete list of commands.

## License

Apache-2.0
