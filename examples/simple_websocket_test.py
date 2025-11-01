#!/usr/bin/env python3
"""
Simple WebSocket test to verify functionality without terminal conflicts.
"""

import asyncio
import sys
import os

# Add the parent directory to the Python path so we can import pytextprinter
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

try:
    from pytextprinter.websocket_client import PyTextPrinterWebSocketClient
except ImportError as e:
    print(f"Import error: {e}")
    print("Make sure PyTextPrinter is installed and dependencies are available")
    sys.exit(1)


async def simple_test():
    """Simple test of WebSocket functionality."""
    print("=" * 50)
    print("PYTEXTPRINTER WEBSOCKET TEST")
    print("=" * 50)
    
    client = PyTextPrinterWebSocketClient('http://localhost:8080')
    
    try:
        print("1. Connecting to WebSocket server...")
        connected = await client.connect()
        
        if not connected:
            print("✗ Failed to connect. Make sure server is running on localhost:8080")
            return False
            
        print("✓ Connected successfully!")
        
        # Wait for connection to stabilize
        await asyncio.sleep(0.5)
        
        # Test basic functionality
        print("\n2. Testing basic functionality...")
        
        # Get server info
        server_info = await client.get_server_info()
        if server_info:
            print(f"   ✓ Server version: {server_info.get('version', 'Unknown')}")
            print(f"   ✓ Connected clients: {server_info.get('connected_clients', 0)}")
        else:
            print("   ✗ Failed to get server info")
        
        # Test console printing
        print("\n3. Testing console printing...")
        
        text_output = await client.print_colored("Hello WebSocket!", color="green", bold=True)
        if text_output:
            print(f"   ✓ Colored text: {repr(text_output.strip())}")
        else:
            print("   ✗ Failed to print colored text")
            
        # Test banner
        banner_output = await client.print_banner("TEST", char="*", width=20)
        if banner_output:
            print("   ✓ Banner printed successfully")
        else:
            print("   ✗ Failed to print banner")
            
        # Test printer discovery
        print("\n4. Testing printer discovery...")
        
        printers = await client.list_printers(text_only=True, refresh=True)
        if printers is not None:
            print(f"   ✓ Found {len(printers)} printers")
            for i, printer in enumerate(printers[:3], 1):  # Show first 3
                print(f"     {i}. {printer.get('name', 'Unknown')} ({printer.get('driver', 'Unknown')})")
        else:
            print("   ✗ Failed to list printers")
            
        # Test auto-select
        selected = await client.auto_select_printer()
        if selected:
            printer_info = await client.get_selected_printer()
            if printer_info:
                print(f"   ✓ Auto-selected: {printer_info.get('name', 'Unknown')}")
            else:
                print("   ✓ Printer selected but info not available")
        else:
            print("   ✗ Failed to auto-select printer")
            
        print("\n✓ All tests completed successfully!")
        print("WebSocket functionality is working correctly.")
        return True
        
    except Exception as e:
        print(f"\n✗ Error during testing: {e}")
        import traceback
        traceback.print_exc()
        return False
        
    finally:
        await client.disconnect()
        print("\n✓ Disconnected from server")


if __name__ == "__main__":
    try:
        success = asyncio.run(simple_test())
        sys.exit(0 if success else 1)
    except KeyboardInterrupt:
        print("\nTest interrupted by user")
        sys.exit(1)
    except Exception as e:
        print(f"Unexpected error: {e}")
        sys.exit(1)