# PyTextPrinter

A Python library for advanced text printing utilities and ESC/POS thermal printer support.

## Features

- Text formatting and styling
- Table printing
- Progress bars
- Banner text generation
- Cross-platform hardware printer support (Windows/Linux/macOS)
- ESC/POS command support for thermal/receipt printers
- **WebSocket API with Socket.IO compatibility** - [See WebSocket Documentation](WEBSOCKET_IMPLEMENTATION.md)

## Installation

```bash
pip install pytextprinter
```

## Quick Start

```python
from pytextprinter import TextPrinter

printer = TextPrinter()
printer.print_text("Hello, World!")
printer.print_banner("Welcome to PyTextPrinter")
```

## WebSocket API

PyTextPrinter now includes complete WebSocket support with Socket.IO compatibility! Access all printer functionality over the network in real-time.

### Quick WebSocket Example

```python
# Start WebSocket Server
from pytextprinter.websocket_server import PyTextPrinterWebSocketServer
import asyncio

async def start_server():
    server = PyTextPrinterWebSocketServer(host='localhost', port=8080)
    await server.start_server()

asyncio.run(start_server())
```

```python
# WebSocket Client
from pytextprinter.websocket_client import PyTextPrinterWebSocketClient
import asyncio

async def client_example():
    client = PyTextPrinterWebSocketClient('http://localhost:8080')
    await client.connect()
    
    # Use any PyTextPrinter function via WebSocket
    await client.print_text("Hello WebSocket!")
    await client.list_printers()
    await client.print_to_hardware("Receipt text\n")
    
    await client.disconnect()

asyncio.run(client_example())
```

**📖 For complete WebSocket documentation, examples, and API reference, see: [WEBSOCKET_IMPLEMENTATION.md](WEBSOCKET_IMPLEMENTATION.md)**

## Development

### Setup Development Environment

```bash
pip install -e .
pip install -r requirements-dev.txt
```

### Running Tests

```bash
pytest
```

### Building Documentation

```bash
cd docs
make html
```

## License

MIT License - see LICENSE file for details.

## Contributing

Contributions are welcome! Please read our contributing guidelines and submit pull requests.