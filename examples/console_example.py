#!/usr/bin/env python3
"""
Simple console example demonstrating PyTextPrinter basic functionality.

This script shows console-based text printing features without requiring hardware printers.
"""

from pytextprinter import TextPrinter, Colors


def main():
    """Main example function for console printing."""
    print("PyTextPrinter Console Example")
    print("=" * 30)
    
    # Initialize the text printer for console output
    printer = TextPrinter()
    
    # Basic colored text printing
    print("\n1. Colored Text Output:")
    printer.print_colored("This is red text!", color="red")
    printer.print_colored("This is green text!", color="green", bold=True)
    printer.print_colored("This is blue text!", color="blue")
    
    # Banner printing
    print("\n2. Banner Example:")
    printer.print_banner("WELCOME", char="*", width=30)
    
    # Table printing
    print("\n3. Table Example:")
    data = [
        ["Alice", "25", "Engineer"],
        ["Bob", "30", "Designer"],
        ["Charlie", "28", "Manager"]
    ]
    headers = ["Name", "Age", "Role"]
    printer.print_table(data, headers=headers, title="Employee List")
    
    # List printing
    print("\n4. List Example:")
    items = ["Feature 1: Colored text", "Feature 2: Tables", "Feature 3: Banners"]
    printer.print_list(items, bullet="→", color="cyan")
    
    # Dictionary printing
    print("\n5. Dictionary Example:")
    config = {
        "Version": "0.1.0",
        "Platform": "Cross-platform",
        "Features": "Text, Hardware, ESC/POS"
    }
    printer.print_dict(config)
    
    # Progress bar example
    print("\n6. Progress Bar Example:")
    import time
    for i in range(11):
        progress = i / 10
        printer.print_progress_bar(progress, width=30)
        time.sleep(0.1)
    print()  # New line after progress bar
    
    # Hardware printer information (if available)
    print("\n7. Available Printers:")
    try:
        printers = printer.list_printers(text_only=False, refresh=True)
        if printers:
            for i, p in enumerate(printers, 1):
                status = "Ready" if printer.printer_manager.discovery.is_printer_available(p.name) else "Not Ready"
                print(f"  {i}. {p.name} - {status}")
        else:
            print("  No printers detected")
    except Exception as e:
        print(f"  Could not list printers: {e}")
    
    print("\n✓ Console example completed successfully!")
    print("\nTo test hardware printing, run: hardware_printer_example.py")


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\nExample interrupted by user.")
    except Exception as e:
        print(f"\nError: {e}")
        import traceback
        traceback.print_exc()