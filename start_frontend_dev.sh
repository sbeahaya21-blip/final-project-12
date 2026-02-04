#!/bin/bash
# Start frontend development server

echo "Starting Frontend Development Server..."
echo ""

# Fix PATH for Node.js
export PATH="/c/Program Files/nodejs:$PATH"

# Verify Node.js
if ! command -v node &> /dev/null; then
    echo "ERROR: Node.js not found in PATH"
    echo "Please make sure Node.js is installed"
    exit 1
fi

echo "Node.js $(node --version) found"
echo "npm $(npm --version) found"
echo ""

# Navigate to frontend directory
cd frontend || exit 1

# Check if node_modules exists
if [ ! -d "node_modules" ]; then
    echo "Installing dependencies (first time)..."
    npm install
    if [ $? -ne 0 ]; then
        echo "ERROR: Failed to install dependencies"
        exit 1
    fi
    echo ""
fi

echo "Starting development server..."
echo "Frontend will be available at: http://localhost:3000"
echo "Press Ctrl+C to stop"
echo ""

npm run dev
