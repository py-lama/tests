# Use a specific version of Ubuntu LTS as base
FROM ubuntu:22.04

# Set non-interactive frontend for apt-get and SSH
ENV DEBIAN_FRONTEND=noninteractive \
    GIT_SSH_COMMAND="ssh -o StrictHostKeyChecking=no -o UserKnownHostsFile=/dev/null"

# Install essential build tools, Python, and SSH client
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    ca-certificates \
    curl \
    git \
    make \
    openssh-client \
    python3 \
    python3-pip \
    python3-venv \
    wget \
    && rm -rf /var/lib/apt/lists/*

# Configure Git to use SSH with strict host checking disabled
RUN git config --global core.sshCommand "ssh -o StrictHostKeyChecking=no -o UserKnownHostsFile=/dev/null"

# Create a non-root user to avoid permission issues
RUN groupadd -r appuser && useradd -r -g appuser appuser \
    && mkdir -p /home/appuser/.ssh \
    && chown -R appuser:appuser /home/appuser

# Set working directory and switch to non-root user
WORKDIR /app
USER appuser

# Copy the test script and set permissions
COPY --chown=appuser:appuser test_make_in_docker.sh .
RUN chmod +x test_make_in_docker.sh

# Set default environment variables
ENV REPO_URL="" \
    BRANCH="main" \
    MAKE_TARGETS="deps test" \
    PYTHON_DEPS="" \
    SYSTEM_DEPS="" \
    TEST_TIMEOUT=300

# Default command
CMD ["./test_make_in_docker.sh"]
