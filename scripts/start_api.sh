#!/bin/bash

# Start the Flask API server
# Set FLASK_DEBUG=true for development, false for production
# Set FLASK_PORT to change the port (default: 5000)

cd "$(dirname "$0")/.." || exit 1

# Activate virtual environment if it exists
if [ -d "venv" ]; then
  source venv/bin/activate
fi

# Run the API
python api.py

