#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Main entry point for the PyLama package.

This module allows the PyLama package to be executed directly with 'python -m devlama'.
It redirects to the appropriate module based on the command-line arguments.
"""

import sys
import os

def main():
    """Main entry point for the PyLama package."""
    # Import here to avoid circular imports
    from devlama.api import main as api_main
    
    # Run the API server by default
    api_main()

if __name__ == "__main__":
    main()
