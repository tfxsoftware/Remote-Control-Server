import asyncio
import json
import logging
from typing import Set
import websockets
from websockets.server import WebSocketServerProtocol
import time

try:
    from .remote_control import RemoteControl
except ImportError:
    from remote_control import RemoteControl

logger = logging.getLogger(__name__)

class WebSocketHandler:
    """Handles WebSocket connections and message processing"""
    
    def __init__(self, remote_control: RemoteControl):
        self.remote_control = remote_control
        self.clients: Set[WebSocketServerProtocol] = set()
    
    async def handle_client(self, websocket: WebSocketServerProtocol, path: str):
        """Handle individual WebSocket client connections"""
        client_id = id(websocket)
        try:
            client_address = websocket.remote_address
        except AttributeError:
            client_address = "unknown"
        self.clients.add(websocket)
        logger.info(f"Remote control client {client_id} connected from {client_address}")
        logger.info(f"Total connected clients: {len(self.clients)}")
        
        try:
            # Send welcome message with screen info
            welcome_message = {
                "type": "welcome",
                "client_id": client_id,
                "screen_info": self.remote_control.get_screen_info(),
                "server_info": {
                    "name": "remote-control",
                    "version": "1.0"
                }
            }
            await websocket.send(json.dumps(welcome_message))
            logger.info(f"Sent welcome message to client {client_id}")
            
            # Handle incoming commands
            async for message in websocket:
                try:
                    logger.info(f"Received message from client {client_id}: {message}")
                    data = json.loads(message)
                    await self.handle_command(websocket, data)
                except json.JSONDecodeError:
                    logger.warning(f"Invalid JSON from client {client_id}: {message}")
                except Exception as e:
                    logger.error(f"Error handling command from client {client_id}: {e}")
                    
        except websockets.exceptions.ConnectionClosed:
            logger.info(f"Remote control client {client_id} disconnected")
        finally:
            self.clients.remove(websocket)
            logger.info(f"Client {client_id} removed. Total clients: {len(self.clients)}")
    
    async def handle_command(self, websocket: WebSocketServerProtocol, data: dict):
        """Handle incoming remote control commands"""
        command_type = data.get("type", "unknown")
        client_id = id(websocket)
        
        logger.info(f"Processing command '{command_type}' from client {client_id}")
        
        try:
            if command_type == "mouse_move":
                await self.remote_control.handle_mouse_move(data)
                
            elif command_type == "mouse_click":
                await self.remote_control.handle_mouse_click(data)
                
            elif command_type == "mouse_scroll":
                await self.remote_control.handle_mouse_scroll(data)
                
            elif command_type == "key_press":
                await self.remote_control.handle_key_press(data)
                
            elif command_type == "key_type":
                await self.remote_control.handle_key_type(data)
                
            elif command_type == "multiple_keys":
                await self.remote_control.handle_multiple_keys(data)
                
            elif command_type == "ping":
                response = {
                    "type": "pong", 
                    "timestamp": data.get("timestamp")
                }
                await websocket.send(json.dumps(response))
                logger.info(f"Sent pong response to client {client_id}")
                
            else:
                logger.warning(f"Unknown command type '{command_type}' from client {client_id}")
                
        except Exception as e:
            logger.error(f"Error executing command '{command_type}' from client {client_id}: {e}")
            # Send error response to client
            error_response = {
                "type": "error",
                "command": command_type,
                "error": str(e)
            }
            await websocket.send(json.dumps(error_response))
            logger.info(f"Sent error response to client {client_id}: {error_response}")
    
    def get_connected_clients_count(self):
        """Get the number of connected clients"""
        return len(self.clients) 