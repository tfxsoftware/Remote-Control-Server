#!/usr/bin/env python3
"""
Remote Control Server - Run Script

This script can be run directly from the server directory to start the server.
Usage: python run.py
"""

print('=== run.py script started ===')

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
    print("Starting Remote Control Server...")
    try:
        # Setup logging
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
        )
        logger = logging.getLogger(__name__)
        
        print("Logging configured")
        logger.info("Starting Remote Control Server...")
        
        # Create server configuration
        config = ServerConfig()
        print(f"Configuration loaded: {config}")
        logger.info(f"Configuration loaded: {config}")
        
        # Create server with configuration
        server = RemoteControlServer(config)
        print("Server instance created successfully")
        logger.info("Server instance created successfully")
        
        # Start the server
        print("Starting server...")
        logger.info("Starting server...")
        asyncio.run(server.start())
        
    except KeyboardInterrupt:
        print("\nServer stopped by user")
    except Exception as e:
        print(f"Error starting server: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)

if __name__ == "__main__":
    main() 