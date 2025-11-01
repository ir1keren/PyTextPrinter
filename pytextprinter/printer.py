"""Main text printer class with various printing utilities."""

import sys
from typing import Optional, Union, List, Dict, Any
from .colors import Colors
from .formatters import TableFormatter, BannerFormatter
from .printer_manager import PrinterManager
from .printer_interface import PrinterInterface
from .escpos_commands import ESCPOSCommandBuilder, TextAlignment, BarcodeType
from .printer_discovery import PrinterInfo


class TextPrinter:
    """Main class for printing formatted text with colors and styles."""
    
    def __init__(self, output=None):
        """Initialize TextPrinter.
        
        Args:
            output: Output stream (default: sys.stdout)
        """
        self.output = output or sys.stdout
        self.table_formatter = TableFormatter()
        self.banner_formatter = BannerFormatter()
        
        # Hardware printer functionality
        self.printer_manager = PrinterManager()
        self.printer_interface = PrinterInterface()
        self.escpos = ESCPOSCommandBuilder()
    
    def print_colored(self, text: str, color: Optional[str] = None, 
                     bold: bool = False, end: str = '\n') -> None:
        """Print text with color formatting.
        
        Args:
            text: Text to print
            color: Color name (red, green, blue, etc.)
            bold: Whether to make text bold
            end: String appended after the text
        """
        if color:
            color_code = Colors.get_color(color)
            if bold:
                color_code = color_code.replace('\033[', '\033[1;')
            formatted_text = f"{color_code}{text}{Colors.RESET}"
        else:
            formatted_text = text
            
        print(formatted_text, end=end, file=self.output)
    
    def print_banner(self, text: str, char: str = '=', width: int = 50) -> None:
        """Print a banner with the given text.
        
        Args:
            text: Text for the banner
            char: Character to use for the banner border
            width: Width of the banner
        """
        banner = self.banner_formatter.create_banner(text, char, width)
        print(banner, file=self.output)
    
    def print_table(self, data: List[List[str]], headers: Optional[List[str]] = None,
                   title: Optional[str] = None) -> None:
        """Print data in a formatted table.
        
        Args:
            data: 2D list of table data
            headers: Optional list of column headers
            title: Optional table title
        """
        table = self.table_formatter.format_table(data, headers, title)
        print(table, file=self.output)
    
    def print_progress_bar(self, progress: float, width: int = 50, 
                          char: str = '█', empty_char: str = '░') -> None:
        """Print a progress bar.
        
        Args:
            progress: Progress value between 0.0 and 1.0
            width: Width of the progress bar
            char: Character for filled portions
            empty_char: Character for empty portions
        """
        filled_width = int(width * progress)
        bar = char * filled_width + empty_char * (width - filled_width)
        percentage = progress * 100
        progress_text = f"[{bar}] {percentage:.1f}%"
        print(f"\r{progress_text}", end='', file=self.output)
    
    def print_list(self, items: List[str], bullet: str = '•', 
                  color: Optional[str] = None) -> None:
        """Print a formatted list.
        
        Args:
            items: List of items to print
            bullet: Bullet character
            color: Color for the bullets
        """
        for item in items:
            if color:
                self.print_colored(f"{bullet} {item}", color=color)
            else:
                print(f"{bullet} {item}", file=self.output)
    
    def print_dict(self, data: Dict[str, Any], indent: int = 2) -> None:
        """Print a dictionary in a formatted way.
        
        Args:
            data: Dictionary to print
            indent: Indentation level
        """
        for key, value in data.items():
            spaces = ' ' * indent
            self.print_colored(f"{spaces}{key}:", color='cyan', end=' ')
            print(value, file=self.output)
    
    # Hardware Printer Methods
    def list_printers(self, text_only: bool = True, refresh: bool = False) -> List[PrinterInfo]:
        """List available printers.
        
        Args:
            text_only: If True, only return text/thermal printers
            refresh: Whether to refresh the printer cache
            
        Returns:
            List of available printers
        """
        if text_only:
            return self.printer_manager.list_text_printers(refresh)
        else:
            return self.printer_manager.list_all_printers(refresh)
    
    def select_printer(self, printer_name: str) -> bool:
        """Select a printer for hardware printing operations.
        
        Args:
            printer_name: Name of the printer to select
            
        Returns:
            True if printer was successfully selected, False otherwise
        """
        return self.printer_manager.select_printer(printer_name)
    
    def select_printer_interactive(self, text_only: bool = True) -> bool:
        """Interactively select a printer from available printers.
        
        Args:
            text_only: If True, only show text/thermal printers
            
        Returns:
            True if a printer was selected, False otherwise
        """
        return self.printer_manager.select_printer_interactive(text_only)
    
    def auto_select_printer(self) -> bool:
        """Automatically select the first available text printer.
        
        Returns:
            True if a printer was selected, False otherwise
        """
        return self.printer_manager.auto_select_text_printer()
    
    def get_selected_printer(self) -> Optional[PrinterInfo]:
        """Get information about the currently selected printer.
        
        Returns:
            Selected printer info, or None if no printer is selected
        """
        return self.printer_manager.get_selected_printer()
    
    def print_to_hardware(self, text: str, encoding: str = 'cp437') -> bool:
        """Print text to the selected hardware printer.
        
        Args:
            text: Text to print
            encoding: Character encoding to use
            
        Returns:
            True if printing was successful, False otherwise
        """
        selected_printer = self.get_selected_printer()
        if not selected_printer:
            print("Error: No printer selected. Use select_printer() first.")
            return False
        
        return self.printer_interface.send_text(selected_printer.name, text, encoding)
    
    def send_escpos_to_hardware(self, commands: bytes) -> bool:
        """Send raw ESC/POS commands to the selected hardware printer.
        
        Args:
            commands: ESC/POS command sequence
            
        Returns:
            True if commands were sent successfully, False otherwise
        """
        selected_printer = self.get_selected_printer()
        if not selected_printer:
            print("Error: No printer selected. Use select_printer() first.")
            return False
        
        return self.printer_interface.send_escpos_commands(selected_printer.name, commands)
    
    def print_hardware_banner(self, text: str, char: str = '=', width: int = 32) -> bool:
        """Print a banner to the selected hardware printer using ESC/POS.
        
        Args:
            text: Text for the banner
            char: Character to use for the banner border
            width: Width of the banner
            
        Returns:
            True if printing was successful, False otherwise
        """
        selected_printer = self.get_selected_printer()
        if not selected_printer:
            print("Error: No printer selected. Use select_printer() first.")
            return False
        
        # Build ESC/POS commands for banner
        commands = (self.escpos
                   .clear()
                   .init_printer()
                   .align_center()
                   .bold(True)
                   .line(char * width)
                   .line(text)
                   .line(char * width)
                   .bold(False)
                   .align_left()
                   .feed_lines(2)
                   .get_commands())
        
        return self.send_escpos_to_hardware(commands)
    
    def print_hardware_barcode(self, data: str, barcode_type: BarcodeType = BarcodeType.CODE128,
                              height: int = 100, width: int = 3) -> bool:
        """Print a barcode to the selected hardware printer.
        
        Args:
            data: Barcode data
            barcode_type: Type of barcode
            height: Barcode height
            width: Barcode width
            
        Returns:
            True if printing was successful, False otherwise
        """
        selected_printer = self.get_selected_printer()
        if not selected_printer:
            print("Error: No printer selected. Use select_printer() first.")
            return False
        
        commands = (self.escpos
                   .clear()
                   .init_printer()
                   .align_center()
                   .barcode(data, barcode_type, height, width)
                   .align_left()
                   .feed_lines(3)
                   .get_commands())
        
        return self.send_escpos_to_hardware(commands)
    
    def print_hardware_qr_code(self, data: str, size: int = 4, error_correction: int = 1) -> bool:
        """Print a QR code to the selected hardware printer.
        
        Args:
            data: QR code data
            size: QR code size (1-16)
            error_correction: Error correction level (0-3)
            
        Returns:
            True if printing was successful, False otherwise
        """
        selected_printer = self.get_selected_printer()
        if not selected_printer:
            print("Error: No printer selected. Use select_printer() first.")
            return False
        
        commands = (self.escpos
                   .clear()
                   .init_printer()
                   .align_center()
                   .qr_code(data, size, error_correction)
                   .align_left()
                   .feed_lines(3)
                   .get_commands())
        
        return self.send_escpos_to_hardware(commands)
    
    def print_hardware_receipt(self, lines: List[str], cut_paper: bool = True) -> bool:
        """Print a formatted receipt to the selected hardware printer.
        
        Args:
            lines: List of text lines for the receipt
            cut_paper: Whether to cut paper after printing
            
        Returns:
            True if printing was successful, False otherwise
        """
        selected_printer = self.get_selected_printer()
        if not selected_printer:
            print("Error: No printer selected. Use select_printer() first.")
            return False
        
        # Build receipt commands
        cmd_builder = self.escpos.clear().init_printer()
        
        for line in lines:
            cmd_builder.line(line)
        
        cmd_builder.feed_lines(3)
        
        if cut_paper:
            cmd_builder.paper_cut()
        
        commands = cmd_builder.get_commands()
        return self.send_escpos_to_hardware(commands)
    
    def open_cash_drawer(self, drawer_number: int = 1) -> bool:
        """Open the cash drawer connected to the selected printer.
        
        Args:
            drawer_number: Drawer number (1 or 2)
            
        Returns:
            True if command was sent successfully, False otherwise
        """
        selected_printer = self.get_selected_printer()
        if not selected_printer:
            print("Error: No printer selected. Use select_printer() first.")
            return False
        
        commands = (self.escpos
                   .clear()
                   .open_drawer(drawer_number)
                   .get_commands())
        
        return self.send_escpos_to_hardware(commands)
    
    def print_test_page(self, use_hardware: bool = False) -> bool:
        """Print a test page.
        
        Args:
            use_hardware: If True, print to selected hardware printer
            
        Returns:
            True if printing was successful, False otherwise
        """
        if use_hardware:
            selected_printer = self.get_selected_printer()
            if not selected_printer:
                print("Error: No printer selected. Use select_printer() first.")
                return False
            
            return self.printer_interface.print_test_page(selected_printer.name)
        else:
            # Print to console
            self.print_banner("PyTextPrinter Test Page")
            print("This is a test page to verify functionality.", file=self.output)
            print(f"Console output is working correctly.", file=self.output)
            return True
    
    def get_printer_status(self, printer_name: Optional[str] = None) -> Optional[str]:
        """Get the status of a printer.
        
        Args:
            printer_name: Name of the printer (uses selected printer if None)
            
        Returns:
            Printer status string, or None if printer not found
        """
        return self.printer_manager.get_printer_status(printer_name)
    
    def is_hardware_printer_ready(self, printer_name: Optional[str] = None) -> bool:
        """Check if a hardware printer is ready.
        
        Args:
            printer_name: Name of the printer (uses selected printer if None)
            
        Returns:
            True if printer is ready, False otherwise
        """
        if printer_name is None:
            selected_printer = self.get_selected_printer()
            if not selected_printer:
                return False
            printer_name = selected_printer.name
        
        return self.printer_interface.is_printer_ready(printer_name)