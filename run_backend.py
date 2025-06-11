#!/usr/bin/env python3
"""
Simplified VC Copilot Backend Runner
-----------------------------------
This script starts the simplified FastAPI backend server with CORS enabled
to allow the frontend to communicate with it. It also handles stopping any
existing process running on the specified port.
"""

import os
import sys
import signal
import subprocess
import time
import argparse
from dotenv import load_dotenv

# Default port for the backend server
DEFAULT_PORT = 8001

def load_environment():
    """Load environment variables from backend/.env file"""
    backend_env_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'backend', '.env')
    load_dotenv(backend_env_path)
    print(f"Loading environment variables from: {backend_env_path}")
    
    # Check for OpenAI API key
    if not os.environ.get("OPENAI_API_KEY"):
        print("Warning: OPENAI_API_KEY environment variable not set.")
        print("Please set it in your .env file or export it in your shell.")
        print("Example: export OPENAI_API_KEY='your-api-key'")
        return False
    return True

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

def start_backend(port=DEFAULT_PORT):
    """Start the backend server"""
    print(f"Starting VC Copilot backend server on port {port}...")
    print("Press Ctrl+C to stop the server")
    
    # Add the project root to Python path
    project_root = os.path.dirname(os.path.abspath(__file__))
    sys.path.insert(0, project_root)
    
    try:
        # Run the server with CORS enabled
        subprocess.run([
            sys.executable, "-m", "uvicorn", 
            "backend.main:app", 
            "--host", "0.0.0.0", 
            "--port", str(port), 
            "--reload"
        ])
    except KeyboardInterrupt:
        print("\nBackend server stopped.")
    except Exception as e:
        print(f"Error starting backend: {e}")

def main():
    """Main function to handle backend server operations"""
    parser = argparse.ArgumentParser(description="VC Copilot Backend Server Manager")
    parser.add_argument("--port", type=int, default=DEFAULT_PORT, help=f"Port to run the server on (default: {DEFAULT_PORT})")
    parser.add_argument("--action", choices=["start", "stop", "restart"], default="start", help="Action to perform (default: start)")
    
    args = parser.parse_args()
    port = args.port
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
        
        # Load environment variables
        if not load_environment():
            sys.exit(1)
            
        # Start the backend
        start_backend(port)

if __name__ == "__main__":
    main()
