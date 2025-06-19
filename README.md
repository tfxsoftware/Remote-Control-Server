# Remote Control Server

A modular Python WebSocket server that acts as a remote control for your computer, allowing mobile apps to send mouse and keyboard commands via WebSocket. The server automatically registers itself using mDNS (multicast DNS) for easy discovery on the local network.

## Features

- **Modular Architecture**: Clean separation of concerns with dedicated modules
- **Remote Control Server**: Receives mouse and keyboard commands from mobile apps
- **mDNS Registration**: Automatically registers the server on the local network
- **Mouse Control**: Move, click, scroll, and right-click functionality
- **Keyboard Control**: Key presses, key holds, and text typing
- **Real-time Response**: Immediate execution of commands
- **Screen Resolution Detection**: Automatically detects and reports screen dimensions
- **Safety Features**: Built-in failsafe and coordinate bounds checking
- **Configurable**: Easy to customize settings and behavior

## Project Structure

```
├── run.py                           # Direct execution script
├── test_client.py                   # Test client for development
├── requirements.txt                 # Python dependencies
├── README.md                        # This file
├── __init__.py                      # Package initialization
├── config.py                        # Configuration management
├── remote_control.py                # Mouse/keyboard control logic
├── mdns_service.py                  # mDNS registration and discovery
├── websocket_handler.py             # WebSocket connection handling
├── remote_control_server.py         # Main server orchestration
└── main.py                          # Package entry point
```

## Installation

1. Install the required dependencies:

```bash
pip install -r requirements.txt
```

**Note**: On some systems, you may need additional dependencies for pyautogui:
- **Windows**: No additional dependencies needed
- **macOS**: `pip install pyobjc-core pyobjc`
- **Linux**: `sudo apt-get install python3-tk python3-dev` or equivalent

## Usage

### Starting the Server

Run the remote control server:

```bash
python run.py
```

The server will:
- Start on `0.0.0.0:8765` by default
- Register itself as an mDNS service with type `_remote-control._tcp.local.`
- Detect your screen resolution
- Accept WebSocket connections from mobile apps
- Execute mouse and keyboard commands in real-time

### Testing with the Test Client

#### Demo Mode
Run a demonstration of all remote control features:

```bash
python test_client.py --demo
```

#### Interactive Mode
Run an interactive client for manual testing:

```bash
python test_client.py
```

## API Documentation

### WebSocket Connection

Connect to the server via WebSocket at `ws://<server-ip>:8765`

### Message Protocol

All messages are JSON formatted with a `type` field indicating the message type.

#### Server to Client Messages

##### Welcome Message
```json
{
  "type": "welcome",
  "client_id": 123456,
  "screen_info": {
    "width": 1920,
    "height": 1080
  },
  "server_info": {
    "name": "remote-tv-server",
    "version": "1.0"
  }
}
```

##### Pong Response
```json
{
  "type": "pong",
  "timestamp": 1640995200.0
}
```

##### Error Response
```json
{
  "type": "error",
  "command": "mouse_move",
  "error": "Invalid coordinates"
}
```

#### Client to Server Commands

##### Mouse Movement
```json
{
  "type": "mouse_move",
  "x": 500,
  "y": 300,
  "relative": false
}
```

##### Mouse Click
```json
{
  "type": "mouse_click",
  "button": "left",
  "clicks": 1,
  "interval": 0.0
}
```

##### Mouse Scroll
```json
{
  "type": "mouse_scroll",
  "clicks": 3,
  "x": 0,
  "y": 0
}
```

##### Key Press
```json
{
  "type": "key_press",
  "key": "ctrl",
  "hold": false,
  "release": false
}
```

##### Text Typing
```json
{
  "type": "key_type",
  "text": "Hello World!",
  "interval": 0.01
}
```

##### Ping
```json
{
  "type": "ping",
  "timestamp": 1640995200.0
}
```

### Command Reference

#### Mouse Commands

| Command | Parameters | Description |
|---------|------------|-------------|
| `mouse_move` | `x`, `y`, `relative` | Move mouse to coordinates |
| `mouse_click` | `button`, `clicks`, `interval` | Click mouse button |
| `mouse_scroll` | `clicks`, `x`, `y` | Scroll mouse wheel |

**Mouse Buttons**: `left`, `right`, `middle`, `double`

#### Keyboard Commands

| Command | Parameters | Description |
|---------|------------|-------------|
| `key_press` | `key`, `hold`, `release` | Press/release key |
| `key_type` | `text`, `interval` | Type text |

**Key Actions**:
- `hold: true` - Hold key down
- `release: true` - Release key
- Both `false` - Press and release

### mDNS Discovery

The server registers itself as a `_remote-control._tcp.local.` service with the following properties:

- `port`: Server port (default: 8765)
- `protocol`: "websocket"
- `version`: "1.0"
- `type`: "remote-control"
- `screen_width`: Screen width in pixels
- `screen_height`: Screen height in pixels

## Configuration

You can customize the server by modifying the configuration:

```python
from config import ServerConfig
from remote_control_server import RemoteControlServer

# Create custom configuration
config = ServerConfig(
    host="0.0.0.0",
    port=8765,
    service_name="my-remote",
    log_level="DEBUG"
)

# Start server with custom config
server = RemoteControlServer(config)
await server.start()
```

## Module Documentation

### `config.py`
Configuration management with a `ServerConfig` dataclass that centralizes all server settings.

### `remote_control.py`
Handles all mouse and keyboard control operations using pyautogui.

### `mdns_service.py`
Manages mDNS service registration and discovery using zeroconf.

### `websocket_handler.py`
Manages WebSocket connections and message processing.

### `remote_control_server.py`
Main server class that orchestrates all components.

## Safety Features

- **Failsafe**: Move mouse to top-left corner to stop execution
- **Coordinate Bounds**: All mouse movements are clamped to screen boundaries
- **Rate Limiting**: Small delays between actions to prevent overwhelming
- **Error Handling**: Graceful handling of invalid commands

## Troubleshooting

### Permission Issues
On some systems, you may need elevated privileges for mouse/keyboard control:

```bash
sudo python run.py
```

### Firewall Issues
Make sure your firewall allows:
- Incoming connections on port 8765 (or your chosen port)
- mDNS traffic (UDP port 5353)

### Display Issues
- Ensure you're running on the correct display (for multi-monitor setups)
- Some remote desktop solutions may interfere with pyautogui

### Network Issues
- Ensure all devices are on the same local network
- Check that mDNS is enabled on your network
- Some corporate networks may block mDNS traffic

## Dependencies

- `websockets`: WebSocket server implementation
- `zeroconf`: mDNS service discovery
- `pyautogui`: Mouse and keyboard control
- `asyncio`: Asynchronous I/O support

## Security Considerations

⚠️ **Warning**: This server allows remote control of your computer. Use with caution:

- Only run on trusted networks
- Consider implementing authentication
- Be aware that anyone on the network can potentially control your computer
- Use firewall rules to restrict access if needed

## License

This project is open source and available under the MIT License. 