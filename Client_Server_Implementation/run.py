"""
Simple script to start both the Todoist MCP server and client.
"""
import subprocess
import sys
import time
import os

def main():
    print("Starting Todoist MCP Assistant...")
    
    # Check if .env file exists
    if not os.path.exists('.env'):
        print("Error: .env file not found. Please create it with your API keys.")
        print("See README.md for setup instructions.")
        return
        
    # Start the server in a separate process
    print("\nStarting server...")
    server_process = subprocess.Popen(
        [sys.executable, "mcp_server.py"],
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True
    )
    
    # Give the server time to start
    print("Waiting for server to initialize...")
    time.sleep(3)
    
    # Check if server is still running
    if server_process.poll() is not None:
        print("Error: Server failed to start.")
        stdout, stderr = server_process.communicate()
        print("Server output:")
        print(stdout)
        print("Server errors:")
        print(stderr)
        return
    
    print("Server started successfully!")
    
    # Start the client
    print("\nStarting client...")
    try:
        client_process = subprocess.Popen(
            [sys.executable, "mcp_client.py"],
            text=True
        )
        
        # Wait for client to finish
        client_process.wait()
    except KeyboardInterrupt:
        print("\nInterrupted by user. Shutting down...")
    finally:
        # Terminate the server when done
        print("\nShutting down server...")
        server_process.terminate()
        try:
            server_process.wait(timeout=5)
        except subprocess.TimeoutExpired:
            server_process.kill()
        
    print("Todoist MCP Assistant stopped.")

if __name__ == "__main__":
    main() 