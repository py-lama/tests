"""
Pytest configuration and fixtures
"""
import os
import sys
from pathlib import Path

# Add the project root directory to the Python path
project_root = Path(__file__).parent.resolve()
sys.path.insert(0, str(project_root))
sys.path.insert(0, str(project_root / "python"))
sys.path.insert(0, str(project_root / "python" / "src"))

# Ensure the dialogchain package is importable
import dialogchain
print(f"dialogchain module path: {dialogchain.__file__}")
