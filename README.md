# PyLama Ecosystem Tests

This directory contains test scripts and utilities for testing all projects in the PyLama ecosystem.

## Available Scripts

- `setup_test_env.sh`: Sets up the test environment, including mock API responses and test data.
- `test_all_projects_comprehensive.sh`: Runs comprehensive tests for all projects in the ecosystem.
- `fix_weblama_tests.sh`: Fixes issues with WebLama tests.
- `fix_getllm_tests.sh`: Fixes issues with GetLLM tests.
- `fix_remaining_projects.sh`: Fixes issues with the remaining projects in the ecosystem.
- `fix_weblama_frontend_tests.sh`: Fixes issues with WebLama frontend tests.
- `install_js_dependencies.sh`: Installs dependencies for JavaScript projects.
- `run_all_tests.sh`: Runs tests for all projects and exits with an error if any tests fail.
- `run_all_tests_tolerant.sh`: Runs tests for all projects and continues even if some tests fail.

## Running Tests

To run all tests for all projects:

```bash
./run_all_tests.sh
```

To run tests and continue even if some tests fail:

```bash
./run_all_tests_tolerant.sh
```

## License

Apache-2.0
