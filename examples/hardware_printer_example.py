#!/usr/bin/env python3
"""
Example script demonstrating PyTextPrinter hardware printer functionality.

This script shows how to:
1. List connected printers
2. Select a printer
3. Send text and ESC/POS commands to a hardware printer
4. Print barcodes and QR codes
"""

from pytextprinter import TextPrinter, BarcodeType


def main():
    """Main example function."""
    print("PyTextPrinter Hardware Printer Example")
    print("=" * 40)
    
    # Initialize the text printer
    printer = TextPrinter()
    
    # List available text/thermal printers
    print("\n1. Listing available text/thermal printers:")
    text_printers = printer.list_printers(text_only=True, refresh=True)
    
    if not text_printers:
        print("No text/thermal printers found.")
        print("Make sure you have a thermal or receipt printer connected.")
        return
    
    for i, p in enumerate(text_printers, 1):
        status = "✓" if printer.printer_manager.discovery.is_printer_available(p.name) else "✗"
        print(f"  {i}. {status} {p.name} ({p.driver}) - {p.port}")
    
    # Auto-select the first available text printer
    print("\n2. Auto-selecting first available text printer:")
    if printer.auto_select_printer():
        selected = printer.get_selected_printer()
        print(f"   Selected: {selected.name}")
    else:
        print("   Failed to select a printer. Switching to interactive mode.")
        
        # Try interactive selection
        print("\n3. Interactive printer selection:")
        if not printer.select_printer_interactive():
            print("No printer selected. Exiting.")
            return
    
    # Get selected printer info
    selected_printer = printer.get_selected_printer()
    print(f"\nUsing printer: {selected_printer.name}")
    
    # Check if printer is ready
    print("\n4. Checking printer status:")
    if printer.is_hardware_printer_ready():
        print("   Printer is ready!")
    else:
        print("   Warning: Printer may not be ready.")
    
    # Print a simple test
    print("\n5. Printing simple text:")
    success = printer.print_to_hardware("Hello from PyTextPrinter!\n\n")
    print(f"   Text printing: {'Success' if success else 'Failed'}")
    
    # Print a formatted banner
    print("\n6. Printing banner:")
    success = printer.print_hardware_banner("PYTEXTPRINTER", width=32)
    print(f"   Banner printing: {'Success' if success else 'Failed'}")
    
    # Print a barcode
    print("\n7. Printing barcode:")
    success = printer.print_hardware_barcode("123456789012", BarcodeType.EAN13)
    print(f"   Barcode printing: {'Success' if success else 'Failed'}")
    
    # Print a QR code
    print("\n8. Printing QR code:")
    success = printer.print_hardware_qr_code("https://github.com/pytextprinter", size=6)
    print(f"   QR code printing: {'Success' if success else 'Failed'}")
    
    # Print a sample receipt
    print("\n9. Printing sample receipt:")
    receipt_lines = [
        "       SAMPLE STORE",
        "      123 Main Street",
        "    City, State 12345",
        "",
        "Receipt #: 12345",
        "Date: 2025-10-31",
        "",
        "Item 1             $10.00",
        "Item 2              $5.50",
        "Tax                 $1.55",
        "------------------------",
        "Total:             $17.05",
        "",
        "Payment: Cash      $20.00",
        "Change:             $2.95",
        "",
        "    Thank you for",
        "     your business!",
        "",
    ]
    
    success = printer.print_hardware_receipt(receipt_lines, cut_paper=True)
    print(f"   Receipt printing: {'Success' if success else 'Failed'}")
    
    # Test cash drawer (if connected)
    print("\n10. Testing cash drawer:")
    try:
        success = printer.open_cash_drawer()
        print(f"    Cash drawer command: {'Sent' if success else 'Failed'}")
    except Exception as e:
        print(f"    Cash drawer: Not available ({e})")
    
    print("\nExample completed!")
    print("\nNote: If any operations failed, make sure:")
    print("  - The printer is properly connected and powered on")
    print("  - You have proper permissions to access the printer")
    print("  - The printer supports ESC/POS commands (thermal/receipt printers)")
    print("  - Paper is loaded and the printer is ready")


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\nExample interrupted by user.")
    except Exception as e:
        print(f"\nError: {e}")
        print("Make sure you have a compatible printer connected.")