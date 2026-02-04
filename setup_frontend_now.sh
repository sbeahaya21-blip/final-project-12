#!/bin/bash
# Quick setup script for React frontend

echo "🚀 Setting up React Frontend..."
echo ""

# Check if Node.js is installed
if ! command -v node &> /dev/null; then
    echo "❌ Node.js is not found in PATH"
    echo ""
    echo "Please:"
    echo "1. Make sure Node.js is installed"
    echo "2. Restart your terminal/Git Bash"
    echo "3. Try again"
    exit 1
fi

echo "✅ Node.js $(node --version) found"
echo "✅ npm $(npm --version) found"
echo ""

# Navigate to frontend directory
cd frontend || exit 1

echo "📦 Installing dependencies..."
npm install

if [ $? -ne 0 ]; then
    echo "❌ Failed to install dependencies"
    exit 1
fi

echo ""
echo "✅ Dependencies installed!"
echo ""
echo "🎉 Setup complete! Now you can run:"
echo "   npm run dev"
echo ""
echo "The React frontend will be available at: http://localhost:3000"
echo ""
