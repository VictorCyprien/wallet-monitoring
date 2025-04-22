#!/bin/bash
# run_api.sh - Script to run the Solana Wallet Token Monitor API

# Navigate to script directory
cd "$(dirname "$0")"

# Activate virtual environment if it exists
if [ -d "venv" ]; then
    source venv/bin/activate
fi

# Run the API server - only bind to localhost for security
uvicorn api:app --host 127.0.0.1 --port 8001

echo "API server started at http://localhost:8000" 