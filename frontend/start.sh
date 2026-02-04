#!/bin/bash
# Start React frontend - fixes PATH for Git Bash

echo "Setting up Node.js PATH for Git Bash..."
echo ""

# Add Node.js to PATH for this session
export PATH="/c/Program Files/nodejs:$PATH"

# Verify Node.js is accessible
if command -v node &> /dev/null; then
    echo "SUCCESS: Node.js $(node --version) found"
    echo "SUCCESS: npm $(npm --version) found"
    echo ""
else
    echo "Node.js still not found. Trying alternative path..."
    export PATH="/c/Program Files (x86)/nodejs:$PATH"
    
    if command -v node &> /dev/null; then
        echo "SUCCESS: Node.js $(node --version) found"
        echo "SUCCESS: npm $(npm --version) found"
        echo ""
    else
        echo "ERROR: Node.js not found. Please check installation."
        echo "Expected location: C:\\Program Files\\nodejs\\"
        exit 1
    fi
fi

# Check if node_modules exists
if [ ! -d "node_modules" ]; then
    echo "Installing dependencies - first time setup..."
    echo "This may take a few minutes..."
    npm install
    
    if [ $? -ne 0 ]; then
        echo "ERROR: Failed to install dependencies"
        exit 1
    fi
    echo "Dependencies installed successfully!"
    echo ""
else
    echo "Dependencies already installed"
    echo ""
fi

echo "Starting React development server..."
echo ""
echo "The frontend will be available at: http://localhost:3000"
echo "Press Ctrl+C to stop the server"
echo ""

npm run dev
