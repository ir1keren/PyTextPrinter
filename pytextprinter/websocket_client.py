"""WebSocket client utilities for PyTextPrinter."""

import asyncio
import json
import logging
from typing import Dict, Any, Optional, Callable, List
from datetime import datetime
import socketio


class PyTextPrinterWebSocketClient:
    """WebSocket client for connecting to PyTextPrinter server."""
    
    def __init__(self, server_url: str = 'http://localhost:8080'):
        """Initialize WebSocket client.
        
        Args:
            server_url: WebSocket server URL
        """
        self.server_url = server_url
        self.sio = socketio.AsyncClient()
        self.connected = False
        self.logger = logging.getLogger(__name__)
        self.response_handlers: Dict[str, Callable] = {}
        self.last_response: Optional[Dict[str, Any]] = None
        
        # Register default event handlers
        self._register_default_handlers()
    
    def _register_default_handlers(self):
        """Register default event handlers."""
        
        @self.sio.event
        async def connect():
            """Handle connection to server."""
            self.connected = True
            self.logger.info(f"Connected to PyTextPrinter server at {self.server_url}")
        
        @self.sio.event
        async def disconnect():
            """Handle disconnection from server."""
            self.connected = False
            self.logger.info("Disconnected from PyTextPrinter server")
        
        @self.sio.event
        async def connected(data):
            """Handle server welcome message."""
            self.logger.info(f"Server welcome: {data.get('message', '')}")
            if 'available_functions' in data:
                self.logger.info(f"Available functions: {', '.join(data['available_functions'])}")
        
        @self.sio.event
        async def error(data):
            """Handle server errors."""
            self.logger.error(f"Server error: {data.get('error', 'Unknown error')}")
            self.last_response = data
        
        # Response handlers for all printer functions
        response_events = [
            'printers_list', 'printer_selected', 'printer_auto_selected', 'selected_printer_info',
            'text_printed', 'banner_printed', 'table_printed', 'list_printed',
            'hardware_printed', 'hardware_banner_printed', 'hardware_barcode_printed',
            'hardware_qr_printed', 'hardware_receipt_printed', 'cash_drawer_opened',
            'raw_escpos_sent', 'printer_status', 'printer_ready_status', 'server_info'
        ]
        
        for event in response_events:
            self._register_response_handler(event)
    
    def _register_response_handler(self, event_name: str):
        """Register a response handler for an event."""
        
        @self.sio.event
        async def handler(data):
            self.last_response = data
            self.logger.debug(f"Received {event_name}: {data}")
            
            # Call custom handler if registered
            if event_name in self.response_handlers:
                await self.response_handlers[event_name](data)
        
        # Dynamically set the handler
        handler.__name__ = event_name
        self.sio.event(handler)
    
    async def connect(self) -> bool:
        """Connect to the WebSocket server.
        
        Returns:
            True if connection successful, False otherwise
        """
        try:
            await self.sio.connect(self.server_url)
            return True
        except Exception as e:
            self.logger.error(f"Failed to connect: {e}")
            return False
    
    async def disconnect(self):
        """Disconnect from the WebSocket server."""
        if self.connected:
            await self.sio.disconnect()
    
    def register_handler(self, event: str, handler: Callable):
        """Register a custom event handler.
        
        Args:
            event: Event name
            handler: Async function to handle the event
        """
        self.response_handlers[event] = handler
    
    async def wait_for_response(self, timeout: float = 5.0) -> Optional[Dict[str, Any]]:
        """Wait for a response from the server.
        
        Args:
            timeout: Timeout in seconds
            
        Returns:
            Last response received or None if timeout
        """
        start_time = asyncio.get_event_loop().time()
        
        while asyncio.get_event_loop().time() - start_time < timeout:
            if self.last_response:
                response = self.last_response
                self.last_response = None  # Clear for next call
                return response
            await asyncio.sleep(0.1)
        
        return None
    
    # Printer discovery and management methods
    async def list_printers(self, text_only: bool = True, refresh: bool = False) -> Optional[List[Dict]]:
        """List available printers.
        
        Args:
            text_only: Only list text/thermal printers
            refresh: Refresh printer cache
            
        Returns:
            List of printers or None if failed
        """
        await self.sio.emit('list_printers', {
            'text_only': text_only,
            'refresh': refresh
        })
        
        response = await self.wait_for_response()
        if response and response.get('success'):
            return response.get('printers', [])
        return None
    
    async def select_printer(self, printer_name: str) -> bool:
        """Select a printer.
        
        Args:
            printer_name: Name of the printer to select
            
        Returns:
            True if successful, False otherwise
        """
        await self.sio.emit('select_printer', {'printer_name': printer_name})
        
        response = await self.wait_for_response()
        return response and response.get('success', False)
    
    async def auto_select_printer(self) -> bool:
        """Auto-select first available text printer.
        
        Returns:
            True if successful, False otherwise
        """
        await self.sio.emit('auto_select_printer')
        
        response = await self.wait_for_response()
        return response and response.get('success', False)
    
    async def get_selected_printer(self) -> Optional[Dict[str, Any]]:
        """Get currently selected printer.
        
        Returns:
            Printer info dict or None
        """
        await self.sio.emit('get_selected_printer')
        
        response = await self.wait_for_response()
        if response and response.get('success'):
            return response.get('selected_printer')
        return None
    
    # Console printing methods
    async def print_text(self, text: str, bold: bool = False) -> Optional[str]:
        """Print text.
        
        Args:
            text: Text to print
            bold: Bold text
            
        Returns:
            Printed output or None if failed
        """
        await self.sio.emit('print_text', {
            'text': text,
            'bold': bold
        })
        
        response = await self.wait_for_response()
        if response and response.get('success'):
            return response.get('output')
        return None
    
    async def print_banner(self, text: str, char: str = '=', width: int = 50) -> Optional[str]:
        """Print a banner.
        
        Args:
            text: Banner text
            char: Border character
            width: Banner width
            
        Returns:
            Printed output or None if failed
        """
        await self.sio.emit('print_banner', {
            'text': text,
            'char': char,
            'width': width
        })
        
        response = await self.wait_for_response()
        if response and response.get('success'):
            return response.get('output')
        return None
    
    async def print_table(self, data: List[List[str]], headers: Optional[List[str]] = None, 
                         title: Optional[str] = None) -> Optional[str]:
        """Print a table.
        
        Args:
            data: Table data
            headers: Column headers
            title: Table title
            
        Returns:
            Printed output or None if failed
        """
        await self.sio.emit('print_table', {
            'data': data,
            'headers': headers,
            'title': title
        })
        
        response = await self.wait_for_response()
        if response and response.get('success'):
            return response.get('output')
        return None
    
    async def print_list(self, items: List[str], bullet: str = '•') -> Optional[str]:
        """Print a formatted list.
        
        Args:
            items: List items
            bullet: Bullet character
            
        Returns:
            Printed output or None if failed
        """
        await self.sio.emit('print_list', {
            'items': items,
            'bullet': bullet
        })
        
        response = await self.wait_for_response()
        if response and response.get('success'):
            return response.get('output')
        return None
    
    # Hardware printing methods
    async def print_to_hardware(self, text: str, encoding: str = 'cp437') -> bool:
        """Print text to hardware printer.
        
        Args:
            text: Text to print
            encoding: Text encoding
            
        Returns:
            True if successful, False otherwise
        """
        await self.sio.emit('print_to_hardware', {
            'text': text,
            'encoding': encoding
        })
        
        response = await self.wait_for_response()
        return response and response.get('success', False)
    
    async def print_hardware_banner(self, text: str, char: str = '=', width: int = 32) -> bool:
        """Print banner to hardware printer.
        
        Args:
            text: Banner text
            char: Border character
            width: Banner width
            
        Returns:
            True if successful, False otherwise
        """
        await self.sio.emit('print_hardware_banner', {
            'text': text,
            'char': char,
            'width': width
        })
        
        response = await self.wait_for_response()
        return response and response.get('success', False)
    
    async def print_hardware_barcode(self, data: str, barcode_type: str = 'CODE128', 
                                    height: int = 100, width: int = 3) -> bool:
        """Print barcode to hardware printer.
        
        Args:
            data: Barcode data
            barcode_type: Barcode type
            height: Barcode height
            width: Barcode width
            
        Returns:
            True if successful, False otherwise
        """
        await self.sio.emit('print_hardware_barcode', {
            'data': data,
            'type': barcode_type,
            'height': height,
            'width': width
        })
        
        response = await self.wait_for_response()
        return response and response.get('success', False)
    
    async def print_hardware_qr_code(self, data: str, size: int = 4, error_correction: int = 1) -> bool:
        """Print QR code to hardware printer.
        
        Args:
            data: QR code data
            size: QR code size
            error_correction: Error correction level
            
        Returns:
            True if successful, False otherwise
        """
        await self.sio.emit('print_hardware_qr_code', {
            'data': data,
            'size': size,
            'error_correction': error_correction
        })
        
        response = await self.wait_for_response()
        return response and response.get('success', False)
    
    async def print_hardware_receipt(self, lines: List[str], cut_paper: bool = True) -> bool:
        """Print receipt to hardware printer.
        
        Args:
            lines: Receipt lines
            cut_paper: Cut paper after printing
            
        Returns:
            True if successful, False otherwise
        """
        await self.sio.emit('print_hardware_receipt', {
            'lines': lines,
            'cut_paper': cut_paper
        })
        
        response = await self.wait_for_response()
        return response and response.get('success', False)
    
    async def open_cash_drawer(self, drawer_number: int = 1) -> bool:
        """Open cash drawer.
        
        Args:
            drawer_number: Drawer number
            
        Returns:
            True if successful, False otherwise
        """
        await self.sio.emit('open_cash_drawer', {'drawer_number': drawer_number})
        
        response = await self.wait_for_response()
        return response and response.get('success', False)
    
    async def send_raw_escpos(self, commands_hex: str) -> bool:
        """Send raw ESC/POS commands.
        
        Args:
            commands_hex: Hex string of commands
            
        Returns:
            True if successful, False otherwise
        """
        await self.sio.emit('send_raw_escpos', {'commands_hex': commands_hex})
        
        response = await self.wait_for_response()
        return response and response.get('success', False)
    
    # Utility methods
    async def get_printer_status(self, printer_name: Optional[str] = None) -> Optional[str]:
        """Get printer status.
        
        Args:
            printer_name: Printer name (uses selected if None)
            
        Returns:
            Status string or None
        """
        await self.sio.emit('get_printer_status', {'printer_name': printer_name})
        
        response = await self.wait_for_response()
        if response and response.get('success'):
            return response.get('status')
        return None
    
    async def is_printer_ready(self, printer_name: Optional[str] = None) -> bool:
        """Check if printer is ready.
        
        Args:
            printer_name: Printer name (uses selected if None)
            
        Returns:
            True if ready, False otherwise
        """
        await self.sio.emit('is_printer_ready', {'printer_name': printer_name})
        
        response = await self.wait_for_response()
        return response and response.get('is_ready', False)
    
    async def get_server_info(self) -> Optional[Dict[str, Any]]:
        """Get server information.
        
        Returns:
            Server info dict or None
        """
        await self.sio.emit('get_server_info')
        
        response = await self.wait_for_response()
        if response and response.get('success'):
            return response.get('info')
        return None


class PyTextPrinterSyncClient:
    """Synchronous wrapper for PyTextPrinterWebSocketClient."""
    
    def __init__(self, server_url: str = 'http://localhost:8080'):
        """Initialize sync client.
        
        Args:
            server_url: WebSocket server URL
        """
        self.client = PyTextPrinterWebSocketClient(server_url)
        self.loop = None
    
    def _run_async(self, coro):
        """Run async coroutine in sync context."""
        try:
            if self.loop is None:
                self.loop = asyncio.new_event_loop()
                asyncio.set_event_loop(self.loop)
            return self.loop.run_until_complete(coro)
        except RuntimeError:
            # If there's already a running loop, create a new one
            import threading
            result = []
            exception = []
            
            def run_in_thread():
                try:
                    new_loop = asyncio.new_event_loop()
                    asyncio.set_event_loop(new_loop)
                    result.append(new_loop.run_until_complete(coro))
                except Exception as e:
                    exception.append(e)
                finally:
                    new_loop.close()
            
            thread = threading.Thread(target=run_in_thread)
            thread.start()
            thread.join()
            
            if exception:
                raise exception[0]
            return result[0] if result else None
    
    def connect(self) -> bool:
        """Connect to server."""
        return self._run_async(self.client.connect())
    
    def disconnect(self):
        """Disconnect from server."""
        self._run_async(self.client.disconnect())
    
    def list_printers(self, text_only: bool = True, refresh: bool = False) -> Optional[List[Dict]]:
        """List available printers."""
        return self._run_async(self.client.list_printers(text_only, refresh))
    
    def select_printer(self, printer_name: str) -> bool:
        """Select a printer."""
        return self._run_async(self.client.select_printer(printer_name))
    
    def print_text(self, text: str, bold: bool = False) -> Optional[str]:
        """Print text."""
        return self._run_async(self.client.print_text(text, bold))
    
    def print_to_hardware(self, text: str, encoding: str = 'cp437') -> bool:
        """Print to hardware."""
        return self._run_async(self.client.print_to_hardware(text, encoding))
    
    def print_hardware_barcode(self, data: str, barcode_type: str = 'CODE128') -> bool:
        """Print barcode to hardware."""
        return self._run_async(self.client.print_hardware_barcode(data, barcode_type))
    
    def __enter__(self):
        """Context manager entry."""
        self.connect()
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        """Context manager exit."""
        self.disconnect()