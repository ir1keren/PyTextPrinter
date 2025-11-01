"""Platform-specific printer interfaces for sending raw data to printers."""

import platform
import subprocess
import tempfile
import os
from typing import Optional, Union, Dict, Any
from abc import ABC, abstractmethod
from .printer_discovery import PrinterInfo


class PrinterInterfaceBase(ABC):
    """Abstract base class for platform-specific printer interfaces."""
    
    @abstractmethod
    def send_raw_data(self, printer_name: str, data: bytes) -> bool:
        """Send raw data to the specified printer.
        
        Args:
            printer_name: Name of the printer
            data: Raw data to send
            
        Returns:
            True if data was sent successfully, False otherwise
        """
        pass
    
    @abstractmethod
    def send_text(self, printer_name: str, text: str, encoding: str = 'cp437') -> bool:
        """Send text to the specified printer.
        
        Args:
            printer_name: Name of the printer
            text: Text to send
            encoding: Character encoding to use
            
        Returns:
            True if text was sent successfully, False otherwise
        """
        pass
    
    @abstractmethod
    def is_printer_ready(self, printer_name: str) -> bool:
        """Check if the printer is ready to receive data.
        
        Args:
            printer_name: Name of the printer
            
        Returns:
            True if printer is ready, False otherwise
        """
        pass


class WindowsPrinterInterface(PrinterInterfaceBase):
    """Windows-specific printer interface using raw printing APIs."""
    
    def __init__(self):
        """Initialize Windows printer interface."""
        self._win32print = None
        try:
            import win32print
            import win32api
            self._win32print = win32print
            self._win32api = win32api
        except ImportError:
            # Fallback to command-line methods
            pass
    
    def send_raw_data(self, printer_name: str, data: bytes) -> bool:
        """Send raw data to Windows printer."""
        if self._win32print:
            return self._send_raw_data_win32(printer_name, data)
        else:
            return self._send_raw_data_fallback(printer_name, data)
    
    def _send_raw_data_win32(self, printer_name: str, data: bytes) -> bool:
        """Send raw data using win32print APIs."""
        try:
            # Open printer
            printer_handle = self._win32print.OpenPrinter(printer_name)
            
            # Start document
            job_info = ("PyTextPrinter Raw Job", None, "RAW")
            job_id = self._win32print.StartDocPrinter(printer_handle, 1, job_info)
            
            # Start page
            self._win32print.StartPagePrinter(printer_handle)
            
            # Write data
            self._win32print.WritePrinter(printer_handle, data)
            
            # End page and document
            self._win32print.EndPagePrinter(printer_handle)
            self._win32print.EndDocPrinter(printer_handle)
            
            # Close printer
            self._win32print.ClosePrinter(printer_handle)
            
            return True
            
        except Exception as e:
            print(f"Error sending raw data to {printer_name}: {e}")
            return False
    
    def _send_raw_data_fallback(self, printer_name: str, data: bytes) -> bool:
        """Send raw data using command-line fallback."""
        try:
            # Create temporary file
            with tempfile.NamedTemporaryFile(delete=False) as temp_file:
                temp_file.write(data)
                temp_filename = temp_file.name
            
            try:
                # Use copy command to send to printer
                result = subprocess.run([
                    'copy', '/B', temp_filename, f'\\\\localhost\\{printer_name}'
                ], shell=True, capture_output=True, text=True)
                
                return result.returncode == 0
                
            finally:
                # Clean up temporary file
                os.unlink(temp_filename)
                
        except Exception as e:
            print(f"Error sending raw data to {printer_name}: {e}")
            return False
    
    def send_text(self, printer_name: str, text: str, encoding: str = 'cp437') -> bool:
        """Send text to Windows printer."""
        try:
            data = text.encode(encoding)
            return self.send_raw_data(printer_name, data)
        except UnicodeEncodeError:
            # Fallback to UTF-8 with error replacement
            data = text.encode('utf-8', errors='replace')
            return self.send_raw_data(printer_name, data)
    
    def is_printer_ready(self, printer_name: str) -> bool:
        """Check if Windows printer is ready."""
        if self._win32print:
            try:
                printer_handle = self._win32print.OpenPrinter(printer_name)
                printer_info = self._win32print.GetPrinter(printer_handle, 2)
                self._win32print.ClosePrinter(printer_handle)
                
                # Check printer status
                status = printer_info.get('Status', 0)
                # Status 0 typically means ready
                return status == 0
                
            except Exception:
                return False
        else:
            # Fallback: assume printer is ready if it exists
            try:
                result = subprocess.run([
                    'wmic', 'printer', 'where', f'Name="{printer_name}"', 'get', 'PrinterStatus'
                ], capture_output=True, text=True, shell=True)
                
                return result.returncode == 0 and 'PrinterStatus' in result.stdout
            except Exception:
                return False


class LinuxPrinterInterface(PrinterInterfaceBase):
    """Linux-specific printer interface using CUPS and lp commands."""
    
    def send_raw_data(self, printer_name: str, data: bytes) -> bool:
        """Send raw data to Linux printer using lp command."""
        try:
            # Create temporary file
            with tempfile.NamedTemporaryFile(delete=False) as temp_file:
                temp_file.write(data)
                temp_filename = temp_file.name
            
            try:
                # Use lp command to send raw data
                result = subprocess.run([
                    'lp', '-d', printer_name, '-o', 'raw', temp_filename
                ], capture_output=True, text=True)
                
                return result.returncode == 0
                
            finally:
                # Clean up temporary file
                os.unlink(temp_filename)
                
        except Exception as e:
            print(f"Error sending raw data to {printer_name}: {e}")
            return False
    
    def send_text(self, printer_name: str, text: str, encoding: str = 'cp437') -> bool:
        """Send text to Linux printer."""
        try:
            # For text, we can send directly through lp
            result = subprocess.run([
                'lp', '-d', printer_name, '-o', 'raw'
            ], input=text, text=True, capture_output=True, encoding=encoding)
            
            return result.returncode == 0
            
        except Exception as e:
            print(f"Error sending text to {printer_name}: {e}")
            # Fallback to raw data method
            try:
                data = text.encode(encoding)
                return self.send_raw_data(printer_name, data)
            except UnicodeEncodeError:
                data = text.encode('utf-8', errors='replace')
                return self.send_raw_data(printer_name, data)
    
    def is_printer_ready(self, printer_name: str) -> bool:
        """Check if Linux printer is ready using lpstat."""
        try:
            result = subprocess.run([
                'lpstat', '-p', printer_name
            ], capture_output=True, text=True)
            
            if result.returncode == 0:
                # Check if printer is idle or printing (not disabled)
                return 'disabled' not in result.stdout.lower()
            
            return False
            
        except Exception:
            return False


class MacOSPrinterInterface(PrinterInterfaceBase):
    """macOS-specific printer interface using CUPS and lp commands."""
    
    def send_raw_data(self, printer_name: str, data: bytes) -> bool:
        """Send raw data to macOS printer using lp command."""
        try:
            # Create temporary file
            with tempfile.NamedTemporaryFile(delete=False) as temp_file:
                temp_file.write(data)
                temp_filename = temp_file.name
            
            try:
                # Use lp command to send raw data
                result = subprocess.run([
                    'lp', '-d', printer_name, '-o', 'raw', temp_filename
                ], capture_output=True, text=True)
                
                return result.returncode == 0
                
            finally:
                # Clean up temporary file
                os.unlink(temp_filename)
                
        except Exception as e:
            print(f"Error sending raw data to {printer_name}: {e}")
            return False
    
    def send_text(self, printer_name: str, text: str, encoding: str = 'cp437') -> bool:
        """Send text to macOS printer."""
        try:
            # For text, we can send directly through lp
            result = subprocess.run([
                'lp', '-d', printer_name, '-o', 'raw'
            ], input=text, text=True, capture_output=True, encoding=encoding)
            
            return result.returncode == 0
            
        except Exception as e:
            print(f"Error sending text to {printer_name}: {e}")
            # Fallback to raw data method
            try:
                data = text.encode(encoding)
                return self.send_raw_data(printer_name, data)
            except UnicodeEncodeError:
                data = text.encode('utf-8', errors='replace')
                return self.send_raw_data(printer_name, data)
    
    def is_printer_ready(self, printer_name: str) -> bool:
        """Check if macOS printer is ready using lpstat."""
        try:
            result = subprocess.run([
                'lpstat', '-p', printer_name
            ], capture_output=True, text=True)
            
            if result.returncode == 0:
                # Check if printer is idle or printing (not disabled)
                return 'disabled' not in result.stdout.lower()
            
            return False
            
        except Exception:
            return False


class PrinterInterface:
    """Main printer interface that handles all platforms."""
    
    def __init__(self):
        """Initialize with platform-specific interface."""
        system = platform.system().lower()
        
        if system == 'windows':
            self._interface = WindowsPrinterInterface()
        elif system == 'linux':
            self._interface = LinuxPrinterInterface()
        elif system == 'darwin':  # macOS
            self._interface = MacOSPrinterInterface()
        else:
            raise NotImplementedError(f"Platform {system} is not supported")
    
    def send_raw_data(self, printer_name: str, data: bytes) -> bool:
        """Send raw data to the specified printer.
        
        Args:
            printer_name: Name of the printer
            data: Raw data to send
            
        Returns:
            True if data was sent successfully, False otherwise
        """
        return self._interface.send_raw_data(printer_name, data)
    
    def send_text(self, printer_name: str, text: str, encoding: str = 'cp437') -> bool:
        """Send text to the specified printer.
        
        Args:
            printer_name: Name of the printer
            text: Text to send
            encoding: Character encoding to use
            
        Returns:
            True if text was sent successfully, False otherwise
        """
        return self._interface.send_text(printer_name, text, encoding)
    
    def send_escpos_commands(self, printer_name: str, commands: bytes) -> bool:
        """Send ESC/POS commands to the specified printer.
        
        Args:
            printer_name: Name of the printer
            commands: ESC/POS command sequence
            
        Returns:
            True if commands were sent successfully, False otherwise
        """
        return self.send_raw_data(printer_name, commands)
    
    def is_printer_ready(self, printer_name: str) -> bool:
        """Check if the printer is ready to receive data.
        
        Args:
            printer_name: Name of the printer
            
        Returns:
            True if printer is ready, False otherwise
        """
        return self._interface.is_printer_ready(printer_name)
    
    def print_test_page(self, printer_name: str) -> bool:
        """Print a test page to verify printer functionality.
        
        Args:
            printer_name: Name of the printer
            
        Returns:
            True if test page was sent successfully, False otherwise
        """
        test_content = (
            "PyTextPrinter Test Page\n"
            "======================\n\n"
            "This is a test page to verify printer functionality.\n"
            "If you can read this, the printer is working correctly.\n\n"
            f"Printer: {printer_name}\n"
            f"Platform: {platform.system()}\n\n"
            "Test completed successfully.\n"
            "\n\n\n"  # Feed some lines for cutting
        )
        
        return self.send_text(printer_name, test_content)