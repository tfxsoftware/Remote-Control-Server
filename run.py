#!/usr/bin/env python3
"""
Remote Control Server - Run Script

This script can be run directly from the server directory to start the server.
Usage: python run.py
"""

import asyncio
import sys
import logging
from pathlib import Path

# Add the current directory to Python path
sys.path.insert(0, str(Path(__file__).parent))

from remote_control_server import RemoteControlServer
from config import ServerConfig

def main():
    """Main entry point for the remote control server"""
    try:
        # Create server with default configuration
        server = RemoteControlServer()
        
        # Start the server
        asyncio.run(server.start())
        
    except KeyboardInterrupt:
        print("\nServer stopped by user")
    except Exception as e:
        print(f"Error starting server: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main() 