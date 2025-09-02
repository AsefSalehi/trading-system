#!/bin/bash

echo "🚀 Trading System - Backend Startup"
echo "===================================="
echo ""
echo "The backend implementation is located in the Bakend/ directory."
echo "Navigating to Bakend/ and starting setup..."
echo ""

cd Bakend/

if [ -f "setup.sh" ]; then
    ./setup.sh
else
    echo "❌ setup.sh not found in Bakend/ directory"
    echo "Please navigate to Bakend/ manually and run ./setup.sh"
fi