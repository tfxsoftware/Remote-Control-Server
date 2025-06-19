import asyncio
import json
import logging
from typing import Dict, Set
import websockets
from websockets.server import WebSocketServerProtocol
import pyautogui
import time

logger = logging.getLogger(__name__)

# Configure pyautogui for safety
pyautogui.FAILSAFE = True
pyautogui.PAUSE = 0.01  # Small delay between actions

class RemoteControl:
    """Handles mouse and keyboard control commands"""
    
    def __init__(self):
        # Get screen dimensions
        self.screen_width, self.screen_height = pyautogui.size()
        logger.info(f"Screen resolution: {self.screen_width}x{self.screen_height}")
    
    async def handle_mouse_move(self, data: dict):
        """Handle mouse movement commands"""
        x = data.get("x")
        y = data.get("y")
        relative = data.get("relative", False)
        
        if relative:
            # Move relative to current position
            pyautogui.moveRel(x, y, duration=0.01)
        else:
            # Move to absolute position
            # Ensure coordinates are within screen bounds
            x = max(0, min(x, self.screen_width - 1))
            y = max(0, min(y, self.screen_height - 1))
            pyautogui.moveTo(x, y, duration=0.01)
        
        logger.debug(f"Mouse moved to ({x}, {y})")
    
    async def handle_mouse_click(self, data: dict):
        """Handle mouse click commands"""
        button = data.get("button", "left")
        clicks = data.get("clicks", 1)
        interval = data.get("interval", 0.0)
        
        if button == "left":
            pyautogui.click(button="left", clicks=clicks, interval=interval)
        elif button == "right":
            pyautogui.click(button="right", clicks=clicks, interval=interval)
        elif button == "middle":
            pyautogui.click(button="middle", clicks=clicks, interval=interval)
        elif button == "double":
            pyautogui.doubleClick()
        
        logger.debug(f"Mouse {button} click, {clicks} times")
    
    async def handle_mouse_scroll(self, data: dict):
        """Handle mouse scroll commands"""
        x = data.get("x", 0)
        y = data.get("y", 0)
        clicks = data.get("clicks", 3)
        
        pyautogui.scroll(clicks, x=x, y=y)
        logger.debug(f"Mouse scroll: {clicks} clicks at ({x}, {y})")
    
    async def handle_key_press(self, data: dict):
        """Handle key press commands"""
        key = data.get("key")
        if not key:
            return
            
        if data.get("hold", False):
            # Hold key down
            pyautogui.keyDown(key)
            logger.debug(f"Key down: {key}")
        elif data.get("release", False):
            # Release key
            pyautogui.keyUp(key)
            logger.debug(f"Key up: {key}")
        else:
            # Press and release
            pyautogui.press(key)
            logger.debug(f"Key press: {key}")
    
    async def handle_key_type(self, data: dict):
        """Handle text typing commands"""
        text = data.get("text", "")
        interval = data.get("interval", 0.01)
        
        if text:
            pyautogui.typewrite(text, interval=interval)
            logger.debug(f"Typed text: {text[:50]}{'...' if len(text) > 50 else ''}")
    
    def get_screen_info(self):
        """Get current screen information"""
        return {
            "width": self.screen_width,
            "height": self.screen_height
        } 