#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
WebLama Microservices Monitoring

This script monitors the health of all WebLama microservices and reports their status.
"""

import requests
import time
import json
import os
from datetime import datetime
from rich.console import Console
from rich.table import Table
from rich.panel import Panel

# Initialize rich console
console = Console()

# Service endpoints
SERVICES = {
    "Bexy": "http://localhost:8000/health",
    "PyLLM": "http://localhost:8001/health",
    "PyLama": "http://localhost:8002/health",
    "WebLama": "http://localhost:5000/health"
}

def check_service_health(name, url):
    """
    Check the health of a service and return its status
    
    Args:
        name (str): The name of the service
        url (str): The health check URL
        
    Returns:
        dict: The service status information
    """
    try:
        response = requests.get(url, timeout=5)
        if response.status_code == 200:
            data = response.json()
            return {
                "name": name,
                "status": data.get("status", "unknown"),
                "version": data.get("version", "unknown"),
                "response_time": response.elapsed.total_seconds(),
                "code": response.status_code,
                "error": None
            }
        else:
            return {
                "name": name,
                "status": "error",
                "version": "unknown",
                "response_time": response.elapsed.total_seconds(),
                "code": response.status_code,
                "error": f"HTTP {response.status_code}"
            }
    except requests.RequestException as e:
        return {
            "name": name,
            "status": "offline",
            "version": "unknown",
            "response_time": 0,
            "code": 0,
            "error": str(e)
        }

def display_status(results):
    """
    Display the service status in a rich table
    
    Args:
        results (list): List of service status dictionaries
    """
    table = Table(title="WebLama Microservices Status")
    
    table.add_column("Service", style="cyan")
    table.add_column("Status", style="green")
    table.add_column("Version", style="blue")
    table.add_column("Response Time", style="magenta")
    table.add_column("Error", style="red")
    
    for result in results:
        status_style = "green" if result["status"] == "healthy" else "red"
        
        table.add_row(
            result["name"],
            f"[{status_style}]{result['status']}",
            result["version"],
            f"{result['response_time']:.4f}s",
            result["error"] or ""
        )
    
    console.print(table)

def log_status(results, log_file="service_status.log"):
    """
    Log the service status to a file
    
    Args:
        results (list): List of service status dictionaries
        log_file (str): Path to the log file
    """
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    log_entry = {
        "timestamp": timestamp,
        "services": results
    }
    
    with open(log_file, "a") as f:
        f.write(json.dumps(log_entry) + "\n")

def monitor_services(interval=60, log=True):
    """
    Monitor services continuously
    
    Args:
        interval (int): Monitoring interval in seconds
        log (bool): Whether to log results to a file
    """
    try:
        while True:
            console.print(Panel(f"Checking services at {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}", 
                               style="blue"))
            
            results = []
            for name, url in SERVICES.items():
                result = check_service_health(name, url)
                results.append(result)
            
            display_status(results)
            
            if log:
                log_status(results)
            
            if interval <= 0:
                break
                
            console.print(f"\nNext check in {interval} seconds. Press Ctrl+C to exit.\n")
            time.sleep(interval)
            
    except KeyboardInterrupt:
        console.print("\n[bold yellow]Monitoring stopped by user.[/bold yellow]")

def main():
    """
    Main function
    """
    console.print(Panel.fit("WebLama Microservices Monitoring", style="bold green"))
    
    # Parse command line arguments
    import argparse
    parser = argparse.ArgumentParser(description="Monitor WebLama microservices")
    parser.add_argument("-i", "--interval", type=int, default=60,
                        help="Monitoring interval in seconds (default: 60, 0 for single check)")
    parser.add_argument("--no-log", action="store_true", help="Disable logging to file")
    args = parser.parse_args()
    
    # Start monitoring
    monitor_services(interval=args.interval, log=not args.no_log)

if __name__ == "__main__":
    main()
