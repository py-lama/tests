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
    
    # Install pyllm package
    pyllm_dir = project_root / "pyllm"
    if not pyllm_dir.exists():
        print(f"Error: {pyllm_dir} does not exist")
        return False
    
    print("\n=== Installing pyllm package ===")
    if not run_command([sys.executable, "-m", "pip", "install", "-e", "."], cwd=pyllm_dir):
        return False
    
    # Install pylama package
    pylama_dir = project_root / "pylama"
    if not pylama_dir.exists():
        print(f"Error: {pylama_dir} does not exist")
        return False
    
    print("\n=== Installing pylama package ===")
    if not run_command([sys.executable, "-m", "pip", "install", "-e", "."], cwd=pylama_dir):
        return False
    
    print("\n=== Installation completed successfully ===")
    print("You can now use PyLama by running:")
    print("  pylama -h")
    print("Or in interactive mode:")
    print("  pylama -i")
    
    return True


if __name__ == "__main__":
    sys.exit(0 if main() else 1)
