#!/bin/bash
# Setup script for frontend

echo "Setting up Invoice Parser Frontend..."
echo ""

# Check if Node.js is installed
if ! command -v node &> /dev/null; then
    echo "❌ Node.js is not installed. Please install Node.js 18+ first."
    exit 1
fi

# Check Node.js version
NODE_VERSION=$(node -v | cut -d'v' -f2 | cut -d'.' -f1)
if [ "$NODE_VERSION" -lt 18 ]; then
    echo "❌ Node.js version 18+ is required. Current version: $(node -v)"
    exit 1
fi

echo "✓ Node.js $(node -v) found"
echo ""

# Navigate to frontend directory
cd frontend || exit 1

# Install dependencies
echo "Installing dependencies..."
npm install

if [ $? -ne 0 ]; then
    echo "❌ Failed to install dependencies"
    exit 1
fi

echo "✓ Dependencies installed"
echo ""

# Build frontend
echo "Building frontend..."
npm run build

if [ $? -ne 0 ]; then
    echo "❌ Failed to build frontend"
    exit 1
fi

echo ""
echo "✅ Frontend setup complete!"
echo ""
echo "You can now:"
echo "  - Run 'npm run dev' in the frontend directory for development"
echo "  - Or start the backend server to serve the built frontend"
echo ""
