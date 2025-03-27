#!/bin/bash

# Set the base directory to the script location
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" &> /dev/null && pwd )"
cd "$SCRIPT_DIR"

# Activate virtual environment if it exists
if [ -d "venv" ]; then
    source venv/bin/activate
fi

# Run the Python script
python main.py

# Log the execution time
echo "Script executed at $(date)" >> execution_log.txt 