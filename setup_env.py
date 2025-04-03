#!/usr/bin/env python
"""
Setup script for EI-harness-lite.

This script creates a virtual environment, activates it, and installs the package
and its dependencies. It's a convenience script for users who want to get started
quickly.
"""

import os
import platform
import subprocess
import sys

def main():
    """Create virtual environment and install dependencies."""
    print("Setting up EI-harness-lite environment...")
    
    # Check if virtual environment already exists
    if os.path.exists("venv"):
        print("Virtual environment already exists. Skipping creation.")
    else:
        print("Creating virtual environment...")
        subprocess.check_call([sys.executable, "-m", "venv", "venv"])
    
    # Determine the activate script based on the platform
    if platform.system() == "Windows":
        activate_script = os.path.join("venv", "Scripts", "activate")
        activate_cmd = f"{activate_script}"
        pip_cmd = os.path.join("venv", "Scripts", "pip")
    else:
        activate_script = os.path.join("venv", "bin", "activate")
        activate_cmd = f"source {activate_script}"
        pip_cmd = os.path.join("venv", "bin", "pip")
    
    # Install the package in development mode
    print("Installing package and dependencies...")
    
    if platform.system() == "Windows":
        # On Windows, we need to use a different approach
        subprocess.check_call([os.path.join("venv", "Scripts", "pip"), "install", "-e", "."])
    else:
        # On Unix-like systems, we can use a shell command
        subprocess.check_call(f"source {activate_script} && pip install -e .", shell=True)
    
    print("\nSetup complete!")
    print("\nTo activate the virtual environment:")
    if platform.system() == "Windows":
        print(f"    {activate_script}")
    else:
        print(f"    {activate_cmd}")
    
    print("\nTo run the Streamlit app:")
    print("    streamlit run app.py")
    
    print("\nTo run the tests:")
    print("    python test_harness.py")
    print("    pytest")
    
    print("\nTo use the CLI:")
    print("    ei-harness-lite --help")
    
    print("\nMake sure to set your API key in a .env file or as an environment variable:")
    print("    OPENAI_API_KEY=your-api-key")

if __name__ == "__main__":
    main()
