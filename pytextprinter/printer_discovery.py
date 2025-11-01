"""Printer discovery module for finding connected text/thermal printers across platforms."""

import platform
import subprocess
import re
from typing import List, Dict, Optional, Any
from dataclasses import dataclass
from abc import ABC, abstractmethod


@dataclass
class PrinterInfo:
    """Information about a discovered printer."""
    name: str
    driver: str
    port: str
    status: str
    is_default: bool = False
    is_shared: bool = False
    location: str = ""
    comment: str = ""
    platform_specific: Dict[str, Any] = None
    
    def __post_init__(self):
        if self.platform_specific is None:
            self.platform_specific = {}


class PrinterDiscoveryBase(ABC):
    """Abstract base class for platform-specific printer discovery."""
    
    @abstractmethod
    def discover_printers(self) -> List[PrinterInfo]:
        """Discover all available printers on the platform.
        
        Returns:
            List of PrinterInfo objects representing discovered printers
        """
        pass
    
    @abstractmethod
    def get_printer_details(self, printer_name: str) -> Optional[PrinterInfo]:
        """Get detailed information about a specific printer.
        
        Args:
            printer_name: Name of the printer to query
            
        Returns:
            PrinterInfo object with detailed information, or None if not found
        """
        pass
    
    def filter_text_printers(self, printers: List[PrinterInfo]) -> List[PrinterInfo]:
        """Filter printers to only include text/thermal printers.
        
        Args:
            printers: List of all discovered printers
            
        Returns:
            Filtered list containing only text/thermal printers
        """
        text_printer_keywords = [
            'thermal', 'receipt', 'pos', 'text', 'dot matrix',
            'impact', 'epson', 'star', 'citizen', 'zebra',
            'bixolon', 'rongta', 'xprinter', 'escpos'
        ]
        
        filtered = []
        for printer in printers:
            printer_info_lower = (printer.name + " " + printer.driver + " " + 
                                printer.comment).lower()
            
            if any(keyword in printer_info_lower for keyword in text_printer_keywords):
                filtered.append(printer)
            # Also include printers connected via USB or Serial (common for thermal printers)
            elif any(port_type in printer.port.lower() for port_type in ['usb', 'com', 'serial']):
                filtered.append(printer)
                
        return filtered


class WindowsPrinterDiscovery(PrinterDiscoveryBase):
    """Windows-specific printer discovery using WMI and system commands."""
    
    def discover_printers(self) -> List[PrinterInfo]:
        """Discover printers using Windows WMI and wmic commands."""
        printers = []
        
        try:
            # Use wmic to get printer information
            result = subprocess.run([
                'wmic', 'printer', 'get', 
                'Name,DriverName,PortName,PrinterStatus,Default,Shared,Location,Comment',
                '/format:csv'
            ], capture_output=True, text=True, shell=True)
            
            if result.returncode == 0:
                lines = result.stdout.strip().split('\n')[1:]  # Skip header
                for line in lines:
                    if line.strip():
                        parts = line.split(',')
                        if len(parts) >= 7:
                            printers.append(PrinterInfo(
                                name=parts[5] or "Unknown",
                                driver=parts[2] or "Unknown",
                                port=parts[6] or "Unknown",
                                status=self._parse_status(parts[7]),
                                is_default=parts[1].lower() == 'true' if parts[1] else False,
                                is_shared=parts[8].lower() == 'true' if len(parts) > 8 and parts[8] else False,
                                location=parts[4] if len(parts) > 4 else "",
                                comment=parts[0] if parts[0] else "",
                                platform_specific={'wmi_data': line}
                            ))
        except Exception as e:
            # Fallback to simpler method
            try:
                result = subprocess.run(['wmic', 'printer', 'get', 'Name'], 
                                      capture_output=True, text=True, shell=True)
                if result.returncode == 0:
                    for line in result.stdout.strip().split('\n')[1:]:
                        if line.strip():
                            printers.append(PrinterInfo(
                                name=line.strip(),
                                driver="Unknown",
                                port="Unknown",
                                status="Unknown"
                            ))
            except Exception:
                pass
        
        return printers
    
    def get_printer_details(self, printer_name: str) -> Optional[PrinterInfo]:
        """Get detailed information about a specific Windows printer."""
        try:
            result = subprocess.run([
                'wmic', 'printer', 'where', f'Name="{printer_name}"', 'get', '*', '/format:list'
            ], capture_output=True, text=True, shell=True)
            
            if result.returncode == 0:
                details = {}
                for line in result.stdout.split('\n'):
                    if '=' in line:
                        key, value = line.split('=', 1)
                        details[key.strip()] = value.strip()
                
                return PrinterInfo(
                    name=details.get('Name', printer_name),
                    driver=details.get('DriverName', 'Unknown'),
                    port=details.get('PortName', 'Unknown'),
                    status=self._parse_status(details.get('PrinterStatus', '0')),
                    is_default=details.get('Default', '').lower() == 'true',
                    is_shared=details.get('Shared', '').lower() == 'true',
                    location=details.get('Location', ''),
                    comment=details.get('Comment', ''),
                    platform_specific=details
                )
        except Exception:
            pass
        
        return None
    
    def _parse_status(self, status_code: str) -> str:
        """Parse Windows printer status code to human-readable string."""
        status_map = {
            '0': 'Unknown',
            '1': 'Other',
            '2': 'No Error',
            '3': 'Degraded',
            '4': 'Predicted Failure',
            '5': 'Error',
            '6': 'Non-Recoverable Error',
            '7': 'Starting',
            '8': 'Stopping',
            '9': 'Stopped',
            '10': 'In Service',
            '11': 'No Contact',
            '12': 'Lost Communication'
        }
        return status_map.get(str(status_code), 'Unknown')


class LinuxPrinterDiscovery(PrinterDiscoveryBase):
    """Linux-specific printer discovery using CUPS and lpstat."""
    
    def discover_printers(self) -> List[PrinterInfo]:
        """Discover printers using CUPS lpstat command."""
        printers = []
        
        try:
            # Get printer list with details
            result = subprocess.run(['lpstat', '-p', '-d'], capture_output=True, text=True)
            
            if result.returncode == 0:
                default_printer = ""
                # Parse default printer
                for line in result.stdout.split('\n'):
                    if line.startswith('system default destination:'):
                        default_printer = line.split(':')[-1].strip()
                        break
                
                # Parse printer information
                for line in result.stdout.split('\n'):
                    if line.startswith('printer '):
                        match = re.match(r'printer (\S+) (.+)', line)
                        if match:
                            name = match.group(1)
                            status = match.group(2)
                            
                            # Get additional details
                            details = self._get_cups_printer_details(name)
                            
                            printers.append(PrinterInfo(
                                name=name,
                                driver=details.get('driver', 'Unknown'),
                                port=details.get('device-uri', 'Unknown'),
                                status=status,
                                is_default=name == default_printer,
                                location=details.get('printer-location', ''),
                                comment=details.get('printer-info', ''),
                                platform_specific=details
                            ))
        except Exception:
            # Fallback to simple lpstat
            try:
                result = subprocess.run(['lpstat', '-a'], capture_output=True, text=True)
                if result.returncode == 0:
                    for line in result.stdout.split('\n'):
                        if line.strip():
                            name = line.split()[0]
                            printers.append(PrinterInfo(
                                name=name,
                                driver="Unknown",
                                port="Unknown",
                                status="Unknown"
                            ))
            except Exception:
                pass
        
        return printers
    
    def get_printer_details(self, printer_name: str) -> Optional[PrinterInfo]:
        """Get detailed information about a specific Linux printer."""
        details = self._get_cups_printer_details(printer_name)
        if details:
            return PrinterInfo(
                name=printer_name,
                driver=details.get('driver', 'Unknown'),
                port=details.get('device-uri', 'Unknown'),
                status=details.get('printer-state-message', 'Unknown'),
                location=details.get('printer-location', ''),
                comment=details.get('printer-info', ''),
                platform_specific=details
            )
        return None
    
    def _get_cups_printer_details(self, printer_name: str) -> Dict[str, str]:
        """Get detailed printer information from CUPS."""
        details = {}
        try:
            result = subprocess.run(['lpoptions', '-p', printer_name, '-l'], 
                                  capture_output=True, text=True)
            if result.returncode == 0:
                for line in result.stdout.split('\n'):
                    if ':' in line:
                        key, value = line.split(':', 1)
                        details[key.strip()] = value.strip()
        except Exception:
            pass
        
        return details


class MacOSPrinterDiscovery(PrinterDiscoveryBase):
    """macOS-specific printer discovery using system_profiler and lpstat."""
    
    def discover_printers(self) -> List[PrinterInfo]:
        """Discover printers using macOS system tools."""
        printers = []
        
        try:
            # Use lpstat first (similar to Linux)
            result = subprocess.run(['lpstat', '-p', '-d'], capture_output=True, text=True)
            
            if result.returncode == 0:
                default_printer = ""
                for line in result.stdout.split('\n'):
                    if 'default destination:' in line:
                        default_printer = line.split(':')[-1].strip()
                        break
                
                for line in result.stdout.split('\n'):
                    if line.startswith('printer '):
                        match = re.match(r'printer (\S+) (.+)', line)
                        if match:
                            name = match.group(1)
                            status = match.group(2)
                            
                            printers.append(PrinterInfo(
                                name=name,
                                driver="Unknown",
                                port="Unknown",
                                status=status,
                                is_default=name == default_printer
                            ))
            
            # Get additional details using system_profiler
            try:
                result = subprocess.run(['system_profiler', 'SPPrintersDataType'], 
                                      capture_output=True, text=True)
                if result.returncode == 0:
                    # Parse system_profiler output to enhance printer information
                    current_printer = None
                    for line in result.stdout.split('\n'):
                        line = line.strip()
                        if line.endswith(':') and not line.startswith(' '):
                            current_printer = line[:-1]
                        elif current_printer and line.startswith('Location:'):
                            location = line.replace('Location:', '').strip()
                            # Find and update the corresponding printer
                            for printer in printers:
                                if printer.name == current_printer:
                                    printer.location = location
                                    break
            except Exception:
                pass
                
        except Exception:
            pass
        
        return printers
    
    def get_printer_details(self, printer_name: str) -> Optional[PrinterInfo]:
        """Get detailed information about a specific macOS printer."""
        # Implementation similar to Linux but with macOS-specific commands
        try:
            result = subprocess.run(['lpoptions', '-p', printer_name], 
                                  capture_output=True, text=True)
            if result.returncode == 0:
                return PrinterInfo(
                    name=printer_name,
                    driver="Unknown",
                    port="Unknown",
                    status="Available",
                    platform_specific={'lpoptions': result.stdout}
                )
        except Exception:
            pass
        
        return None


class PrinterDiscovery:
    """Main printer discovery class that handles all platforms."""
    
    def __init__(self):
        """Initialize with platform-specific discovery implementation."""
        system = platform.system().lower()
        
        if system == 'windows':
            self._discovery = WindowsPrinterDiscovery()
        elif system == 'linux':
            self._discovery = LinuxPrinterDiscovery()
        elif system == 'darwin':  # macOS
            self._discovery = MacOSPrinterDiscovery()
        else:
            raise NotImplementedError(f"Platform {system} is not supported")
    
    def discover_all_printers(self) -> List[PrinterInfo]:
        """Discover all available printers on the current platform.
        
        Returns:
            List of all discovered printers
        """
        return self._discovery.discover_printers()
    
    def discover_text_printers(self) -> List[PrinterInfo]:
        """Discover only text/thermal printers.
        
        Returns:
            Filtered list of text/thermal printers
        """
        all_printers = self.discover_all_printers()
        return self._discovery.filter_text_printers(all_printers)
    
    def get_printer_info(self, printer_name: str) -> Optional[PrinterInfo]:
        """Get detailed information about a specific printer.
        
        Args:
            printer_name: Name of the printer to query
            
        Returns:
            PrinterInfo object with detailed information, or None if not found
        """
        return self._discovery.get_printer_details(printer_name)
    
    def is_printer_available(self, printer_name: str) -> bool:
        """Check if a printer is available and responsive.
        
        Args:
            printer_name: Name of the printer to check
            
        Returns:
            True if printer is available, False otherwise
        """
        printer_info = self.get_printer_info(printer_name)
        if printer_info:
            # Consider printer available if status doesn't indicate error
            error_statuses = ['error', 'stopped', 'offline', 'no contact', 'lost communication']
            return not any(status in printer_info.status.lower() for status in error_statuses)
        return False
