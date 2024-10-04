
# Project Setup Guide

## Introduction
This project requires a Python environment with specific dependencies to be installed for proper functioning. This guide will walk you through setting up the environment and installing the required dependencies.

### Prerequisites
- **Python 3.x**: Ensure that Python 3.x is installed on your system.
- **Pip**: The Python package installer should also be available.

## Setup Instructions

### For Linux/MacOS Users:
1. **Install Python 3 and Pip** (if not already installed):
   - Run the `setup.sh` script to automatically install Python 3 and Pip if they are missing.
   - It also sets up a Python virtual environment and installs the required dependencies.

   **To execute the setup script:**
   ```bash
   chmod +x setup.sh
   ./setup.sh
   ```

2. **Activate Virtual Environment:**
   Once the environment is created, you can activate it manually by running:
   ```bash
   source py-diff-z/bin/activate
   ```

3. **Install Dependencies:**
   If you need to manually install the dependencies:
   ```bash
   pip3 install -r requirements.txt
   ```

4. **Deactivate Virtual Environment:**
   When you are done working in the environment, you can deactivate it:
   ```bash
   deactivate
   ```

### For Windows Users:
1. **Run the setup script**:
   You can run `setup.bat` to set up the Python environment and install dependencies.
   - **To run**: Open Command Prompt and execute the following:
   ```cmd
   setup.bat
   ```

## Cleanup Instructions

To clean up the environment after you're done working or if you want to start fresh:
1. **Run the cleanup script**:
   ```bash
   chmod +x cleanup.sh
   ./cleanup.sh
   ```
   This script will:
   - Deactivate the virtual environment (if it's active).
   - Remove the virtual environment directory (`py-diff-z`).
   - Uninstall all dependencies listed in `requirements.txt` from the current environment.

## Dependencies
The required dependencies for this project are listed in `requirements.txt`:
```text
fastdtw==0.3.4
matplotlib==3.8.4
numpy==1.26.4
PyQt5==5.15.10
PyQt5-Qt5==5.15.2
PyQt5_sip==12.13.0
pyqtgraph==0.13.4
scikit_learn==1.4.2
scipy==1.13.0
git+https://github.com/ransford/sllurp.git
```

Ensure that these packages are correctly installed in your virtual environment.

## Additional Information
For any additional configurations or troubleshooting, please refer to the individual script files or contact the project maintainer (tetheredwireless@gmail.com).
