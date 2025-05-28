# PyLama Microservices Architecture

## Overview

This repository contains a microservices-based architecture for the PyLama ecosystem, consisting of the following components:

- **LogLama**: Primary service for the entire ecosystem that provides centralized logging, environment management, dependency validation, and service orchestration
- **BEXY**: Python code execution sandbox
- **PyLLM**: LLM operations service
- **PyLama**: Ollama management service
- **SheLLama**: Shell and filesystem operations service
- **APILama**: API gateway for all services
- **WebLama**: Web frontend (JavaScript/HTML/CSS)

The architecture has been refactored to improve maintainability, scalability, and separation of concerns. Each component now exposes a REST API that can be consumed by other services through the APILama gateway.

## Architecture

The PyLama ecosystem is built around LogLama as the primary service that starts first and coordinates all other components. LogLama provides centralized logging, environment management, dependency validation, and service orchestration. This architecture ensures all components have the correct configuration before they run, allows for better integration, simplified deployment, and consistent configuration across all services.

```
                   +------------+
                   |   Ollama   |
                   |   (LLM)    |
                   +------------+
                        ^
                        |
                        v
                  +---------------+
                  |   LogLama     |
                  | (Environment) |
                  +---------------+
                     ^    ^    ^
                     |    |    |
         +-----------+    |    +-----------+
         |                |                |
         v                v                v
+------------+     +------------+     +---------------+     +------------+
|   BEXY    |     |   PyLLM    |<--->|   PyLama      |<--->| SheLLama   |
|  (Sandbox) |<--->|   (LLM)    |     | (Orchestrator)|     |  (Shell)   |
+------------+     +------------+     +---------------+     +------------+
      ^                  ^                  ^                  ^
      |                  |                  |                  |
      v                  v                  v                  v
+-----------------------------------------------------------------------+
|                            APILama                                    |
|                          (API Gateway)                                |
+-----------------------------------------------------------------------+
                                ^
                                |
                                v
+-----------------------------------------------------------------------+
|                            WebLama                                    |
|                           (Frontend)                                  |
+-----------------------------------------------------------------------+
                                ^
                                |
                                v
+-----------------------------------------------------------------------+
|                            Browser                                    |
+-----------------------------------------------------------------------+
```

## Services

### LogLama (Port 5000) - Primary Service for the PyLama Ecosystem

LogLama is the primary service that starts first and coordinates all other components in the PyLama ecosystem. It provides:
- Centralized environment variable management through a shared `.env` file
- Dependency validation and installation for all components
- Comprehensive logging system with structured logging support and multi-output capabilities
- Service health monitoring, diagnostics, and orchestration
- Web interface for viewing logs, filtering by component, and monitoring system status
- CLI for managing the entire PyLama ecosystem
- Integration tools for all components to connect to the centralized logging system
- Multi-language support for logging from Python, JavaScript, Bash, and other languages

### PyLama (Port 8003) - Ollama Orchestration Service

PyLama serves as the orchestration point for Ollama integration. It provides:
- Model management via Ollama integration
- Model inference and fine-tuning
- Coordination between LLM-related services
- Unified interface for managing Ollama models

### APILama (Port 8080) - Backend API Gateway

APILama acts as the API gateway that connects all backend services and exposes them to the frontend. It provides:
- Unified REST API for all services
- Request routing to appropriate backend services (BEXY, PyLLM, SheLLama, PyLama)
- Authentication and authorization
- Health monitoring and logging
- Error handling and response formatting
- Cross-Origin Resource Sharing (CORS) support

All frontend requests go through APILama, which then communicates with the appropriate backend service. This architecture ensures a clean separation between frontend and backend components.

### WebLama (Port 8081) - Frontend-Only Component

WebLama is a pure frontend application built with HTML, CSS, and JavaScript. It provides:
- User interface for interacting with the services
- Code editor with syntax highlighting using CodeMirror
- File explorer and markdown rendering with Marked.js
- Mermaid diagram support
- Execution results display

The WebLama frontend communicates exclusively with the APILama backend gateway and contains no backend logic of its own. It's designed as a static web application that can be served by any web server (Nginx in Docker).

### SheLLama (Port 8002) - Shell and Filesystem Operations

SheLLama provides shell and filesystem operations as a dedicated REST API service. It includes:
- File operations (read, write, list, search)
- Directory management and navigation
- Shell command execution with proper error handling
- Git integration for version control
- Secure file handling with proper permissions

APILama communicates with SheLLama to perform all file system and shell operations, maintaining a clean separation between the frontend and backend components.

### BEXY (Port 8000) - Code Execution Sandbox

Python code execution sandbox service that provides:
- Code execution in isolated environments
- Dependency management
- Code analysis and security checks
- Output capture and formatting

### PyLLM (Port 8001) - LLM Operations

LLM operations service that provides:
- LLM model queries and interactions
- Code fixing and enhancement functionality
- Alternative solution generation
- Code explanation and documentation

## Centralized Environment and Logging System

The PyLama ecosystem uses a centralized environment and logging system managed by LogLama as the primary service. This system ensures that all components share the same configuration, environment variables, and logging infrastructure, simplifying management and deployment while providing comprehensive visibility into the entire ecosystem.

### Key Features

- **Single Source of Truth**: All projects use a common `.env` file in the `pylama` directory
- **Automatic Validation**: LogLama checks for required variables and adds them with defaults if missing
- **Dependency Management**: LogLama can check and install dependencies before starting services
- **Service Orchestration**: LogLama can start all services in the correct order
- **Fallback Mechanism**: Components can still use local `.env` files if the central one is not available

### Using the Centralized Environment

```bash
# Initialize the centralized environment
python -m loglama.cli.main init

# Check and install dependencies for all components
python -m loglama.cli.main check-deps all

# Start all services
python -m loglama.cli.main start-all

# View environment variables
python -m loglama.cli.main env
```

## Getting Started

### Prerequisites

- Docker and Docker Compose (recommended for easy deployment)
- Python 3.8 or higher (for development without Docker)
- Node.js 14 or higher (for WebLama frontend development)
- Git

### Docker Deployment (Recommended)

The easiest way to run the entire PyLama ecosystem is using Docker Compose, which will set up all components with the correct configuration and dependencies.

1. Clone the repository:
   ```bash
   git clone https://github.com/yourusername/py-lama.git
   cd py-lama
   ```

2. Start all services with Docker Compose:
   ```bash
   docker-compose up -d
   ```
   This will start all components in the correct order with LogLama as the primary service for environment and logging management.

3. Access the web interfaces:
   - LogLama web interface: `http://localhost:6001` (for logs and system status)
   - WebLama interface: `http://localhost:9081` (for the main application)
   - Grafana dashboard: `http://localhost:3000` (for visualizing logs, when using LogLama-Grafana integration)

4. To start with LogLama-Grafana integration for centralized logging and visualization:
   ```bash
   # Use the specialized docker-compose file for logging integration
   docker-compose -f docker-compose.logging.yml up -d
   
   # Or use the convenience script
   ./docker-start-with-logs.sh start
   ```

5. Monitor the logs using LogLama:
   ```bash
   # View logs through LogLama CLI
   python -m loglama.cli.main logs
   
   # Or use Docker logs
   docker-compose logs -f
   
   # Generate sample logs for Grafana visualization
   docker exec loglama python -m loglama.examples.loglama-grafana.generate_diverse_logs_fixed
   ```

6. Stop all services:
   ```bash
   docker-compose down
   
   # Or if using the logging integration
   docker-compose -f docker-compose.logging.yml down
   ```

### Manual Installation (Development)

For development purposes, you can set up each component individually.

1. Clone the repository:
   ```bash
   git clone https://github.com/yourusername/py-lama.git
   cd py-lama
   ```

2. Set up each component:

   #### PyLama (Central Orchestration Service)
   ```bash
   cd pylama
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   pip install -e .
   ```

   #### APILama (API Gateway)
   ```bash
   cd apilama
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   pip install -e .
   ```

   #### SheLLama (Shell Operations)
   ```bash
   cd shellama
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   pip install -e .
   ```

   #### BEXY (Sandbox)
   ```bash
   cd bexy
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   pip install -e .
   ```

   #### PyLLM (LLM Operations)
   ```bash
   cd getllm
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   pip install -e .
   ```

   #### WebLama (Frontend)
   ```bash
   cd weblama
   npm install
   ```

### Running the Services Manually

#### Option 1: Using the start-pylama.sh Script (Recommended)

The repository includes a convenient script that can start, stop, and manage all PyLama services:

```bash
# Start all services
./start-pylama.sh start

# Stop all services
./start-pylama.sh stop

# Restart all services
./start-pylama.sh restart

# Check status of all services
./start-pylama.sh status

# View logs for a specific service
./start-pylama.sh logs weblama

# Open WebLama in browser
./start-pylama.sh open
```

This script will start each service in the background, save the PID to a file, and redirect the output to a log file. You can check the status of each service or view the logs at any time.

#### Option 2: Starting Services Individually

If you prefer to start each service manually, follow these steps in order:

1. **BEXY** (Sandbox):
   ```bash
   cd bexy
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   python -m bexy.app --port 8000 --host 127.0.0.1
   ```

2. **PyLLM** (LLM Operations):
   ```bash
   cd getllm
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   python -m getllm.app --port 8001 --host 127.0.0.1
   ```

3. **SheLLama** (Shell Operations):
   ```bash
   cd shellama
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   python -m shellama.app --port 8002 --host 127.0.0.1
   ```

4. **APILama** (API Gateway):
   ```bash
   cd apilama
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   python -m apilama.app --port 8080 --host 127.0.0.1
   ```
   Note: APILama now communicates with SheLLama via its REST API.

5. **PyLama** (Central Orchestration):
   ```bash
   cd pylama
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   python -m pylama.app --port 8003 --host 127.0.0.1
   ```
   PyLama coordinates all other services and provides a unified interface.

6. **WebLama** (Frontend):
   ```bash
   cd weblama
   weblama start
   ```
   Or use the WebLama CLI with more options:
   ```bash
   # Start with custom port and API URL
   weblama start --port 8090 --api-url http://localhost:8080
   
   # Start and automatically open in browser
   weblama start --open
   ```

7. Access the web interface:
   - Open your browser and navigate to `http://localhost:8081` (or whatever port you configured for the WebLama frontend)

## API Documentation

### APILama Endpoints

#### Health Check
```
GET /api/health
```
Returns the health status of the APILama service.

#### PyLama Endpoints
```
GET /api/pylama/health
POST /api/pylama/execute
```

#### BEXY Endpoints
```
GET /api/bexy/health
POST /api/bexy/execute
```

#### PyLLM Endpoints
```
GET /api/getllm/health
POST /api/getllm/generate
```

#### SheLLama Endpoints
```
GET /api/shellama/health
GET /api/shellama/files
GET /api/shellama/file
POST /api/shellama/file
DELETE /api/shellama/file
GET /api/shellama/directory
POST /api/shellama/directory
DELETE /api/shellama/directory
POST /api/shellama/shell
```

## Development

### Adding a New Service

To add a new service to the ecosystem:

1. Create a new directory for your service
2. Implement the service with a REST API
3. Add routes to APILama to proxy requests to your service
4. Update the WebLama frontend to interact with your service through APILama

### Testing

Each service has its own test suite. To run the tests for a service:

```bash
cd <service-directory>
python -m unittest discover tests
```

To run the integration tests for the entire ecosystem:

```bash
python integration_test.py
```

## Benefits of the Microservices Architecture

1. **Modularity**: Each service can be developed, deployed, and scaled independently
2. **Scalability**: Services can be scaled based on demand
3. **Maintainability**: Clearer separation of concerns
4. **Deployment Flexibility**: Components can be deployed separately or together
5. **Language Agnostic**: Future components could be written in different languages

## Using PyLama with the Frontend (WebLama)

The PyLama ecosystem is designed to provide a seamless integration between the backend services and the WebLama frontend. Here's how to effectively use the frontend with the PyLama backend services:

### Accessing the WebLama Interface

1. **Start the PyLama ecosystem** using one of the methods described above (Docker or manual installation).

2. **Open WebLama in your browser**:
   - When using Docker: `http://localhost:9081`
   - When running manually: `http://localhost:8081` (or the port you specified)

3. **Alternative ways to open WebLama**:
   ```bash
   # Using the PyLama CLI
   python -m pylama.cli open
   
   # Or when starting services
   python -m pylama.cli start --weblama --open
   
   # Using the convenience script
   ./start-pylama.sh open
   ```

### WebLama Interface Features

1. **Code Editor**: WebLama provides a full-featured code editor with syntax highlighting.
   - Create new files using the file explorer
   - Edit existing files with syntax highlighting
   - Execute code directly from the editor

2. **Markdown Support**: WebLama can render markdown files with support for:
   - Standard markdown syntax
   - Code blocks with syntax highlighting
   - Mermaid diagrams for visualizing workflows and architecture

3. **File Explorer**: Navigate through available files and directories.
   - Click on files to open them in the editor
   - Create, rename, and delete files

4. **Integration with PyLama Services**:
   - Execute code through BEXY
   - Interact with LLMs through PyLLM
   - Perform file operations through SheLLama
   - Access logs through LogLama

### LogLama-Grafana Integration

The PyLama ecosystem includes integration with Grafana for advanced log visualization and analysis:

1. **Access the Grafana Dashboard**:
   - When using Docker with logging integration: `http://localhost:3000`
   - Default credentials: admin/admin (you'll be prompted to change on first login)

2. **Available Dashboards**:
   - **PyLama Overview**: Shows logs from all services in the ecosystem
   - **LogLama Metrics**: Displays performance metrics and log statistics
   - **Service Health**: Monitors the health of all services

3. **Generating Sample Logs for Visualization**:
   ```bash
   # Using Docker
   docker exec loglama python -m loglama.examples.loglama-grafana.generate_diverse_logs_fixed
   
   # Using the Makefile
   cd loglama && make generate-grafana-logs
   ```

4. **Continuous Web Log Monitoring**:
   ```bash
   # Start web log monitoring
   cd loglama && make run-grafana-web-monitor
   
   # Stop web log monitoring
   cd loglama && make stop-grafana-web-monitor
   ```

### Troubleshooting Frontend-Backend Integration

1. **Check Service Status**:
   ```bash
   # Using Docker
   docker-compose ps
   
   # Using the PyLama CLI
   python -m pylama.cli status
   
   # Using the convenience script
   ./start-pylama.sh status
   ```

2. **Check Logs for Errors**:
   ```bash
   # View logs for WebLama
   docker-compose logs weblama
   
   # View logs for APILama (the gateway)
   docker-compose logs apilama
   
   # View logs for all services
   docker-compose logs
   ```

3. **Debug Utilities**:
   ```bash
   # Run debug utilities to check LogLama integration
   cd loglama && make run-debug
   
   # Run specific debug tests
   cd loglama && make run-debug-context
   cd loglama && make run-debug-sqlite
   cd loglama && make run-debug-file
   ```

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## License

This project is licensed under the MIT License - see the LICENSE file for details.
