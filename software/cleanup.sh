#!/bin/bash

# Deactivate virtual environment if it is active
if [[ $VIRTUAL_ENV != "" ]]; then
    echo "Deactivating virtual environment..."
    deactivate
fi

# Remove virtual environment directory
if [[ -d "py-diff-z" ]]; then
    echo "Removing virtual environment directory..."
    rm -rf py-diff-z
fi

# Remove installed dependencies
if [[ -f "requirements.txt" ]]; then
    echo "Uninstalling dependencies..."
    pip uninstall -r requirements.txt -y
fi

echo "Cleanup complete."