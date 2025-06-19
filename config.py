import logging
from dataclasses import dataclass
from typing import Optional

@dataclass
class ServerConfig:
    """Configuration for the remote control server"""
    
    # Server settings
    host: str = "0.0.0.0"
    port: int = 8765
    service_name: str = "remote-tv-server"
    
    # Logging settings
    log_level: str = "INFO"
    log_format: str = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    
    # WebSocket settings
    websocket_ping_interval: Optional[float] = 20.0
    websocket_ping_timeout: Optional[float] = 20.0
    
    # Remote control settings
    mouse_move_duration: float = 0.01
    key_type_interval: float = 0.01
    pyautogui_pause: float = 0.01
    
    # mDNS settings
    mdns_service_type: str = "_remote-control._tcp.local."
    mdns_protocol: str = "websocket"
    mdns_version: str = "1.0"

# Default configuration
DEFAULT_CONFIG = ServerConfig()

def setup_logging(config: ServerConfig = DEFAULT_CONFIG):
    """Setup logging configuration"""
    logging.basicConfig(
        level=getattr(logging, config.log_level),
        format=config.log_format
    )

def get_config() -> ServerConfig:
    """Get the current configuration"""
    return DEFAULT_CONFIG 