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
        
        # Fail-safe configurations
        self.last_mouse_move_time = time.time()
        self.min_move_interval = 0.005  # Minimum time between mouse moves (200Hz max)
        self.max_move_distance = 100    # Maximum pixels per move
        self.move_count = 0
        self.last_move_reset = time.time()
        self.max_moves_per_second = 200  # Maximum moves per second
        self.is_locked = False          # Emergency lock if erratic behavior detected
    
    def _validate_movement(self, x: int, y: int, relative: bool) -> tuple[bool, str]:
        """Validate mouse movement parameters"""
        current_time = time.time()
        
        # Check rate limiting
        if current_time - self.last_mouse_move_time < self.min_move_interval:
            return False, "Rate limit exceeded"
            
        # Check move frequency
        self.move_count += 1
        if current_time - self.last_move_reset >= 1.0:
            self.move_count = 0
            self.last_move_reset = current_time
        elif self.move_count > self.max_moves_per_second:
            self.is_locked = True
            return False, "Emergency lock: too many movements"
            
        # Validate movement distance
        if relative:
            if abs(x) > self.max_move_distance or abs(y) > self.max_move_distance:
                return False, f"Movement too large: ({x}, {y})"
        else:
            # For absolute movements, ensure within screen bounds
            if not (0 <= x < self.screen_width and 0 <= y < self.screen_height):
                return False, f"Position out of bounds: ({x}, {y})"
        
        return True, ""
    
    def _emergency_unlock(self):
        """Reset emergency lock after a timeout"""
        if self.is_locked and time.time() - self.last_move_reset > 2.0:
            self.is_locked = False
            self.move_count = 0
            self.last_move_reset = time.time()
            logger.info("Emergency lock released")
    
    async def handle_mouse_move(self, data: dict):
        """Handle mouse movement commands"""
        try:
            # Check emergency lock
            self._emergency_unlock()
            if self.is_locked:
                logger.warning("Movement blocked: emergency lock active")
                return
            
            x = data.get("x", 0)
            y = data.get("y", 0)
            relative = data.get("relative", False)
            
            # Validate movement
            is_valid, error_msg = self._validate_movement(x, y, relative)
            if not is_valid:
                logger.warning(f"Invalid movement: {error_msg}")
                return
            
            if relative:
                # Move relative to current position
                current_x, current_y = pyautogui.position()
                target_x = max(0, min(current_x + x, self.screen_width - 1))
                target_y = max(0, min(current_y + y, self.screen_height - 1))
                actual_x = target_x - current_x
                actual_y = target_y - current_y
                pyautogui.moveRel(actual_x, actual_y, duration=0.01)
            else:
                # Move to absolute position
                x = max(0, min(x, self.screen_width - 1))
                y = max(0, min(y, self.screen_height - 1))
                pyautogui.moveTo(x, y, duration=0.01)
            
            self.last_mouse_move_time = time.time()
            logger.debug(f"Mouse moved to ({x}, {y})")
            
        except Exception as e:
            logger.error(f"Mouse movement error: {str(e)}")
            self.is_locked = True  # Enable emergency lock on error
    
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
        try:
            amount = data.get("amount", 0)
            
            # Validate scroll amount
            max_scroll = 500
            amount = max(-max_scroll, min(max_scroll, amount))
            
            pyautogui.scroll(amount)
            logger.debug(f"Mouse scroll: {amount}")
            
        except Exception as e:
            logger.error(f"Mouse scroll error: {str(e)}")
    
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