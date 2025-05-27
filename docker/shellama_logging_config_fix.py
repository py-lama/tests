#!/usr/bin/env python3

"""
Shellama Logging Configuration

This module configures logging for the Shellama application.
It attempts to find and use the PyLogs library for centralized logging.
"""

import os
import sys
import logging
from pathlib import Path

# Try to find PyLogs in the parent directory
parent_dir = Path(__file__).resolve().parent.parent.parent
loglama_path = parent_dir / 'loglama'

# Add PyLogs to the path if it exists
if loglama_path.exists() and str(loglama_path) not in sys.path:
    sys.path.insert(0, str(loglama_path))
    print(f"Added PyLogs path: {loglama_path}")
else:
    # Try an alternative path calculation
    alt_pylogs_path = Path('/app/loglama')
    if alt_pylogs_path.exists() and str(alt_pylogs_path) not in sys.path:
        sys.path.insert(0, str(alt_pylogs_path))
        print(f"Added alternative PyLogs path: {alt_pylogs_path}")

# Import PyLogs components
try:
    from loglama.config.env_loader import load_env, get_env
    from loglama.utils import configure_logging, LogContext, capture_context
    PYLOGS_AVAILABLE = True
except ImportError:
    print("Warning: PyLogs not found. Using basic logging configuration.")
    PYLOGS_AVAILABLE = False

# Load environment variables
if PYLOGS_AVAILABLE:
    load_env()

# Configure basic logging as a fallback
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S'
)

def init_logging():
    """
    Initialize logging for Shellama using PyLogs.
    
    This function should be called at the very beginning of the application
    before any other imports or configurations are done.
    """
    # Set up environment variables
    os.environ.setdefault('APP_NAME', 'shellama')
    os.environ.setdefault('LOG_LEVEL', 'INFO')
    
    # Configure logging with PyLogs if available
    if PYLOGS_AVAILABLE:
        try:
            # Get configuration from environment
            log_level = get_env('LOG_LEVEL', 'INFO')
            app_name = get_env('APP_NAME', 'shellama')
            log_file = get_env('LOG_FILE', None)
            
            # Configure logging
            configure_logging(
                level=log_level,
                app_name=app_name,
                log_file=log_file,
                console=True,
                json_format=False
            )
            
            print(f"Logging initialized with PyLogs: level={log_level}, app={app_name}")
            return True
        except Exception as e:
            print(f"Error initializing PyLogs: {e}")
            print("Falling back to basic logging configuration.")
    
    # If PyLogs is not available or configuration failed, use basic logging
    print("Using basic logging configuration.")
    return False

def get_logger(name=None):
    """
    Get a logger instance.
    
    Args:
        name (str, optional): Name of the logger. Defaults to 'shellama'.
        
    Returns:
        Logger: A configured logger instance.
    """
    if name is None:
        name = 'shellama'
        
    if PYLOGS_AVAILABLE:
        # Use PyLogs context capture if available
        try:
            return logging.getLogger(name)
        except Exception as e:
            print(f"Error getting PyLogs logger: {e}")
    
    # Fallback to standard logging
    return logging.getLogger(name)
