#!/usr/bin/env python3

"""
APILama Logging Configuration

This module configures logging for the APILama application.
It attempts to find and use the LogLama library for centralized logging.
"""

import os
import sys
import logging
import functools
from pathlib import Path
from flask import request, g

# Try to find LogLama in the parent directory
parent_dir = Path(__file__).resolve().parent.parent.parent
loglama_path = parent_dir / 'loglama'

# Add LogLama to the path if it exists
if loglama_path.exists() and str(loglama_path) not in sys.path:
    sys.path.insert(0, str(loglama_path))
    print(f"Added LogLama path: {loglama_path}")
else:
    # Try an alternative path calculation
    alt_loglama_path = Path('/app/loglama')
    if alt_loglama_path.exists() and str(alt_loglama_path) not in sys.path:
        sys.path.insert(0, str(alt_loglama_path))
        print(f"Added alternative LogLama path: {alt_loglama_path}")

# Import LogLama components
try:
    from loglama.config.env_loader import load_env, get_env
    from loglama.utils import configure_logging, LogContext, capture_context
    LOGLAMA_AVAILABLE = True
except ImportError as e:
    print(f"PyLogs import error: {e}")
    print("PyLogs package not available. Using default logging configuration.")
    LOGLAMA_AVAILABLE = False

# Define LogContext class if LogLama is not available
if not LOGLAMA_AVAILABLE:
    class LogContext:
        """Context manager for structured logging when LogLama is not available."""
        def __init__(self, **kwargs):
            self.context = kwargs
            
        def __enter__(self):
            return self
            
        def __exit__(self, exc_type, exc_val, exc_tb):
            pass

# Load environment variables
if LOGLAMA_AVAILABLE:
    load_env()

# Configure basic logging as a fallback
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S'
)

def init_logging():
    """
    Initialize logging for APILama using LogLama.
    
    This function should be called at the very beginning of the application
    before any other imports or configurations are done.
    """
    # Set up environment variables
    os.environ.setdefault('APP_NAME', 'apilama')
    os.environ.setdefault('LOG_LEVEL', 'INFO')
    
    # Configure logging with LogLama if available
    if LOGLAMA_AVAILABLE:
        try:
            # Get configuration from environment
            log_level = get_env('LOG_LEVEL', 'INFO')
            app_name = get_env('APP_NAME', 'apilama')
            log_file = get_env('LOG_FILE', None)
            
            # Configure logging
            configure_logging(
                level=log_level,
                app_name=app_name,
                log_file=log_file,
                console=True,
                json_format=False
            )
            
            print(f"Logging initialized with LogLama: level={log_level}, app={app_name}")
            return True
        except Exception as e:
            print(f"Error initializing LogLama: {e}")
            print("Falling back to basic logging configuration.")
    
    # If LogLama is not available or configuration failed, use basic logging
    print("Using basic logging configuration.")
    return False

def get_logger(name=None):
    """
    Get a logger instance.
    
    Args:
        name (str, optional): Name of the logger. Defaults to 'apilama'.
        
    Returns:
        Logger: A configured logger instance.
    """
    if name is None:
        name = 'apilama'
        
    if LOGLAMA_AVAILABLE:
        # Use LogLama context capture if available
        try:
            return logging.getLogger(name)
        except Exception as e:
            print(f"Error getting LogLama logger: {e}")
    
    # Fallback to standard logging
    return logging.getLogger(name)

def log_request_context(func):
    """Decorator to log request context."""
    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        logger = get_logger()
        
        # Extract request information
        client_ip = request.remote_addr if request else "No IP"
        method = request.method if request else "No Method"
        url = request.url if request else "No URL"
        
        # Log request start
        logger.info(f"Request started: {method} {url} from {client_ip}")
        
        # Execute the wrapped function
        try:
            result = func(*args, **kwargs)
            logger.info(f"Request completed: {method} {url}")
            return result
        except Exception as e:
            logger.error(f"Request failed: {method} {url} - {str(e)}")
            raise
    
    return wrapper

def log_file_operation(operation):
    """Decorator to log file operations."""
    def decorator(func):
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            logger = get_logger()
            
            # Extract file path from args or kwargs
            file_path = None
            if args and isinstance(args[0], (str, Path)):
                file_path = args[0]
            elif 'path' in kwargs:
                file_path = kwargs['path']
            
            # Log operation start
            if file_path:
                logger.info(f"{operation} operation started on {file_path}")
            else:
                logger.info(f"{operation} operation started")
            
            # Execute the wrapped function
            try:
                result = func(*args, **kwargs)
                if file_path:
                    logger.info(f"{operation} operation completed on {file_path}")
                else:
                    logger.info(f"{operation} operation completed")
                return result
            except Exception as e:
                if file_path:
                    logger.error(f"{operation} operation failed on {file_path} - {str(e)}")
                else:
                    logger.error(f"{operation} operation failed - {str(e)}")
                raise
        
        return wrapper
    
    return decorator
