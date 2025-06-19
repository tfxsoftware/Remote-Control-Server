#!/usr/bin/env python3
"""
Remote Control Test Client

A test client for the remote control server that demonstrates
various mouse and keyboard commands.
"""

import asyncio
import json
import websockets
import logging
import time
import sys

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class RemoteControlTestClient:
    """Test client for the remote control server"""
    
    def __init__(self, uri: str = "ws://localhost:8765"):
        self.uri = uri
        self.websocket = None
        self.screen_width = 1920
        self.screen_height = 1080
    
    async def connect(self):
        """Connect to the remote control server"""
        try:
            self.websocket = await websockets.connect(self.uri)
            logger.info(f"Connected to remote control server at {self.uri}")
            
            # Start listening for messages
            asyncio.create_task(self.listen_for_messages())
            
        except Exception as e:
            logger.error(f"Failed to connect: {e}")
    
    async def listen_for_messages(self):
        """Listen for incoming messages from the server"""
        try:
            async for message in self.websocket:
                try:
                    data = json.loads(message)
                    await self.handle_message(data)
                except json.JSONDecodeError:
                    logger.warning(f"Received invalid JSON: {message}")
                except Exception as e:
                    logger.error(f"Error handling message: {e}")
        except websockets.exceptions.ConnectionClosed:
            logger.info("Connection closed")
        except Exception as e:
            logger.error(f"Error in message listener: {e}")
    
    async def handle_message(self, data: dict):
        """Handle incoming messages from the server"""
        message_type = data.get("type", "unknown")
        
        if message_type == "welcome":
            logger.info(f"Welcome! Client ID: {data.get('client_id')}")
            screen_info = data.get("screen_info", {})
            self.screen_width = screen_info.get("width", 1920)
            self.screen_height = screen_info.get("height", 1080)
            logger.info(f"Screen resolution: {self.screen_width}x{self.screen_height}")
            
            server_info = data.get("server_info", {})
            logger.info(f"Server: {server_info.get('name')} v{server_info.get('version')}")
        
        elif message_type == "pong":
            logger.info(f"Received pong with timestamp: {data.get('timestamp')}")
        
        elif message_type == "error":
            logger.error(f"Server error: {data.get('error')} for command: {data.get('command')}")
        
        else:
            logger.info(f"Received message: {data}")
    
    async def send_ping(self):
        """Send a ping message to the server"""
        if self.websocket:
            message = {
                "type": "ping",
                "timestamp": time.time()
            }
            await self.websocket.send(json.dumps(message))
    
    async def send_mouse_move(self, x: int, y: int, relative: bool = False):
        """Send mouse movement command"""
        if self.websocket:
            message = {
                "type": "mouse_move",
                "x": x,
                "y": y,
                "relative": relative
            }
            await self.websocket.send(json.dumps(message))
            logger.info(f"Mouse move: ({x}, {y}) {'relative' if relative else 'absolute'}")
    
    async def send_mouse_click(self, button: str = "left", clicks: int = 1, interval: float = 0.0):
        """Send mouse click command"""
        if self.websocket:
            message = {
                "type": "mouse_click",
                "button": button,
                "clicks": clicks,
                "interval": interval
            }
            await self.websocket.send(json.dumps(message))
            logger.info(f"Mouse click: {button} button, {clicks} times")
    
    async def send_mouse_scroll(self, clicks: int, x: int = 0, y: int = 0):
        """Send mouse scroll command"""
        if self.websocket:
            message = {
                "type": "mouse_scroll",
                "clicks": clicks,
                "x": x,
                "y": y
            }
            await self.websocket.send(json.dumps(message))
            logger.info(f"Mouse scroll: {clicks} clicks at ({x}, {y})")
    
    async def send_key_press(self, key: str, hold: bool = False, release: bool = False):
        """Send key press command"""
        if self.websocket:
            message = {
                "type": "key_press",
                "key": key,
                "hold": hold,
                "release": release
            }
            await self.websocket.send(json.dumps(message))
            action = "hold" if hold else "release" if release else "press"
            logger.info(f"Key {action}: {key}")
    
    async def send_key_type(self, text: str, interval: float = 0.01):
        """Send text typing command"""
        if self.websocket:
            message = {
                "type": "key_type",
                "text": text,
                "interval": interval
            }
            await self.websocket.send(json.dumps(message))
            logger.info(f"Typing text: {text[:50]}{'...' if len(text) > 50 else ''}")
    
    async def close(self):
        """Close the WebSocket connection"""
        if self.websocket:
            await self.websocket.close()
            logger.info("Connection closed")

async def demo_remote_control():
    """Demonstrate various remote control commands"""
    client = RemoteControlTestClient()
    await client.connect()
    
    # Wait for welcome message
    await asyncio.sleep(2)
    
    logger.info("Starting remote control demo...")
    
    # Test ping
    await client.send_ping()
    await asyncio.sleep(1)
    
    # Test mouse movement to center of screen
    center_x = client.screen_width // 2
    center_y = client.screen_height // 2
    await client.send_mouse_move(center_x, center_y)
    await asyncio.sleep(1)
    
    # Test mouse click
    await client.send_mouse_click("left", 1)
    await asyncio.sleep(1)
    
    # Test mouse scroll
    await client.send_mouse_scroll(3)
    await asyncio.sleep(1)
    
    # Test key press
    await client.send_key_press("ctrl")
    await asyncio.sleep(0.5)
    await client.send_key_press("a")
    await asyncio.sleep(0.5)
    await client.send_key_press("ctrl", release=True)
    await asyncio.sleep(1)
    
    # Test text typing
    await client.send_key_type("Hello from remote control!")
    await asyncio.sleep(2)
    
    # Test right click
    await client.send_mouse_click("right", 1)
    await asyncio.sleep(1)
    
    logger.info("Demo completed!")
    await client.close()

async def interactive_remote_control():
    """Interactive remote control client"""
    client = RemoteControlTestClient()
    await client.connect()
    
    # Wait for welcome message
    await asyncio.sleep(2)
    
    print("\nRemote Control Commands:")
    print("  'move <x> <y>' - Move mouse to absolute position")
    print("  'moverel <dx> <dy>' - Move mouse relative to current position")
    print("  'click <button>' - Click mouse button (left/right/middle/double)")
    print("  'scroll <clicks>' - Scroll mouse wheel")
    print("  'key <key>' - Press a key")
    print("  'hold <key>' - Hold a key down")
    print("  'release <key>' - Release a key")
    print("  'type <text>' - Type text")
    print("  'ping' - Send ping to server")
    print("  'quit' - Exit client")
    print()
    
    try:
        while True:
            command = input("Enter command: ").strip().split()
            if not command:
                continue
                
            cmd = command[0].lower()
            
            if cmd == "move" and len(command) == 3:
                x, y = int(command[1]), int(command[2])
                await client.send_mouse_move(x, y)
            
            elif cmd == "moverel" and len(command) == 3:
                dx, dy = int(command[1]), int(command[2])
                await client.send_mouse_move(dx, dy, relative=True)
            
            elif cmd == "click" and len(command) == 2:
                button = command[1].lower()
                await client.send_mouse_click(button)
            
            elif cmd == "scroll" and len(command) == 2:
                clicks = int(command[1])
                await client.send_mouse_scroll(clicks)
            
            elif cmd == "key" and len(command) == 2:
                key = command[1]
                await client.send_key_press(key)
            
            elif cmd == "hold" and len(command) == 2:
                key = command[1]
                await client.send_key_press(key, hold=True)
            
            elif cmd == "release" and len(command) == 2:
                key = command[1]
                await client.send_key_press(key, release=True)
            
            elif cmd == "type" and len(command) > 1:
                text = " ".join(command[1:])
                await client.send_key_type(text)
            
            elif cmd == "ping":
                await client.send_ping()
            
            elif cmd == "quit":
                break
            
            else:
                print("Invalid command. Use 'move <x> <y>', 'click <button>', 'key <key>', etc.")
    
    except KeyboardInterrupt:
        print("\nInterrupted by user")
    
    finally:
        await client.close()

def main():
    """Main entry point for the test client"""
    if len(sys.argv) > 1 and sys.argv[1] == "--demo":
        asyncio.run(demo_remote_control())
    else:
        asyncio.run(interactive_remote_control())

if __name__ == "__main__":
    main() 