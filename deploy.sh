#!/bin/bash
# Run tests
python -m pytest

# Build and run with Docker
docker compose up --build -d

# Wait for services
sleep 10

# Health check
curl -f http://localhost:8000/health || exit 1

echo "✅ Backend deployed successfully"