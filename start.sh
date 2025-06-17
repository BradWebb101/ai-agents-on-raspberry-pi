#!/bin/bash
# Start all containers using Docker Compose

set -e

cleanup() {
  echo "\nShutting down containers..."
  docker-compose down
  exit
}

trap cleanup SIGINT SIGTERM

docker-compose up -d --build

# Wait for OIDC server to be ready (port 3000)
echo "Waiting for OIDC server to be ready..."
while ! nc -z localhost 3000; do
  sleep 1
done
echo "OIDC server is up."

# Wait for database API to be ready (port 8000)
echo "Waiting for database API to be ready..."
while ! nc -z localhost 8000; do
  sleep 1
done
echo "Database API is up."

# Wait for MCP server to be ready (port 9000)
echo "Waiting for MCP server to be ready..."
while ! nc -z localhost 9000; do
  sleep 1
done
echo "MCP server is up. Running agent."

# Run the agent (uncomment if you want to run it here)
# python3 agents/sql_agent/main.py

echo "All services are running. Press Ctrl+C to stop and clean up."
while true; do sleep 3600; done
