"""PyTextPrinter - A Python library for advanced text printing utilities."""

__version__ = "0.1.0"
__author__ = "Irwan Darmawan"
__email__ = "ir1keren@gmail.com"
__license__ = "MIT"
__url__ = "https://github.com/ir1keren/PyTextPrinter"
__description__ = "A Python library for advanced text printing utilities."

from .printer import TextPrinter
from .formatters import TableFormatter, BannerFormatter
from .printer_discovery import PrinterDiscovery, PrinterInfo
from .printer_manager import PrinterManager
from .printer_interface import PrinterInterface
from .escpos_commands import ESCPOSCommandBuilder, ESCPOSCommands, TextAlignment, BarcodeType

__all__ = [
    "TextPrinter", 
    "TableFormatter", 
    "BannerFormatter",
    "PrinterDiscovery",
    "PrinterInfo", 
    "PrinterManager",
    "PrinterInterface",
    "ESCPOSCommandBuilder",
    "ESCPOSCommands",
    "TextAlignment",
    "BarcodeType"
]