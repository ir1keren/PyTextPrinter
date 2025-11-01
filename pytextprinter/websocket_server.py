"""WebSocket server module for PyTextPrinter with socket.io compatibility."""

import asyncio
import json
import logging
import traceback
from typing import Dict, Any, Optional, List, Callable
from datetime import datetime
import socketio
from aiohttp import web, WSMsgType
from aiohttp.web import Request, WebSocketResponse

from .printer import TextPrinter
from .printer_discovery import PrinterInfo
from .escpos_commands import BarcodeType, TextAlignment


class PyTextPrinterWebSocketServer:
    """WebSocket server for PyTextPrinter with socket.io compatibility."""
    
    def __init__(self, host: str = 'localhost', port: int = 8080, cors_allowed_origins: str = "*"):
        """Initialize WebSocket server.
        
        Args:
            host: Server host address
            port: Server port number
            cors_allowed_origins: CORS allowed origins
        """
        self.host = host
        self.port = port
        self.printer = TextPrinter()
        self.clients: Dict[str, Dict[str, Any]] = {}
        
        # Setup logging
        logging.basicConfig(level=logging.INFO)
        self.logger = logging.getLogger(__name__)
        
        # Create socket.io server
        self.sio = socketio.AsyncServer(
            async_mode='aiohttp',
            cors_allowed_origins=cors_allowed_origins,
            logger=True,
            engineio_logger=True
        )
        
        # Create aiohttp app
        self.app = web.Application()
        self.sio.attach(self.app)
        
        # Register socket.io event handlers
        self._register_socketio_handlers()
        
        # Add HTTP routes
        self._setup_http_routes()
    
    def _register_socketio_handlers(self):
        """Register socket.io event handlers."""
        
        @self.sio.event
        async def connect(sid, environ):
            """Handle client connection."""
            self.logger.info(f"Client {sid} connected")
            self.clients[sid] = {
                'connected_at': datetime.now(),
                'last_activity': datetime.now()
            }
            
            # Send welcome message with available functionality
            await self.sio.emit('connected', {
                'message': 'Connected to PyTextPrinter WebSocket server',
                'available_functions': self._get_available_functions(),
                'server_info': {
                    'version': '0.1.0',
                    'features': ['console_printing', 'hardware_printing', 'escpos_commands']
                }
            }, room=sid)
        
        @self.sio.event
        async def disconnect(sid):
            """Handle client disconnection."""
            self.logger.info(f"Client {sid} disconnected")
            if sid in self.clients:
                del self.clients[sid]
        
        # Printer discovery and management
        @self.sio.event
        async def list_printers(sid, data=None):
            """List available printers."""
            try:
                text_only = data.get('text_only', True) if data else True
                refresh = data.get('refresh', False) if data else False
                
                printers = self.printer.list_printers(text_only=text_only, refresh=refresh)
                printer_list = [self._printer_info_to_dict(p) for p in printers]
                
                await self.sio.emit('printers_list', {
                    'success': True,
                    'printers': printer_list,
                    'count': len(printer_list)
                }, room=sid)
                
            except Exception as e:
                await self._send_error(sid, 'list_printers', str(e))
        
        @self.sio.event
        async def select_printer(sid, data):
            """Select a printer."""
            try:
                printer_name = data.get('printer_name')
                if not printer_name:
                    raise ValueError("printer_name is required")
                
                success = self.printer.select_printer(printer_name)
                selected_printer = self.printer.get_selected_printer()
                
                await self.sio.emit('printer_selected', {
                    'success': success,
                    'printer_name': printer_name,
                    'selected_printer': self._printer_info_to_dict(selected_printer) if selected_printer else None
                }, room=sid)
                
            except Exception as e:
                await self._send_error(sid, 'select_printer', str(e))
        
        @self.sio.event
        async def auto_select_printer(sid, data=None):
            """Auto-select first available text printer."""
            try:
                success = self.printer.auto_select_printer()
                selected_printer = self.printer.get_selected_printer()
                
                await self.sio.emit('printer_auto_selected', {
                    'success': success,
                    'selected_printer': self._printer_info_to_dict(selected_printer) if selected_printer else None
                }, room=sid)
                
            except Exception as e:
                await self._send_error(sid, 'auto_select_printer', str(e))
        
        @self.sio.event
        async def get_selected_printer(sid, data=None):
            """Get currently selected printer."""
            try:
                selected_printer = self.printer.get_selected_printer()
                
                await self.sio.emit('selected_printer_info', {
                    'success': True,
                    'selected_printer': self._printer_info_to_dict(selected_printer) if selected_printer else None
                }, room=sid)
                
            except Exception as e:
                await self._send_error(sid, 'get_selected_printer', str(e))
        
        # Console printing functions
        @self.sio.event
        async def print_colored(sid, data):
            """Print colored text to console."""
            try:
                text = data.get('text', '')
                color = data.get('color')
                bold = data.get('bold', False)
                end = data.get('end', '\n')
                
                # Capture output
                import io
                output_buffer = io.StringIO()
                temp_printer = TextPrinter(output=output_buffer)
                temp_printer.print_colored(text, color=color, bold=bold, end=end)
                output = output_buffer.getvalue()
                
                await self.sio.emit('text_printed', {
                    'success': True,
                    'output': output,
                    'type': 'colored_text'
                }, room=sid)
                
            except Exception as e:
                await self._send_error(sid, 'print_colored', str(e))
        
        @self.sio.event
        async def print_banner(sid, data):
            """Print a banner."""
            try:
                text = data.get('text', '')
                char = data.get('char', '=')
                width = data.get('width', 50)
                
                import io
                output_buffer = io.StringIO()
                temp_printer = TextPrinter(output=output_buffer)
                temp_printer.print_banner(text, char=char, width=width)
                output = output_buffer.getvalue()
                
                await self.sio.emit('banner_printed', {
                    'success': True,
                    'output': output,
                    'type': 'banner'
                }, room=sid)
                
            except Exception as e:
                await self._send_error(sid, 'print_banner', str(e))
        
        @self.sio.event
        async def print_table(sid, data):
            """Print a table."""
            try:
                table_data = data.get('data', [])
                headers = data.get('headers')
                title = data.get('title')
                
                import io
                output_buffer = io.StringIO()
                temp_printer = TextPrinter(output=output_buffer)
                temp_printer.print_table(table_data, headers=headers, title=title)
                output = output_buffer.getvalue()
                
                await self.sio.emit('table_printed', {
                    'success': True,
                    'output': output,
                    'type': 'table'
                }, room=sid)
                
            except Exception as e:
                await self._send_error(sid, 'print_table', str(e))
        
        @self.sio.event
        async def print_list(sid, data):
            """Print a formatted list."""
            try:
                items = data.get('items', [])
                bullet = data.get('bullet', '•')
                color = data.get('color')
                
                import io
                output_buffer = io.StringIO()
                temp_printer = TextPrinter(output=output_buffer)
                temp_printer.print_list(items, bullet=bullet, color=color)
                output = output_buffer.getvalue()
                
                await self.sio.emit('list_printed', {
                    'success': True,
                    'output': output,
                    'type': 'list'
                }, room=sid)
                
            except Exception as e:
                await self._send_error(sid, 'print_list', str(e))
        
        # Hardware printing functions
        @self.sio.event
        async def print_to_hardware(sid, data):
            """Print text to hardware printer."""
            try:
                text = data.get('text', '')
                encoding = data.get('encoding', 'cp437')
                
                success = self.printer.print_to_hardware(text, encoding=encoding)
                
                await self.sio.emit('hardware_printed', {
                    'success': success,
                    'type': 'hardware_text',
                    'message': 'Text sent to hardware printer' if success else 'Failed to send text to hardware printer'
                }, room=sid)
                
            except Exception as e:
                await self._send_error(sid, 'print_to_hardware', str(e))
        
        @self.sio.event
        async def print_hardware_banner(sid, data):
            """Print banner to hardware printer."""
            try:
                text = data.get('text', '')
                char = data.get('char', '=')
                width = data.get('width', 32)
                
                success = self.printer.print_hardware_banner(text, char=char, width=width)
                
                await self.sio.emit('hardware_banner_printed', {
                    'success': success,
                    'type': 'hardware_banner',
                    'message': 'Banner sent to hardware printer' if success else 'Failed to send banner to hardware printer'
                }, room=sid)
                
            except Exception as e:
                await self._send_error(sid, 'print_hardware_banner', str(e))
        
        @self.sio.event
        async def print_hardware_barcode(sid, data):
            """Print barcode to hardware printer."""
            try:
                barcode_data = data.get('data', '')
                barcode_type = data.get('type', 'CODE128')
                height = data.get('height', 100)
                width = data.get('width', 3)
                
                # Convert string to BarcodeType enum
                barcode_enum = getattr(BarcodeType, barcode_type, BarcodeType.CODE128)
                
                success = self.printer.print_hardware_barcode(
                    barcode_data, barcode_type=barcode_enum, height=height, width=width
                )
                
                await self.sio.emit('hardware_barcode_printed', {
                    'success': success,
                    'type': 'hardware_barcode',
                    'message': 'Barcode sent to hardware printer' if success else 'Failed to send barcode to hardware printer'
                }, room=sid)
                
            except Exception as e:
                await self._send_error(sid, 'print_hardware_barcode', str(e))
        
        @self.sio.event
        async def print_hardware_qr_code(sid, data):
            """Print QR code to hardware printer."""
            try:
                qr_data = data.get('data', '')
                size = data.get('size', 4)
                error_correction = data.get('error_correction', 1)
                
                success = self.printer.print_hardware_qr_code(
                    qr_data, size=size, error_correction=error_correction
                )
                
                await self.sio.emit('hardware_qr_printed', {
                    'success': success,
                    'type': 'hardware_qr',
                    'message': 'QR code sent to hardware printer' if success else 'Failed to send QR code to hardware printer'
                }, room=sid)
                
            except Exception as e:
                await self._send_error(sid, 'print_hardware_qr_code', str(e))
        
        @self.sio.event
        async def print_hardware_receipt(sid, data):
            """Print receipt to hardware printer."""
            try:
                lines = data.get('lines', [])
                cut_paper = data.get('cut_paper', True)
                
                success = self.printer.print_hardware_receipt(lines, cut_paper=cut_paper)
                
                await self.sio.emit('hardware_receipt_printed', {
                    'success': success,
                    'type': 'hardware_receipt',
                    'message': 'Receipt sent to hardware printer' if success else 'Failed to send receipt to hardware printer'
                }, room=sid)
                
            except Exception as e:
                await self._send_error(sid, 'print_hardware_receipt', str(e))
        
        @self.sio.event
        async def open_cash_drawer(sid, data=None):
            """Open cash drawer."""
            try:
                drawer_number = data.get('drawer_number', 1) if data else 1
                
                success = self.printer.open_cash_drawer(drawer_number=drawer_number)
                
                await self.sio.emit('cash_drawer_opened', {
                    'success': success,
                    'type': 'cash_drawer',
                    'message': 'Cash drawer command sent' if success else 'Failed to send cash drawer command'
                }, room=sid)
                
            except Exception as e:
                await self._send_error(sid, 'open_cash_drawer', str(e))
        
        @self.sio.event
        async def send_raw_escpos(sid, data):
            """Send raw ESC/POS commands."""
            try:
                commands_hex = data.get('commands_hex', '')
                commands_bytes = data.get('commands_bytes')
                
                if commands_bytes:
                    commands = bytes(commands_bytes)
                elif commands_hex:
                    commands = bytes.fromhex(commands_hex)
                else:
                    raise ValueError("Either commands_hex or commands_bytes is required")
                
                success = self.printer.send_escpos_to_hardware(commands)
                
                await self.sio.emit('raw_escpos_sent', {
                    'success': success,
                    'type': 'raw_escpos',
                    'message': 'Raw ESC/POS commands sent' if success else 'Failed to send raw ESC/POS commands'
                }, room=sid)
                
            except Exception as e:
                await self._send_error(sid, 'send_raw_escpos', str(e))
        
        # Utility functions
        @self.sio.event
        async def get_printer_status(sid, data=None):
            """Get printer status."""
            try:
                printer_name = data.get('printer_name') if data else None
                status = self.printer.get_printer_status(printer_name)
                
                await self.sio.emit('printer_status', {
                    'success': True,
                    'status': status,
                    'printer_name': printer_name
                }, room=sid)
                
            except Exception as e:
                await self._send_error(sid, 'get_printer_status', str(e))
        
        @self.sio.event
        async def is_printer_ready(sid, data=None):
            """Check if printer is ready."""
            try:
                printer_name = data.get('printer_name') if data else None
                is_ready = self.printer.is_hardware_printer_ready(printer_name)
                
                await self.sio.emit('printer_ready_status', {
                    'success': True,
                    'is_ready': is_ready,
                    'printer_name': printer_name
                }, room=sid)
                
            except Exception as e:
                await self._send_error(sid, 'is_printer_ready', str(e))
        
        @self.sio.event
        async def get_server_info(sid, data=None):
            """Get server information."""
            await self.sio.emit('server_info', {
                'success': True,
                'info': {
                    'version': '0.1.0',
                    'connected_clients': len(self.clients),
                    'available_functions': self._get_available_functions(),
                    'current_printer': self._printer_info_to_dict(self.printer.get_selected_printer())
                }
            }, room=sid)
    
    def _setup_http_routes(self):
        """Setup HTTP routes for web interface."""
        
        async def index(request):
            """Serve index page."""
            html_content = """
            <!DOCTYPE html>
            <html>
            <head>
                <title>PyTextPrinter WebSocket Server</title>
                <style>
                    body { font-family: Arial, sans-serif; margin: 40px; }
                    .container { max-width: 800px; }
                    .status { padding: 10px; background: #f0f0f0; border-radius: 5px; }
                    .endpoint { margin: 10px 0; padding: 10px; background: #e8f4f8; border-radius: 3px; }
                    code { background: #f5f5f5; padding: 2px 4px; border-radius: 3px; }
                </style>
            </head>
            <body>
                <div class="container">
                    <h1>PyTextPrinter WebSocket Server</h1>
                    <div class="status">
                        <p><strong>Status:</strong> Running</p>
                        <p><strong>WebSocket URL:</strong> <code>ws://""" + self.host + """:""" + str(self.port) + """</code></p>
                        <p><strong>Socket.IO URL:</strong> <code>http://""" + self.host + """:""" + str(self.port) + """</code></p>
                    </div>
                    
                    <h2>Available Functions</h2>
                    <div class="endpoint"><strong>list_printers</strong> - List available printers</div>
                    <div class="endpoint"><strong>select_printer</strong> - Select a specific printer</div>
                    <div class="endpoint"><strong>print_colored</strong> - Print colored text to console</div>
                    <div class="endpoint"><strong>print_to_hardware</strong> - Print text to hardware printer</div>
                    <div class="endpoint"><strong>print_hardware_barcode</strong> - Print barcode to hardware</div>
                    <div class="endpoint"><strong>print_hardware_qr_code</strong> - Print QR code to hardware</div>
                    
                    <h2>Example Usage</h2>
                    <pre><code>
// JavaScript client example
const socket = io('http://""" + self.host + """:""" + str(self.port) + """');

socket.emit('list_printers', {text_only: true});
socket.emit('print_colored', {text: 'Hello World!', color: 'green'});
socket.emit('print_to_hardware', {text: 'Hello Hardware!'});
                    </code></pre>
                </div>
            </body>
            </html>
            """
            return web.Response(text=html_content, content_type='text/html')
        
        async def health(request):
            """Health check endpoint."""
            return web.json_response({
                'status': 'healthy',
                'connected_clients': len(self.clients),
                'selected_printer': self._printer_info_to_dict(self.printer.get_selected_printer())
            })
        
        self.app.router.add_get('/', index)
        self.app.router.add_get('/health', health)
    
    def _get_available_functions(self) -> List[str]:
        """Get list of available WebSocket functions."""
        return [
            'list_printers', 'select_printer', 'auto_select_printer', 'get_selected_printer',
            'print_colored', 'print_banner', 'print_table', 'print_list',
            'print_to_hardware', 'print_hardware_banner', 'print_hardware_barcode',
            'print_hardware_qr_code', 'print_hardware_receipt', 'open_cash_drawer',
            'send_raw_escpos', 'get_printer_status', 'is_printer_ready', 'get_server_info'
        ]
    
    def _printer_info_to_dict(self, printer_info: Optional[PrinterInfo]) -> Optional[Dict[str, Any]]:
        """Convert PrinterInfo to dictionary."""
        if not printer_info:
            return None
        
        return {
            'name': printer_info.name,
            'driver': printer_info.driver,
            'port': printer_info.port,
            'status': printer_info.status,
            'is_default': printer_info.is_default,
            'is_shared': printer_info.is_shared,
            'location': printer_info.location,
            'comment': printer_info.comment
        }
    
    async def _send_error(self, sid: str, event: str, error_message: str):
        """Send error message to client."""
        self.logger.error(f"Error in {event}: {error_message}")
        await self.sio.emit('error', {
            'success': False,
            'event': event,
            'error': error_message,
            'timestamp': datetime.now().isoformat()
        }, room=sid)
    
    async def start_server(self):
        """Start the WebSocket server."""
        self.logger.info(f"Starting PyTextPrinter WebSocket server on {self.host}:{self.port}")
        
        runner = web.AppRunner(self.app)
        await runner.setup()
        site = web.TCPSite(runner, self.host, self.port)
        await site.start()
        
        self.logger.info(f"Server started successfully!")
        self.logger.info(f"WebSocket URL: ws://{self.host}:{self.port}")
        self.logger.info(f"Socket.IO URL: http://{self.host}:{self.port}")
        self.logger.info(f"Web interface: http://{self.host}:{self.port}")
    
    async def stop_server(self):
        """Stop the WebSocket server."""
        self.logger.info("Stopping PyTextPrinter WebSocket server...")
        await self.sio.shutdown()


async def main():
    """Main function to run the WebSocket server."""
    server = PyTextPrinterWebSocketServer(host='localhost', port=8080)
    
    try:
        await server.start_server()
        
        # Keep the server running
        while True:
            await asyncio.sleep(1)
            
    except KeyboardInterrupt:
        print("\nShutting down server...")
    finally:
        await server.stop_server()


if __name__ == "__main__":
    asyncio.run(main())