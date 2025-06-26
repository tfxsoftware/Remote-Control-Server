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

# Key mapping for special keys
SPECIAL_KEYS = {
    # Navigation keys
    'backspace': 'backspace',
    'delete': 'delete',
    'enter': 'enter',
    'tab': 'tab',
    'escape': 'esc',
    'esc': 'esc',
    
    # Arrow keys
    'up': 'up',
    'down': 'down',
    'left': 'left',
    'right': 'right',
    
    # Function keys
    'f1': 'f1', 'f2': 'f2', 'f3': 'f3', 'f4': 'f4', 'f5': 'f5',
    'f6': 'f6', 'f7': 'f7', 'f8': 'f8', 'f9': 'f9', 'f10': 'f10',
    'f11': 'f11', 'f12': 'f12',
    
    # Modifier keys
    'ctrl': 'ctrl', 'control': 'ctrl',
    'alt': 'alt',
    'shift': 'shift',
    'win': 'win', 'windows': 'win',
    'cmd': 'cmd', 'command': 'cmd',
    
    # Common keys
    'space': 'space',
    'home': 'home',
    'end': 'end',
    'pageup': 'pageup', 'pgup': 'pageup',
    'pagedown': 'pagedown', 'pgdn': 'pagedown',
    'insert': 'insert', 'ins': 'insert',
    
    # Media keys
    'volumeup': 'volumeup', 'volup': 'volumeup',
    'volumedown': 'volumedown', 'voldown': 'volumedown',
    'volumemute': 'volumemute', 'mute': 'volumemute',
    'play': 'space', 'pause': 'space', 'stop': 'stop',
    'next': 'nexttrack', 'previous': 'prevtrack',
    
    # Browser keys
    'browserback': 'browserback', 'back': 'browserback',
    'browserforward': 'browserforward', 'forward': 'browserforward',
    'browserrefresh': 'browserrefresh', 'refresh': 'browserrefresh',
    'browserstop': 'browserstop', 'stop': 'browserstop',
    'browsersearch': 'browsersearch', 'search': 'browsersearch',
    'browserfavorites': 'browserfavorites', 'favorites': 'browserfavorites',
    'browserhome': 'browserhome', 'homepage': 'browserhome',
}

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
        amount = data.get("amount", 0)
        
        logger.info(f"Scroll command received: amount={amount}, data={data}")
        
        if amount != 0:
            try:
                # Use simple scroll without coordinates - pyautogui will use current mouse position
                logger.info(f"Executing scroll: amount={amount}")
                pyautogui.scroll(amount)
                logger.info(f"Scroll executed successfully: amount={amount}")
            except Exception as e:
                logger.error(f"Error executing scroll: {e}")
        else:
            logger.warning(f"Scroll command ignored: amount is 0")
    
    async def handle_key_press(self, data: dict):
        """Handle key press commands"""
        key = data.get("key", "").lower()
        if not key:
            return
        
        # Handle special keys
        if key in SPECIAL_KEYS:
            key = SPECIAL_KEYS[key]
        
        # Handle key combinations (e.g., "ctrl+c", "alt+tab")
        if '+' in key:
            keys = [k.strip().lower() for k in key.split('+')]
            # Map special keys in combinations
            mapped_keys = []
            for k in keys:
                if k in SPECIAL_KEYS:
                    mapped_keys.append(SPECIAL_KEYS[k])
                else:
                    mapped_keys.append(k)
            
            if data.get("hold", False):
                # Hold all keys down
                for k in mapped_keys:
                    pyautogui.keyDown(k)
                logger.debug(f"Key combination down: {key}")
            elif data.get("release", False):
                # Release all keys
                for k in reversed(mapped_keys):
                    pyautogui.keyUp(k)
                logger.debug(f"Key combination up: {key}")
            else:
                # Press and release combination
                pyautogui.hotkey(*mapped_keys)
                logger.debug(f"Key combination press: {key}")
        else:
            # Single key
            if data.get("hold", False):
                # Hold key down
                pyautogui.keyDown(key)
                logger.debug(f"Key down: {key}")
            elif data.get("release", False):
                # Release key
                pyautogui.keyUp(key)
                logger.debug(f"Key up: {key}")
            else:
                # Press and release - use typewrite for space key for better reliability
                if key == 'space':
                    pyautogui.typewrite(' ')
                else:
                    pyautogui.press(key)
                logger.debug(f"Key press: {key}")
    
    async def handle_key_type(self, data: dict):
        """Handle text typing commands"""
        text = data.get("text", "")
        interval = data.get("interval", 0.01)
        
        if text:
            # Handle special characters in text
            processed_text = self._process_text_for_typing(text)
            pyautogui.typewrite(processed_text, interval=interval)
            logger.debug(f"Typed text: {text[:50]}{'...' if len(text) > 50 else ''}")
    
    def _process_text_for_typing(self, text: str) -> str:
        """Process text to handle special characters"""
        # Replace common special characters with their key equivalents
        replacements = {
            '\n': 'enter',
            '\t': 'tab',
            '\b': 'backspace',
        }
        
        # For now, just return the text as-is
        # pyautogui.typewrite handles most characters well
        return text
    
    async def handle_multiple_keys(self, data: dict):
        """Handle multiple key presses in sequence"""
        keys = data.get("keys", [])
        interval = data.get("interval", 0.1)
        
        for key in keys:
            if isinstance(key, str):
                await self.handle_key_press({"key": key})
            elif isinstance(key, dict):
                await self.handle_key_press(key)
            await asyncio.sleep(interval)
        
        logger.debug(f"Pressed multiple keys: {keys}")
    
    def get_screen_info(self):
        """Get current screen information"""
        return {
            "width": self.screen_width,
            "height": self.screen_height
        } 