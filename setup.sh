#!/bin/bash
set -e

# --- Backend Setup ---
echo "--- Setting up Python backend ---"

# Check for python3
if ! command -v python3 &> /dev/null
then
    echo "python3 could not be found. Please install Python 3."
    exit 1
fi

# Create a virtual environment
echo "Creating Python virtual environment in '.venv'..."
python3 -m venv .venv

# Activate the virtual environment and install dependencies
echo "Installing backend dependencies from requirements.txt..."
source .venv/bin/activate
pip install -r requirements.txt
deactivate

echo "Backend setup complete."
echo ""

# --- Frontend Setup ---
echo "--- Setting up Node.js frontend ---"

# Check for npm
if ! command -v npm &> /dev/null
then
    echo "npm could not be found. Please install Node.js and npm."
    exit 1
fi

# Install frontend dependencies
if [ -d "frontend" ]; then
  echo "Navigating to 'frontend' directory..."
  cd frontend
  echo "Installing frontend dependencies with npm..."
  npm install
  cd ..
else
  echo "Warning: 'frontend' directory not found. Skipping frontend setup."
fi

echo "Frontend setup complete."
echo ""
echo "Setup finished successfully!"
echo "Run 'start.sh' (on Linux/macOS) or 'start.bat' (on Windows) to start the servers." 