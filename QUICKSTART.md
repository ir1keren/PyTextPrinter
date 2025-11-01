# Quick Start Guide

## Installation and Setup

### 1. Set up Development Environment

```bash
# Navigate to the project directory
cd PyTextPrinter-Library

# Install in development mode (recommended for development)
pip install -e .

# Or install from source
pip install .
```

### 2. Install Dependencies

```bash
# Development dependencies (for testing and development)
pip install -r requirements-dev.txt

# For Windows hardware printer support
pip install pywin32
```

### 3. Basic Usage

#### Console Text Printing

```python
from pytextprinter import TextPrinter

# Initialize printer
printer = TextPrinter()

# Print colored text
printer.print_colored("Hello World!", color="green")

# Print a banner
printer.print_banner("WELCOME")

# Print a table
data = [["Name", "Age"], ["Alice", "25"], ["Bob", "30"]]
printer.print_table(data)
```

#### Hardware Printer Usage

```python
from pytextprinter import TextPrinter, BarcodeType

# Initialize printer
printer = TextPrinter()

# List available printers
printers = printer.list_printers(text_only=True)
for p in printers:
    print(f"Found: {p.name}")

# Select a printer
printer.select_printer("Your Printer Name")
# Or auto-select first available
printer.auto_select_printer()

# Print to hardware
printer.print_to_hardware("Hello from hardware printer!")

# Print barcode
printer.print_hardware_barcode("123456789", BarcodeType.CODE128)

# Print QR code
printer.print_hardware_qr_code("https://example.com")
```

### 4. Running Examples

```bash
# Console example (no hardware required)
python examples/console_example.py

# Hardware printer example (requires connected printer)
python examples/hardware_printer_example.py
```

### 5. Testing

```bash
# Run all tests
pytest

# Run with coverage
pytest --cov=pytextprinter

# Run specific test file
pytest tests/test_printer.py
```

## Troubleshooting

### ModuleNotFoundError
If you get "ModuleNotFoundError: No module named 'pytextprinter'":
1. Make sure you're in the correct directory
2. Install the package: `pip install -e .`
3. Check your Python environment is activated

### Hardware Printer Issues
1. Ensure printer is connected and powered on
2. Check printer permissions (may need admin rights)
3. Verify printer supports ESC/POS (thermal/receipt printers)
4. For Windows: Install `pywin32` package

### Import Errors
If you get import errors for platform-specific modules:
- Windows: `pip install pywin32`
- Linux/macOS: Install CUPS development packages

## Platform-Specific Notes

### Windows
- Supports native win32print APIs
- Fallback to command-line printing
- May require administrator privileges for some printers

### Linux
- Uses CUPS (lp, lpstat commands)
- May need to install: `sudo apt-get install cups-dev`

### macOS
- Uses CUPS and system_profiler
- Most functionality works out of the box