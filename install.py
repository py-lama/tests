#!/usr/bin/env python3

import os
import sys
import subprocess
from pathlib import Path


def run_command(cmd, cwd=None):
    """Run a shell command and return the output."""
    print(f"Running: {' '.join(cmd)}")
    result = subprocess.run(cmd, cwd=cwd, capture_output=True, text=True)
    if result.returncode != 0:
        print(f"Error: {result.stderr}")
        return False
    print(result.stdout)
    return True


def main():
    """Install the PyLama project and its dependencies."""
    # Get the project root directory
    project_root = Path(__file__).parent.absolute()
    print(f"Project root: {project_root}")
    
    # Install bexy package
    bexy_dir = project_root / "bexy"
    if not bexy_dir.exists():
        print(f"Error: {bexy_dir} does not exist")
        return False
    
    print("\n=== Installing bexy package ===")
    if not run_command([sys.executable, "-m", "pip", "install", "-e", "."], cwd=bexy_dir):
        return False
    
    # Install getllm package
    getllm_dir = project_root / "getllm"
    if not getllm_dir.exists():
        print(f"Error: {getllm_dir} does not exist")
        return False
    
    print("\n=== Installing getllm package ===")
    if not run_command([sys.executable, "-m", "pip", "install", "-e", "."], cwd=getllm_dir):
        return False
    
    # Install devlama package
    devlama_dir = project_root / "devlama"
    if not devlama_dir.exists():
        print(f"Error: {devlama_dir} does not exist")
        return False
    
    print("\n=== Installing devlama package ===")
    if not run_command([sys.executable, "-m", "pip", "install", "-e", "."], cwd=devlama_dir):
        return False
    
    print("\n=== Installation completed successfully ===")
    print("You can now use PyLama by running:")
    print("  devlama -h")
    print("Or in interactive mode:")
    print("  devlama -i")
    
    return True


if __name__ == "__main__":
    sys.exit(0 if main() else 1)
