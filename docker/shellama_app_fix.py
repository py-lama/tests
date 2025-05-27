#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
SheLLama - REST API for shell and filesystem operations

This module provides a Flask-based REST API for executing shell commands
and performing filesystem operations.
"""

import os
import sys
import argparse
from pathlib import Path
from flask import Flask, jsonify, request, g
import logging

# Import SheLLama modules
from shellama.logging_config import init_logging, get_logger
from shellama import file_ops, dir_ops, shell, git_ops

# Initialize logging
init_logging()
logger = get_logger()

# Define function to initialize the app
def init_app(app):
    """
    Initialize the Flask application with logging and configuration.
    
    Args:
        app (Flask): The Flask application instance.
    """
    # Set up request logging
    @app.before_request
    def before_request():
        g.start_time = os.times()
        logger.info(f"Request started: {request.method} {request.path}")

    @app.after_request
    def after_request(response):
        if hasattr(g, 'start_time'):
            end_time = os.times()
            user_time = end_time.user - g.start_time.user
            sys_time = end_time.system - g.start_time.system
            logger.info(f"Request completed: {request.method} {request.path} - Status: {response.status_code} - Time: {user_time+sys_time:.4f}s")
        return response
    
    return app

def create_app(test_config=None):
    """
    Create and configure the Flask application.
    
    Args:
        test_config (dict, optional): Test configuration to override default config.
        
    Returns:
        Flask: The configured Flask application.
    """
    # Create and configure the app
    app = Flask(__name__, instance_relative_config=True)
    app.config.from_mapping(
        SECRET_KEY=os.environ.get('SECRET_KEY', 'dev'),
        DEBUG=os.environ.get('DEBUG', 'True').lower() in ('true', '1', 't'),
    )
    
    # Override with test config if provided
    if test_config is not None:
        app.config.update(test_config)
    
    # Initialize the logger
    init_app(app)
    
    # Health check endpoint
    @app.route('/health', methods=['GET'])
    def health_check():
        return jsonify({'status': 'ok', 'service': 'shellama'})
    
    # File operations endpoints
    @app.route('/files', methods=['GET'])
    def get_files():
        directory = request.args.get('directory', '.')
        pattern = request.args.get('pattern', '*')
        recursive = request.args.get('recursive', 'false').lower() in ('true', '1', 't')
        
        try:
            files = file_ops.list_files(directory, pattern, recursive)
            return jsonify({'files': files})
        except Exception as e:
            logger.error(f"Error listing files: {str(e)}")
            return jsonify({'error': str(e)}), 500
    
    @app.route('/files', methods=['POST'])
    def create_file():
        data = request.get_json()
        
        if not data or 'path' not in data or 'content' not in data:
            return jsonify({'error': 'Missing required fields: path and content'}), 400
        
        try:
            file_ops.write_file(data['path'], data['content'])
            return jsonify({'success': True, 'path': data['path']})
        except Exception as e:
            logger.error(f"Error creating file: {str(e)}")
            return jsonify({'error': str(e)}), 500
    
    @app.route('/files/<path:file_path>', methods=['GET'])
    def read_file(file_path):
        try:
            content = file_ops.read_file(file_path)
            return jsonify({'content': content, 'path': file_path})
        except Exception as e:
            logger.error(f"Error reading file: {str(e)}")
            return jsonify({'error': str(e)}), 500
    
    @app.route('/files/<path:file_path>', methods=['PUT'])
    def update_file(file_path):
        data = request.get_json()
        
        if not data or 'content' not in data:
            return jsonify({'error': 'Missing required field: content'}), 400
        
        try:
            file_ops.write_file(file_path, data['content'])
            return jsonify({'success': True, 'path': file_path})
        except Exception as e:
            logger.error(f"Error updating file: {str(e)}")
            return jsonify({'error': str(e)}), 500
    
    @app.route('/files/<path:file_path>', methods=['DELETE'])
    def delete_file(file_path):
        try:
            file_ops.delete_file(file_path)
            return jsonify({'success': True, 'path': file_path})
        except Exception as e:
            logger.error(f"Error deleting file: {str(e)}")
            return jsonify({'error': str(e)}), 500
    
    # Directory operations endpoints
    @app.route('/directories', methods=['GET'])
    def get_directories():
        parent = request.args.get('parent', '.')
        recursive = request.args.get('recursive', 'false').lower() in ('true', '1', 't')
        
        try:
            directories = dir_ops.list_directories(parent, recursive)
            return jsonify({'directories': directories})
        except Exception as e:
            logger.error(f"Error listing directories: {str(e)}")
            return jsonify({'error': str(e)}), 500
    
    @app.route('/directories', methods=['POST'])
    def create_directory():
        data = request.get_json()
        
        if not data or 'path' not in data:
            return jsonify({'error': 'Missing required field: path'}), 400
        
        try:
            dir_ops.create_directory(data['path'])
            return jsonify({'success': True, 'path': data['path']})
        except Exception as e:
            logger.error(f"Error creating directory: {str(e)}")
            return jsonify({'error': str(e)}), 500
    
    @app.route('/directories/<path:dir_path>', methods=['DELETE'])
    def delete_directory(dir_path):
        recursive = request.args.get('recursive', 'false').lower() in ('true', '1', 't')
        
        try:
            dir_ops.delete_directory(dir_path, recursive)
            return jsonify({'success': True, 'path': dir_path})
        except Exception as e:
            logger.error(f"Error deleting directory: {str(e)}")
            return jsonify({'error': str(e)}), 500
    
    # Shell command endpoints
    @app.route('/shell', methods=['POST'])
    def execute_command():
        data = request.get_json()
        
        if not data or 'command' not in data:
            return jsonify({'error': 'Missing required field: command'}), 400
        
        working_dir = data.get('working_dir', '.')
        timeout = data.get('timeout', 30)
        
        try:
            result = shell.execute_command(data['command'], working_dir, timeout)
            return jsonify({
                'command': data['command'],
                'working_dir': working_dir,
                'stdout': result['stdout'],
                'stderr': result['stderr'],
                'exit_code': result['exit_code'],
                'timed_out': result['timed_out']
            })
        except Exception as e:
            logger.error(f"Error executing command: {str(e)}")
            return jsonify({'error': str(e)}), 500
    
    # Git operations endpoints
    @app.route('/git/status', methods=['GET'])
    def git_status():
        repo_path = request.args.get('repo_path', '.')
        
        try:
            status = git_ops.get_status(repo_path)
            return jsonify(status)
        except Exception as e:
            logger.error(f"Error getting git status: {str(e)}")
            return jsonify({'error': str(e)}), 500
    
    @app.route('/git/log', methods=['GET'])
    def git_log():
        repo_path = request.args.get('repo_path', '.')
        max_count = request.args.get('max_count', 10, type=int)
        
        try:
            logs = git_ops.get_log(repo_path, max_count)
            return jsonify({'logs': logs})
        except Exception as e:
            logger.error(f"Error getting git log: {str(e)}")
            return jsonify({'error': str(e)}), 500
    
    @app.route('/git/branches', methods=['GET'])
    def git_branches():
        repo_path = request.args.get('repo_path', '.')
        
        try:
            branches = git_ops.get_branches(repo_path)
            return jsonify({'branches': branches})
        except Exception as e:
            logger.error(f"Error getting git branches: {str(e)}")
            return jsonify({'error': str(e)}), 500
    
    @app.route('/git/checkout', methods=['POST'])
    def git_checkout():
        data = request.get_json()
        
        if not data or 'branch' not in data:
            return jsonify({'error': 'Missing required field: branch'}), 400
        
        repo_path = data.get('repo_path', '.')
        
        try:
            result = git_ops.checkout_branch(repo_path, data['branch'])
            return jsonify({'success': result, 'branch': data['branch']})
        except Exception as e:
            logger.error(f"Error checking out git branch: {str(e)}")
            return jsonify({'error': str(e)}), 500
    
    @app.route('/git/commit', methods=['POST'])
    def git_commit():
        data = request.get_json()
        
        if not data or 'message' not in data:
            return jsonify({'error': 'Missing required field: message'}), 400
        
        repo_path = data.get('repo_path', '.')
        add_all = data.get('add_all', True)
        
        try:
            result = git_ops.commit(repo_path, data['message'], add_all)
            return jsonify({'success': True, 'commit_hash': result})
        except Exception as e:
            logger.error(f"Error creating git commit: {str(e)}")
            return jsonify({'error': str(e)}), 500
    
    @app.route('/git/pull', methods=['POST'])
    def git_pull():
        data = request.get_json()
        repo_path = data.get('repo_path', '.')
        remote = data.get('remote', 'origin')
        branch = data.get('branch', None)
        
        try:
            result = git_ops.pull(repo_path, remote, branch)
            return jsonify({'success': result})
        except Exception as e:
            logger.error(f"Error pulling git repository: {str(e)}")
            return jsonify({'error': str(e)}), 500
    
    @app.route('/git/push', methods=['POST'])
    def git_push():
        data = request.get_json()
        repo_path = data.get('repo_path', '.')
        remote = data.get('remote', 'origin')
        branch = data.get('branch', None)
        
        try:
            result = git_ops.push(repo_path, remote, branch)
            return jsonify({'success': result})
        except Exception as e:
            logger.error(f"Error pushing git repository: {str(e)}")
            return jsonify({'error': str(e)}), 500
    
    return app

def main():
    """
    Run the Flask application.
    
    This function is the entry point for the application when run directly.
    Supports both environment variables and command-line arguments.
    """
    # Parse command-line arguments
    parser = argparse.ArgumentParser(description='SheLLama API Server')
    parser.add_argument('--host', default=os.environ.get('HOST', '0.0.0.0'),
                        help='Host to bind the server to')
    parser.add_argument('--port', type=int, default=int(os.environ.get('PORT', 8002)),
                        help='Port to bind the server to')
    parser.add_argument('--debug', action='store_true', default=os.environ.get('DEBUG', 'False').lower() in ('true', '1', 't'),
                        help='Enable debug mode')
    args = parser.parse_args()
    
    # Create and run the app
    app = create_app()
    app.run(host=args.host, port=args.port, debug=args.debug)

if __name__ == '__main__':
    main()
