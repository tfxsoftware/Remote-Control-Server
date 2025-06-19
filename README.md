# Tomas Control Server

A modern Python WebSocket server that transforms your computer into a remotely controllable device. The server automatically registers itself on the local network using mDNS, making it easy for mobile apps to discover and connect without manual IP configuration.

## 🚀 Features

### **Remote Control Capabilities**
- **Mouse Control**: Move, click (left/right), scroll with precision
- **Touchpad Support**: Drag movement and tap-to-click functionality
- **Keyboard Control**: Type text, send special keys, key combinations
- **Special Keys**: Backspace, Enter, Tab, Escape, Function keys (F1-F12), Arrow keys
- **Key Combinations**: Ctrl+C, Alt+Tab, Ctrl+Alt+Delete, and more
- **Real-time Response**: Immediate execution of commands

### **Network Discovery**
- **mDNS Registration**: Automatically registers as `remote-control.local`
- **Zero Configuration**: No manual IP setup required
- **Cross-Platform**: Works on Windows, macOS, and Linux
- **Local Network**: Secure local network communication

### **Connection Management**
- **Multiple Clients**: Support for multiple connected devices
- **Connection Resilience**: Automatic reconnection handling
- **Status Monitoring**: Real-time connection status
- **Graceful Shutdown**: Clean disconnection handling

### **Safety Features**
- **Failsafe Mode**: Move mouse to corner to stop (pyautogui safety)
- **Coordinate Bounds**: Prevents mouse from going off-screen
- **Input Validation**: Validates all incoming commands
- **Error Handling**: Comprehensive error logging and recovery

## 🏗️ Architecture

```
┌─────────────────┐    WebSocket    ┌─────────────────┐
│   Mobile App    │ ◄─────────────► │  Tomas Control  │
│   (Client)      │                 │    Server       │
└─────────────────┘                 └─────────────────┘
                                              │
                                              ▼
                                    ┌─────────────────┐
                                    │   mDNS Service  │
                                    │  (Discovery)    │
                                    └─────────────────┘
```

## 📦 Installation

### **Prerequisites**
- Python 3.8+
- Windows/macOS/Linux

### **Install Dependencies**
```bash
pip install -r requirements.txt
```

### **Required Packages**
- `websockets`: WebSocket server implementation
- `pyautogui`: Mouse and keyboard control
- `zeroconf`: mDNS service registration
- `asyncio`: Asynchronous operations

## 🚀 Quick Start

### **1. Start the Server**
```bash
cd server
python run.py
```

### **2. Server Output**
```
=== run.py script started ===
Starting Remote Control Server...
Configuration loaded: ServerConfig(...)
Server instance created successfully
Starting server...
Starting WebSocket server on 0.0.0.0:8765
WebSocket server started successfully
Starting mDNS service...
Service registered: remote-control.local:8765
Remote Control Server is now running and ready for connections
```

### **3. Connect from Mobile App**
- Install "Tomas Control" app on your phone
- App will automatically discover the server
- Connect and start controlling your PC!

## ⚙️ Configuration

### **Server Configuration** (`config.py`)
```python
@dataclass
class ServerConfig:
    host: str = "0.0.0.0"           # Listen on all interfaces
    port: int = 8765                # WebSocket port
    service_name: str = "remote-control"  # mDNS service name
    service_type: str = "_remote-control._tcp.local."  # mDNS type
```

### **Custom Configuration**
```python
from config import ServerConfig
from remote_control_server import RemoteControlServer

# Custom configuration
config = ServerConfig(
    host="192.168.1.100",
    port=9000,
    service_name="my-remote"
)

# Start server
server = RemoteControlServer(config)
await server.start()
```

## 📡 API Reference

### **WebSocket Commands**

#### **Mouse Commands**
```json
// Move mouse
{
  "type": "mouse_move",
  "x": 100,
  "y": 200,
  "relative": false
}

// Click mouse
{
  "type": "mouse_click",
  "button": "left",
  "clicks": 1,
  "interval": 0.0
}

// Scroll mouse
{
  "type": "mouse_scroll",
  "clicks": 3,
  "x": 0,
  "y": 0
}
```

#### **Keyboard Commands**
```json
// Type text
{
  "type": "key_type",
  "text": "Hello World!",
  "interval": 0.01
}

// Press special key
{
  "type": "key_press",
  "key": "backspace"
}

// Key combination
{
  "type": "key_press",
  "key": "ctrl+c"
}

// Hold key
{
  "type": "key_press",
  "key": "shift",
  "hold": true
}
```

#### **System Commands**
```json
// Ping server
{
  "type": "ping",
  "timestamp": 1640995200.0
}
```

### **Supported Special Keys**
- **Navigation**: `backspace`, `delete`, `enter`, `tab`, `escape`, `space`
- **Arrow Keys**: `up`, `down`, `left`, `right`
- **Function Keys**: `f1` through `f12`
- **Page Navigation**: `home`, `end`, `pageup`, `pagedown`
- **Modifier Keys**: `ctrl`, `alt`, `shift`, `win`, `cmd`

## 🔧 Development

### **Project Structure**
```
server/
├── run.py                    # Main entry point
├── remote_control_server.py  # Server orchestration
├── websocket_handler.py      # WebSocket connection handling
├── remote_control.py         # Mouse/keyboard control logic
├── mdns_service.py          # mDNS registration and discovery
├── config.py                # Configuration management
├── test_client.py           # Test client for development
└── requirements.txt         # Python dependencies
```

### **Running Tests**
```bash
# Test client for development
python test_client.py --demo

# Interactive test client
python test_client.py
```

### **Logging**
The server uses structured logging with different levels:
- `INFO`: Connection events, command execution
- `DEBUG`: Detailed command information
- `ERROR`: Connection failures, command errors

## 🔒 Security Considerations

### **Network Security**
- **Local Network Only**: Server only accepts local connections
- **No Authentication**: Designed for trusted local networks
- **mDNS Discovery**: Automatic service discovery within network

### **Input Safety**
- **Command Validation**: All commands are validated before execution
- **Coordinate Bounds**: Mouse coordinates are bounded to screen
- **Failsafe Mode**: Move mouse to corner to stop execution

## 🐛 Troubleshooting

### **Common Issues**

#### **Server Won't Start**
```bash
# Check if port is in use
netstat -an | findstr 8765

# Check Python dependencies
pip list | grep websockets
```

#### **mDNS Registration Fails**
```bash
# Check if mDNS is working
dns-sd -B _remote-control._tcp local.

# Try manual IP configuration
# Edit config.py to use specific IP
```

#### **Client Can't Connect**
- Ensure both devices are on same WiFi network
- Check firewall settings
- Verify mDNS is enabled on network

### **Debug Mode**
```bash
# Enable debug logging
export LOG_LEVEL=DEBUG
python run.py
```

## 📄 License

This project is part of Tomas Control - a remote control solution for local networks.

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Test thoroughly
5. Submit a pull request

---

**Tomas Control Server** - Transform your computer into a remotely controllable device with zero configuration! 🚀 