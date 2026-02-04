#!/bin/bash
# Set ERPNext environment variables for bash

export ERPNEXT_BASE_URL="http://localhost:8080"
export ERPNEXT_API_KEY="c1ac1b04200e7e9"
export ERPNEXT_API_SECRET="0f20d3f8eedc30b"

echo "✓ Environment variables set:"
echo "  ERPNEXT_BASE_URL=$ERPNEXT_BASE_URL"
echo "  ERPNEXT_API_KEY=$ERPNEXT_API_KEY"
echo "  ERPNEXT_API_SECRET=*** (hidden)"

echo ""
echo "To verify configuration, run:"
echo "  python check_erpnext_config.py"
echo ""
echo "To start the server, run:"
echo "  python run.py"
