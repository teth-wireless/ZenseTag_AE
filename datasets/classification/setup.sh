#!/bin/bash

# Check if Python 3 is installed
if ! command -v python3 &> /dev/null; then
    echo "Python 3 is not installed. Installing Python 3..."
    sudo apt-get update && sudo apt-get install python3 -y
fi

# Check if pip3 is installed
if ! command -v pip3 &> /dev/null; then
    echo "pip3 is not installed. Installing pip3..."
    sudo apt-get install python3-pip -y
fi

# Create virtual environment
echo "Creating virtual environment..."
python3 -m venv py-zeta

# Activate virtual environment
echo "Activating virtual environment..."
source py-zeta/bin/activate

# Install dependencies
echo "Installing dependencies..."
pip3 install -r requirements.txt

# Deactivate virtual environment
echo "Deactivating virtual environment..."
deactivate

echo "Setup complete."
