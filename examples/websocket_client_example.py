#!/usr/bin/env python3
"""
WebSocket client example for PyTextPrinter.

This script demonstrates how to connect to a PyTextPrinter WebSocket server
and use all available functionality through the client interface.
"""

import asyncio
import logging
from pytextprinter.websocket_client import PyTextPrinterWebSocketClient


async def main():
    """Main function to demonstrate WebSocket client usage."""
    print("PyTextPrinter WebSocket Client Example")
    print("=" * 40)
    
    # Configure logging
    logging.basicConfig(level=logging.INFO)
    
    # Create client
    client = PyTextPrinterWebSocketClient('http://localhost:8080')
    
    try:
        # Connect to server
        print("\n1. Connecting to WebSocket server...")
        connected = await client.connect()
        
        if not connected:
            print("Failed to connect to server. Make sure the server is running.")
            return
        
        print("✓ Connected successfully!")
        
        # Wait a moment for connection to stabilize
        await asyncio.sleep(1)
        
        # Get server info
        print("\n2. Getting server information...")
        server_info = await client.get_server_info()
        if server_info:
            print(f"   Server version: {server_info.get('version', 'Unknown')}")
            print(f"   Connected clients: {server_info.get('connected_clients', 0)}")
            print(f"   Available functions: {len(server_info.get('available_functions', []))}")
        
        # List available printers
        print("\n3. Listing available printers...")
        printers = await client.list_printers(text_only=True, refresh=True)
        if printers:
            for i, printer in enumerate(printers, 1):
                print(f"   {i}. {printer['name']} ({printer['driver']}) - {printer['port']}")
        else:
            print("   No printers found or failed to list printers")
        
        # Auto-select a printer
        print("\n4. Auto-selecting printer...")
        selected = await client.auto_select_printer()
        if selected:
            printer_info = await client.get_selected_printer()
            if printer_info:
                print(f"   ✓ Selected: {printer_info['name']}")
            else:
                print("   ✓ Printer selected but info not available")
        else:
            print("   ✗ Failed to auto-select printer")
        
        # Test console printing
        print("\n5. Testing console printing...")
        
        # Print text
        output = await client.print_text("Hello from WebSocket!", bold=True)
        if output:
            print(f"   Text output: {repr(output.strip())}")
        
        # Print banner
        banner_output = await client.print_banner("WEBSOCKET TEST", char="*", width=30)
        if banner_output:
            print("   Banner printed:")
            for line in banner_output.strip().split('\n'):
                print(f"     {line}")
        
        # Print table
        table_data = [
            ["Feature", "Status"],
            ["WebSocket", "✓ Working"],
            ["Socket.IO", "✓ Compatible"],
            ["Console Print", "✓ Tested"]
        ]
        table_output = await client.print_table(table_data, headers=["Component", "Status"], title="Test Results")
        if table_output:
            print("   Table printed:")
            for line in table_output.strip().split('\n'):
                print(f"     {line}")
        
        # Print list
        items = ["Real-time communication", "Cross-platform support", "Easy integration"]
        list_output = await client.print_list(items, bullet="→")
        if list_output:
            print("   List printed:")
            for line in list_output.strip().split('\n'):
                print(f"     {line}")
        
        # Test hardware printing (if printer is selected)
        selected_printer = await client.get_selected_printer()
        if selected_printer:
            print(f"\n6. Testing hardware printing with {selected_printer['name']}...")
            
            # Check if printer is ready
            is_ready = await client.is_printer_ready()
            print(f"   Printer ready: {is_ready}")
            
            # Print simple text
            success = await client.print_to_hardware("Hello from WebSocket client!\n\n")
            print(f"   Text printing: {'✓ Success' if success else '✗ Failed'}")
            
            # Print banner
            success = await client.print_hardware_banner("WEBSOCKET", width=32)
            print(f"   Banner printing: {'✓ Success' if success else '✗ Failed'}")
            
            # Print barcode
            success = await client.print_hardware_barcode("123456789", "CODE128")
            print(f"   Barcode printing: {'✓ Success' if success else '✗ Failed'}")
            
            # Print QR code
            success = await client.print_hardware_qr_code("WebSocket Test QR Code", size=4)
            print(f"   QR code printing: {'✓ Success' if success else '✗ Failed'}")
            
            # Print receipt
            receipt_lines = [
                "    WEBSOCKET TEST RECEIPT",
                "    =====================",
                "",
                "Item: WebSocket Demo",
                "Price: $0.00 (Free!)",
                "",
                "Total: $0.00",
                "",
                "Thank you for testing!",
                ""
            ]
            success = await client.print_hardware_receipt(receipt_lines, cut_paper=True)
            print(f"   Receipt printing: {'✓ Success' if success else '✗ Failed'}")
            
            # Test cash drawer
            success = await client.open_cash_drawer()
            print(f"   Cash drawer: {'✓ Command sent' if success else '✗ Failed'}")
            
        else:
            print("\n6. Skipping hardware tests (no printer selected)")
        
        # Test utility functions
        print("\n7. Testing utility functions...")
        
        # Get printer status
        if selected_printer:
            status = await client.get_printer_status()
            print(f"   Printer status: {status}")
        
        print("\n✓ All tests completed successfully!")
        print("\nWebSocket functionality is working correctly.")
        
    except Exception as e:
        print(f"\nError during testing: {e}")
        import traceback
        traceback.print_exc()
        
    finally:
        # Disconnect
        print("\nDisconnecting...")
        await client.disconnect()
        print("✓ Disconnected")


async def simple_example():
    """Simple example showing basic usage."""
    print("\n" + "="*50)
    print("SIMPLE USAGE EXAMPLE")
    print("="*50)
    
    client = PyTextPrinterWebSocketClient('http://localhost:8080')
    
    try:
        # Connect
        await client.connect()
        await asyncio.sleep(0.5)  # Wait for connection
        
        # Print text
        output = await client.print_text("Simple WebSocket Test", bold=True)
        print(f"Output: {output}")
        
        # List printers
        printers = await client.list_printers()
        print(f"Found {len(printers) if printers else 0} printers")
        
    finally:
        await client.disconnect()


if __name__ == "__main__":
    try:
        print("Make sure the WebSocket server is running first!")
        print("Run: python examples/websocket_server_example.py")
        print()
        
        # Run main example
        asyncio.run(main())
        
        # Run simple example
        asyncio.run(simple_example())
        
    except KeyboardInterrupt:
        print("\nClient stopped by user.")
    except Exception as e:
        print(f"Error: {e}")
        print("\nMake sure the WebSocket server is running:")
        print("python examples/websocket_server_example.py")