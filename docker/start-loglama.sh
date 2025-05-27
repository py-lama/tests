#!/bin/bash

# Start the LogLama collector in the background
echo "Starting LogLama collector..."
python -m loglama.cli.main collect-daemon &

# Give the collector a moment to initialize
sleep 2

# Start the LogLama web interface
echo "Starting LogLama web interface..."
exec python -m loglama.cli.main web --host 0.0.0.0 --port 5001 --db /app/logs/loglama.db
