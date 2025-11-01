"""Printer selection and management module for handling connected printers."""

from typing import List, Optional, Dict, Any
from .printer_discovery import PrinterDiscovery, PrinterInfo


class PrinterManager:
    """Manager class for selecting and managing printer connections."""
    
    def __init__(self):
        """Initialize the printer manager."""
        self.discovery = PrinterDiscovery()
        self._selected_printer: Optional[PrinterInfo] = None
        self._printer_cache: Dict[str, PrinterInfo] = {}
        self._refresh_cache()
    
    def _refresh_cache(self) -> None:
        """Refresh the internal printer cache."""
        try:
            printers = self.discovery.discover_all_printers()
            self._printer_cache = {printer.name: printer for printer in printers}
        except Exception:
            self._printer_cache = {}
    
    def list_all_printers(self, refresh: bool = False) -> List[PrinterInfo]:
        """List all available printers.
        
        Args:
            refresh: Whether to refresh the printer cache
            
        Returns:
            List of all available printers
        """
        if refresh or not self._printer_cache:
            self._refresh_cache()
        
        return list(self._printer_cache.values())
    
    def list_text_printers(self, refresh: bool = False) -> List[PrinterInfo]:
        """List only text/thermal printers.
        
        Args:
            refresh: Whether to refresh the printer cache
            
        Returns:
            List of text/thermal printers
        """
        if refresh or not self._printer_cache:
            self._refresh_cache()
        
        all_printers = list(self._printer_cache.values())
        return self.discovery._discovery.filter_text_printers(all_printers)
    
    def select_printer(self, printer_name: str) -> bool:
        """Select a printer for operations.
        
        Args:
            printer_name: Name of the printer to select
            
        Returns:
            True if printer was successfully selected, False otherwise
        """
        # Refresh cache to get latest printer status
        self._refresh_cache()
        
        if printer_name in self._printer_cache:
            printer_info = self._printer_cache[printer_name]
            
            # Verify printer is available
            if self.discovery.is_printer_available(printer_name):
                self._selected_printer = printer_info
                return True
            else:
                print(f"Warning: Printer '{printer_name}' is not available or has errors.")
                return False
        else:
            print(f"Error: Printer '{printer_name}' not found.")
            return False
    
    def select_default_printer(self) -> bool:
        """Select the system default printer.
        
        Returns:
            True if default printer was found and selected, False otherwise
        """
        self._refresh_cache()
        
        for printer in self._printer_cache.values():
            if printer.is_default:
                return self.select_printer(printer.name)
        
        print("No default printer found.")
        return False
    
    def auto_select_text_printer(self) -> bool:
        """Automatically select the first available text/thermal printer.
        
        Returns:
            True if a text printer was found and selected, False otherwise
        """
        text_printers = self.list_text_printers(refresh=True)
        
        for printer in text_printers:
            if self.discovery.is_printer_available(printer.name):
                self._selected_printer = printer
                return True
        
        print("No available text/thermal printers found.")
        return False
    
    def get_selected_printer(self) -> Optional[PrinterInfo]:
        """Get the currently selected printer.
        
        Returns:
            Currently selected printer info, or None if no printer is selected
        """
        return self._selected_printer
    
    def is_printer_selected(self) -> bool:
        """Check if a printer is currently selected.
        
        Returns:
            True if a printer is selected, False otherwise
        """
        return self._selected_printer is not None
    
    def get_printer_status(self, printer_name: Optional[str] = None) -> Optional[str]:
        """Get the status of a printer.
        
        Args:
            printer_name: Name of the printer (uses selected printer if None)
            
        Returns:
            Printer status string, or None if printer not found
        """
        if printer_name is None:
            if self._selected_printer:
                printer_name = self._selected_printer.name
            else:
                return None
        
        printer_info = self.discovery.get_printer_info(printer_name)
        return printer_info.status if printer_info else None
    
    def print_printer_list(self, text_only: bool = False) -> None:
        """Print a formatted list of available printers.
        
        Args:
            text_only: If True, only show text/thermal printers
        """
        printers = self.list_text_printers() if text_only else self.list_all_printers()
        
        if not printers:
            print("No printers found.")
            return
        
        print(f"\n{'Available Text Printers:' if text_only else 'Available Printers:'}")
        print("-" * 60)
        
        for i, printer in enumerate(printers, 1):
            status_indicator = "✓" if self.discovery.is_printer_available(printer.name) else "✗"
            default_indicator = " (Default)" if printer.is_default else ""
            selected_indicator = " [SELECTED]" if (self._selected_printer and 
                                                 self._selected_printer.name == printer.name) else ""
            
            print(f"{i:2d}. {status_indicator} {printer.name}{default_indicator}{selected_indicator}")
            print(f"     Driver: {printer.driver}")
            print(f"     Port: {printer.port}")
            print(f"     Status: {printer.status}")
            if printer.location:
                print(f"     Location: {printer.location}")
            print()
    
    def select_printer_interactive(self, text_only: bool = True) -> bool:
        """Interactively select a printer from a list.
        
        Args:
            text_only: If True, only show text/thermal printers
            
        Returns:
            True if a printer was selected, False otherwise
        """
        printers = self.list_text_printers() if text_only else self.list_all_printers()
        
        if not printers:
            print("No printers available for selection.")
            return False
        
        self.print_printer_list(text_only)
        
        try:
            choice = input(f"Select printer (1-{len(printers)}) or 'q' to quit: ").strip()
            
            if choice.lower() == 'q':
                return False
            
            index = int(choice) - 1
            if 0 <= index < len(printers):
                selected_printer = printers[index]
                if self.select_printer(selected_printer.name):
                    print(f"Selected printer: {selected_printer.name}")
                    return True
                else:
                    print(f"Failed to select printer: {selected_printer.name}")
                    return False
            else:
                print("Invalid selection.")
                return False
                
        except ValueError:
            print("Invalid input. Please enter a number.")
            return False
        except KeyboardInterrupt:
            print("\nSelection cancelled.")
            return False
    
    def get_printer_capabilities(self, printer_name: Optional[str] = None) -> Dict[str, Any]:
        """Get printer capabilities and features.
        
        Args:
            printer_name: Name of the printer (uses selected printer if None)
            
        Returns:
            Dictionary with printer capabilities
        """
        if printer_name is None:
            if self._selected_printer:
                printer_name = self._selected_printer.name
            else:
                return {}
        
        printer_info = self.discovery.get_printer_info(printer_name)
        if not printer_info:
            return {}
        
        capabilities = {
            'name': printer_info.name,
            'driver': printer_info.driver,
            'port': printer_info.port,
            'status': printer_info.status,
            'is_default': printer_info.is_default,
            'is_shared': printer_info.is_shared,
            'location': printer_info.location,
            'comment': printer_info.comment,
            'supports_graphics': self._supports_graphics(printer_info),
            'is_thermal': self._is_thermal_printer(printer_info),
            'platform_specific': printer_info.platform_specific
        }
        
        return capabilities
    
    def _supports_graphics(self, printer_info: PrinterInfo) -> bool:
        """Determine if printer supports graphics."""
        # Most modern printers support some form of graphics
        # Thermal and dot matrix printers typically have limited graphics support
        thermal_keywords = ['thermal', 'receipt', 'pos', 'dot matrix']
        printer_text = (printer_info.name + " " + printer_info.driver + " " + 
                       printer_info.comment).lower()
        
        # If it's a thermal printer, assume limited graphics support
        if any(keyword in printer_text for keyword in thermal_keywords):
            return True  # ESC/POS printers typically support basic graphics
        
        # For other printers, assume full graphics support
        return True
    
    def _is_thermal_printer(self, printer_info: PrinterInfo) -> bool:
        """Determine if printer is a thermal/receipt printer."""
        thermal_keywords = ['thermal', 'receipt', 'pos', 'escpos']
        printer_text = (printer_info.name + " " + printer_info.driver + " " + 
                       printer_info.comment).lower()
        return any(keyword in printer_text for keyword in thermal_keywords)