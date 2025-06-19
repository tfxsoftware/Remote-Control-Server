import asyncio
import logging
import signal
import sys
from typing import Optional
import websockets

try:
    from .websocket_handler import WebSocketHandler
    from .remote_control import RemoteControl
    from .mdns_service import MDNSService
    from .config import ServerConfig
except ImportError:
    from websocket_handler import WebSocketHandler
    from remote_control import RemoteControl
    from mdns_service import MDNSService
    from config import ServerConfig

logger = logging.getLogger(__name__)

class RemoteControlServer:
    """Main server class that coordinates WebSocket and mDNS services"""
    
    def __init__(self, config: ServerConfig):
        self.config = config
        self.remote_control = RemoteControl()
        self.websocket_handler = WebSocketHandler(self.remote_control)
        self.mdns_service = MDNSService(config)
        self.websocket_server: Optional[asyncio.Server] = None
        self.running = False
        
    async def start(self):
        """Start the remote control server"""
        logger.info("Starting Remote Control Server...")
        logger.info(f"Configuration: {self.config}")
        
        try:
            # Start WebSocket server
            logger.info(f"Starting WebSocket server on {self.config.host}:{self.config.port}")
            self.websocket_server = await websockets.serve(
                self.websocket_handler.handle_client,
                self.config.host,
                self.config.port
            )
            logger.info(f"WebSocket server started successfully on {self.config.host}:{self.config.port}")
            
            # Start mDNS service
            logger.info("Starting mDNS service...")
            await self.mdns_service.start()
            logger.info("mDNS service started successfully")
            
            self.running = True
            logger.info("Remote Control Server is now running and ready for connections")
            
            # Keep the server running
            await self.websocket_server.wait_closed()
            
        except Exception as e:
            logger.error(f"Failed to start server: {e}")
            await self.stop()
            raise
    
    async def stop(self):
        """Stop the remote control server"""
        logger.info("Stopping Remote Control Server...")
        self.running = False
        
        try:
            # Stop WebSocket server
            if self.websocket_server:
                logger.info("Stopping WebSocket server...")
                self.websocket_server.close()
                await self.websocket_server.wait_closed()
                logger.info("WebSocket server stopped")
            
            # Stop mDNS service
            logger.info("Stopping mDNS service...")
            await self.mdns_service.stop()
            logger.info("mDNS service stopped")
            
            logger.info("Remote Control Server stopped successfully")
            
        except Exception as e:
            logger.error(f"Error stopping server: {e}")

async def main():
    """Main entry point"""
    # Configure logging
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    
    logger.info("Initializing Remote Control Server...")
    
    # Load configuration
    config = ServerConfig()
    logger.info(f"Loaded configuration: {config}")
    
    # Create and start server
    server = RemoteControlServer(config)
    
    # Handle graceful shutdown
    def signal_handler():
        logger.info("Received shutdown signal")
        asyncio.create_task(server.stop())
    
    # Register signal handlers
    for sig in (signal.SIGINT, signal.SIGTERM):
        asyncio.get_event_loop().add_signal_handler(sig, signal_handler)
    
    try:
        await server.start()
    except KeyboardInterrupt:
        logger.info("Received keyboard interrupt")
    except Exception as e:
        logger.error(f"Server error: {e}")
        sys.exit(1)
    finally:
        await server.stop()

if __name__ == "__main__":
    asyncio.run(main()) 