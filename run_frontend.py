#!/usr/bin/env python3
"""
VC Copilot Frontend Runner
--------------------------
This script manages the Next.js frontend server for the VC Copilot application.
It can start, stop, or restart the frontend server.
"""

import os
import sys
import signal
import subprocess
import time
import argparse
import json
from pathlib import Path

# Default port for the frontend server
DEFAULT_PORT = 3000
FRONTEND_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'frontend')

def find_process_on_port(port):
    """Find process ID using the specified port"""
    try:
        # Use lsof to find process using the port
        cmd = f"lsof -i :{port} -t"
        result = subprocess.run(cmd, shell=True, text=True, capture_output=True)
        if result.stdout.strip():
            return result.stdout.strip()
        return None
    except Exception as e:
        print(f"Error checking port: {e}")
        return None

def kill_process(pid):
    """Kill process with the specified PID"""
    try:
        os.kill(int(pid), signal.SIGTERM)
        print(f"Process {pid} terminated.")
        # Give it a moment to shut down
        time.sleep(1)
        return True
    except ProcessLookupError:
        print(f"Process {pid} not found.")
        return False
    except Exception as e:
        print(f"Error killing process: {e}")
        return False

def get_npm_script(script_name="dev"):
    """Check if the specified npm script exists in package.json"""
    try:
        package_json_path = os.path.join(FRONTEND_DIR, 'package.json')
        if not os.path.exists(package_json_path):
            print(f"Error: package.json not found at {package_json_path}")
            return None
            
        with open(package_json_path, 'r') as f:
            package_data = json.load(f)
            
        if 'scripts' in package_data and script_name in package_data['scripts']:
            return script_name
            
        # If requested script doesn't exist, find alternatives
        if 'scripts' in package_data:
            available_scripts = list(package_data['scripts'].keys())
            print(f"Script '{script_name}' not found. Available scripts: {', '.join(available_scripts)}")
            
            # Try to find a suitable alternative
            alternatives = ['start', 'serve', 'dev', 'develop', 'development']
            for alt in alternatives:
                if alt in package_data['scripts']:
                    print(f"Using '{alt}' script instead.")
                    return alt
                    
        return None
    except Exception as e:
        print(f"Error reading package.json: {e}")
        return None

def check_node_modules():
    """Check if node_modules directory exists, if not, install dependencies"""
    node_modules_path = os.path.join(FRONTEND_DIR, 'node_modules')
    if not os.path.exists(node_modules_path):
        print("Node modules not found. Installing dependencies...")
        try:
            subprocess.run(["npm", "install"], cwd=FRONTEND_DIR, check=True)
            print("Dependencies installed successfully.")
        except subprocess.CalledProcessError as e:
            print(f"Error installing dependencies: {e}")
            return False
    return True

def start_frontend(port=DEFAULT_PORT, script_name="dev"):
    """Start the frontend server"""
    # First check if node_modules exists
    if not check_node_modules():
        return False
        
    # Find the appropriate npm script
    script = get_npm_script(script_name)
    if not script:
        print("Could not find a suitable npm script to run the frontend.")
        return False
    
    print(f"Starting VC Copilot frontend server on port {port}...")
    print("Press Ctrl+C to stop the server")
    
    # Set environment variables for the frontend
    env = os.environ.copy()
    env["PORT"] = str(port)
    
    try:
        # Run the npm script
        subprocess.run(["npm", "run", script], cwd=FRONTEND_DIR, env=env)
        return True
    except KeyboardInterrupt:
        print("\nFrontend server stopped.")
        return True
    except Exception as e:
        print(f"Error starting frontend: {e}")
        return False

def update_next_config(backend_port):
    """Update the Next.js config to point to the correct backend port"""
    next_config_path = os.path.join(FRONTEND_DIR, 'next.config.js')
    if not os.path.exists(next_config_path):
        print(f"Warning: next.config.js not found at {next_config_path}")
        return False
        
    try:
        with open(next_config_path, 'r') as f:
            config_content = f.read()
            
        # Update the backend port in the config
        updated_content = config_content.replace(
            'destination: \'http://localhost:8000/:path*\'',
            f'destination: \'http://localhost:{backend_port}/:path*\''
        ).replace(
            'destination: \'http://localhost:8001/:path*\'',
            f'destination: \'http://localhost:{backend_port}/:path*\''
        )
        
        if updated_content != config_content:
            with open(next_config_path, 'w') as f:
                f.write(updated_content)
            print(f"Updated next.config.js to use backend port {backend_port}")
            return True
        else:
            print("No changes needed in next.config.js")
            return True
    except Exception as e:
        print(f"Error updating next.config.js: {e}")
        return False

def main():
    """Main function to handle frontend server operations"""
    parser = argparse.ArgumentParser(description="VC Copilot Frontend Server Manager")
    parser.add_argument("--port", type=int, default=DEFAULT_PORT, help=f"Port to run the frontend server on (default: {DEFAULT_PORT})")
    parser.add_argument("--backend-port", type=int, default=8001, help="Port where the backend server is running (default: 8001)")
    parser.add_argument("--script", type=str, default="dev", help="NPM script to run (default: dev)")
    parser.add_argument("--action", choices=["start", "stop", "restart"], default="start", help="Action to perform (default: start)")
    
    args = parser.parse_args()
    port = args.port
    backend_port = args.backend_port
    script = args.script
    action = args.action
    
    # Check if port is in use
    pid = find_process_on_port(port)
    
    if action == "stop" or action == "restart":
        if pid:
            print(f"Stopping process {pid} on port {port}...")
            kill_process(pid)
        else:
            print(f"No process found running on port {port}.")
        
        if action == "stop":
            return
    
    # If starting or restarting, check again to make sure port is free
    if action == "start" or action == "restart":
        pid = find_process_on_port(port)
        if pid:
            print(f"Port {port} is still in use by process {pid}. Cannot start server.")
            print("Please use a different port or stop the process first.")
            return
        
        # Update next.config.js to point to the correct backend port
        update_next_config(backend_port)
            
        # Start the frontend
        start_frontend(port, script)

if __name__ == "__main__":
    main()
