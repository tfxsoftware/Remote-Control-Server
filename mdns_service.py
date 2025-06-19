import asyncio
import logging
import socket
from typing import Dict, List, Optional
from zeroconf import ServiceInfo, Zeroconf, ServiceBrowser
from zeroconf.asyncio import AsyncZeroconf

try:
    from .config import ServerConfig
except ImportError:
    from config import ServerConfig

logger = logging.getLogger(__name__)

class MDNSService:
    """Handles mDNS service registration and discovery"""
    
    def __init__(self, config: ServerConfig):
        self.config = config
        self.zeroconf: Optional[AsyncZeroconf] = None
        self.service_info: Optional[ServiceInfo] = None
        self.browser: Optional[ServiceBrowser] = None
        self.discovered_services: Dict[str, ServiceInfo] = {}
        
    async def start(self):
        """Start the mDNS service and register our service"""
        logger.info("Starting mDNS service...")
        try:
            # Initialize AsyncZeroconf
            self.zeroconf = AsyncZeroconf()
            logger.info("AsyncZeroconf initialized successfully")
            
            # Register our service
            await self.register_service()
            logger.info("Service registration completed")
            
            # Start service discovery
            await self.start_discovery()
            logger.info("Service discovery started")
            
        except Exception as e:
            logger.error(f"Failed to start mDNS service: {e}")
            raise
    
    async def register_service(self):
        """Register our remote control service via mDNS"""
        try:
            logger.info(f"Registering service: {self.config.service_name}")
            logger.info(f"Service type: {self.config.service_type}")
            logger.info(f"Port: {self.config.port}")
            logger.info(f"Host: {self.config.host}")
            
            # Get local IP address for mDNS registration
            # We need to get the actual local IP, not 0.0.0.0 or 127.0.0.1
            local_ip = self._get_local_ip()
            logger.info(f"Using IP address for mDNS: {local_ip}")
            
            # Create service properties
            properties = {
                "version": "1.0",
                "protocol": "websocket",
                "description": "Remote Control Server"
            }
            
            # Create ServiceInfo
            self.service_info = ServiceInfo(
                type_=self.config.service_type,
                name=f"{self.config.service_name}.{self.config.service_type}",
                addresses=[socket.inet_pton(socket.AF_INET, local_ip)],
                port=self.config.port,
                properties=properties
            )
            
            # Register the service
            await self.zeroconf.async_register_service(self.service_info)
            logger.info(f"Successfully registered service: {self.service_info.name}")
            logger.info(f"Service available at: {self.config.service_name}.local:{self.config.port}")
            
        except Exception as e:
            logger.error(f"Failed to register service: {e}")
            raise
    
    def _get_local_ip(self):
        """Get the local IP address for mDNS registration"""
        try:
            # Create a socket to get local IP
            with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as s:
                # Connect to a remote address (doesn't actually connect)
                s.connect(("8.8.8.8", 80))
                local_ip = s.getsockname()[0]
                logger.info(f"Detected local IP: {local_ip}")
                return local_ip
        except Exception as e:
            logger.warning(f"Could not detect local IP, using 127.0.0.1: {e}")
            return "127.0.0.1"
    
    async def start_discovery(self):
        """Start discovering other services on the network"""
        try:
            logger.info("Starting service discovery...")
            
            # Create service browser
            self.browser = ServiceBrowser(
                self.zeroconf.zeroconf,
                [self.config.service_type],
                handlers=[self._on_service_state_change]
            )
            logger.info("Service browser created successfully")
            
        except Exception as e:
            logger.error(f"Failed to start service discovery: {e}")
            raise
    
    def _on_service_state_change(self, zeroconf, service_type, name, state_change):
        """Handle service state changes during discovery"""
        try:
            if state_change == "Added":
                logger.info(f"Service discovered: {name}")
                # Resolve the service to get its details
                asyncio.create_task(self._resolve_service(name))
            elif state_change == "Removed":
                logger.info(f"Service removed: {name}")
                if name in self.discovered_services:
                    del self.discovered_services[name]
            elif state_change == "Updated":
                logger.info(f"Service updated: {name}")
                # Re-resolve the service
                asyncio.create_task(self._resolve_service(name))
        except Exception as e:
            logger.error(f"Error handling service state change: {e}")
    
    async def _resolve_service(self, name: str):
        """Resolve a discovered service to get its details"""
        try:
            logger.info(f"Resolving service: {name}")
            info = await self.zeroconf.async_get_service_info(self.config.service_type, name)
            if info:
                self.discovered_services[name] = info
                logger.info(f"Service resolved: {name}")
                logger.info(f"  Address: {info.parsed_addresses()}")
                logger.info(f"  Port: {info.port}")
                logger.info(f"  Properties: {info.properties}")
            else:
                logger.warning(f"Failed to resolve service: {name}")
        except Exception as e:
            logger.error(f"Error resolving service {name}: {e}")
    
    async def update_service(self, properties: Dict[str, str]):
        """Update service properties"""
        try:
            logger.info(f"Updating service properties: {properties}")
            if self.service_info:
                # Create new service info with updated properties
                updated_info = ServiceInfo(
                    type_=self.service_info.type,
                    name=self.service_info.name,
                    addresses=self.service_info.addresses,
                    port=self.service_info.port,
                    properties=properties
                )
                
                # Unregister old service and register new one
                await self.zeroconf.async_unregister_service(self.service_info)
                await self.zeroconf.async_register_service(updated_info)
                self.service_info = updated_info
                logger.info("Service updated successfully")
        except Exception as e:
            logger.error(f"Failed to update service: {e}")
    
    async def stop(self):
        """Stop the mDNS service and cleanup"""
        logger.info("Stopping mDNS service...")
        try:
            # Stop service discovery
            if self.browser:
                logger.info("Stopping service browser...")
                self.browser.cancel()
                self.browser = None
                logger.info("Service browser stopped")
            
            # Unregister our service
            if self.service_info and self.zeroconf:
                logger.info("Unregistering service...")
                await self.zeroconf.async_unregister_service(self.service_info)
                logger.info("Service unregistered")
            
            # Close zeroconf
            if self.zeroconf:
                logger.info("Closing AsyncZeroconf...")
                await self.zeroconf.async_close()
                self.zeroconf = None
                logger.info("AsyncZeroconf closed")
            
            logger.info("mDNS service stopped successfully")
            
        except Exception as e:
            logger.error(f"Error stopping mDNS service: {e}")
    
    def get_discovered_services(self) -> List[Dict]:
        """Get list of discovered services"""
        services = []
        for name, info in self.discovered_services.items():
            services.append({
                "name": name,
                "addresses": info.parsed_addresses(),
                "port": info.port,
                "properties": info.properties
            })
        return services 