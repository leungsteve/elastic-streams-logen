#!/bin/bash

# Elastic Streams Log Generator Setup Script

set -e  # Exit on any error

echo "=========================================="
echo "Elastic Streams Log Generator Setup"
echo "=========================================="

# Check if Python 3 is installed
if ! command -v python3 &> /dev/null; then
    echo "Error: Python 3 is required but not installed."
    echo "Please install Python 3.8 or higher."
    exit 1
fi

# Create virtual environment if it doesn't exist
if [ ! -d "venv" ]; then
    echo "Creating virtual environment..."
    python3 -m venv venv
else
    echo "Virtual environment already exists."
fi

# Activate virtual environment and install dependencies
echo "Installing dependencies..."
source venv/bin/activate
pip install --upgrade pip
pip install -r requirements.txt

echo ""
echo "=========================================="
echo "Setup Complete!"
echo "=========================================="
echo ""
echo "To start generating logs:"
echo "  1. Activate the virtual environment:"
echo "     source venv/bin/activate"
echo ""
echo "  2. Check the current configuration:"
echo "     python main.py --status"
echo ""
echo "  3. Start log generation:"
echo "     python main.py"
echo ""
echo "  4. Or run for a specific duration (e.g., 5 minutes):"
echo "     python main.py --duration 300"
echo ""
echo "Configuration file: config.yaml"
echo "Generated logs will be stored in: ./logs/"
echo ""
echo "For Filebeat integration:"
echo "  1. Update filebeat.yml with your Elastic Cloud credentials"
echo "  2. Start Filebeat: filebeat -c filebeat.yml"
echo ""
echo "=========================================="