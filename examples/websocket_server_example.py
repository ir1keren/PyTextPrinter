#!/usr/bin/env python3
"""
WebSocket server example for PyTextPrinter.

This script demonstrates how to run a WebSocket server that exposes
all PyTextPrinter functionality via socket.io compatible WebSocket connections.
"""

import asyncio
import logging
import signal
import sys
from pytextprinter.websocket_server import PyTextPrinterWebSocketServer


async def main():
    """Main function to run the WebSocket server."""
    print("PyTextPrinter WebSocket Server Example")
    print("=" * 40)
    
    # Configure logging
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    
    # Create and start server
    server = PyTextPrinterWebSocketServer(
        host='localhost',
        port=8080,
        cors_allowed_origins="*"
    )
    
    print(f"\nStarting WebSocket server...")
    print(f"WebSocket URL: ws://localhost:8080")
    print(f"Socket.IO URL: http://localhost:8080")
    print(f"Web interface: http://localhost:8080")
    print(f"\nPress Ctrl+C to stop the server\n")
    
    try:
        await server.start_server()
        
        # Keep the server running
        while True:
            await asyncio.sleep(1)
            
    except KeyboardInterrupt:
        print("\n\nShutting down server...")
    except Exception as e:
        print(f"Server error: {e}")
    finally:
        await server.stop_server()
        print("Server stopped.")


def signal_handler(signum, frame):
    """Handle Ctrl+C gracefully."""
    print("\nReceived interrupt signal...")
    sys.exit(0)


if __name__ == "__main__":
    # Handle Ctrl+C
    signal.signal(signal.SIGINT, signal_handler)
    
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\nServer stopped by user.")
    except Exception as e:
        print(f"Error: {e}")
        sys.exit(1)