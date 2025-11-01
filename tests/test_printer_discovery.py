"""Test cases for printer discovery functionality."""

import pytest
from unittest.mock import Mock, patch, MagicMock
from pytextprinter.printer_discovery import (
    PrinterInfo, PrinterDiscovery, WindowsPrinterDiscovery,
    LinuxPrinterDiscovery, MacOSPrinterDiscovery
)


class TestPrinterInfo:
    """Test cases for PrinterInfo data class."""
    
    def test_printer_info_creation(self):
        """Test creating PrinterInfo objects."""
        printer = PrinterInfo(
            name="Test Printer",
            driver="Test Driver",
            port="USB001",
            status="Ready"
        )
        
        assert printer.name == "Test Printer"
        assert printer.driver == "Test Driver"
        assert printer.port == "USB001"
        assert printer.status == "Ready"
        assert printer.is_default == False
        assert printer.platform_specific == {}
    
    def test_printer_info_with_defaults(self):
        """Test PrinterInfo with default values."""
        printer = PrinterInfo(
            name="Test",
            driver="Driver",
            port="PORT",
            status="Ready",
            is_default=True,
            location="Office"
        )
        
        assert printer.is_default == True
        assert printer.location == "Office"


class TestPrinterDiscoveryBase:
    """Test cases for printer discovery base functionality."""
    
    def test_filter_text_printers(self):
        """Test filtering for text/thermal printers."""
        discovery = WindowsPrinterDiscovery()
        
        printers = [
            PrinterInfo("HP LaserJet", "HP Driver", "USB", "Ready"),
            PrinterInfo("Epson TM-T88V", "Epson Thermal", "USB", "Ready"),
            PrinterInfo("Canon Inkjet", "Canon Driver", "USB", "Ready"),
            PrinterInfo("Star TSP100", "Star Receipt", "USB", "Ready"),
            PrinterInfo("Generic USB Printer", "Generic", "USB001", "Ready"),
        ]
        
        filtered = discovery.filter_text_printers(printers)
        
        # Should include thermal printers and USB-connected printers
        assert len(filtered) >= 3  # At least Epson, Star, and Generic USB
        printer_names = [p.name for p in filtered]
        assert "Epson TM-T88V" in printer_names
        assert "Star TSP100" in printer_names


@patch('subprocess.run')
class TestWindowsPrinterDiscovery:
    """Test cases for Windows printer discovery."""
    
    def test_discover_printers_success(self, mock_run):
        """Test successful printer discovery on Windows."""
        # Mock wmic output
        mock_output = """Node,Comment,Default,DriverName,Location,Name,PortName,PrinterStatus,Shared
COMPUTER,,FALSE,HP LaserJet Driver,,HP LaserJet,USB001,2,FALSE
COMPUTER,,TRUE,Epson TM Driver,,Epson TM-T88V,USB002,2,FALSE
"""
        mock_run.return_value = Mock(returncode=0, stdout=mock_output)
        
        discovery = WindowsPrinterDiscovery()
        printers = discovery.discover_printers()
        
        assert len(printers) == 2
        assert printers[0].name == "HP LaserJet"
        assert printers[1].name == "Epson TM-T88V"
        assert printers[1].is_default == True
    
    def test_discover_printers_fallback(self, mock_run):
        """Test fallback method when wmic fails."""
        # First call fails, second succeeds with simple output
        mock_run.side_effect = [
            Mock(returncode=1, stdout=""),
            Mock(returncode=0, stdout="Name\nHP LaserJet\nEpson TM-T88V\n")
        ]
        
        discovery = WindowsPrinterDiscovery()
        printers = discovery.discover_printers()
        
        assert len(printers) == 2
        assert printers[0].name == "HP LaserJet"
        assert printers[1].name == "Epson TM-T88V"


@patch('subprocess.run')
class TestLinuxPrinterDiscovery:
    """Test cases for Linux printer discovery."""
    
    def test_discover_printers_success(self, mock_run):
        """Test successful printer discovery on Linux."""
        mock_output = """printer HP_LaserJet is idle.  enabled since Mon 01 Jan 2024 12:00:00 PM EST
printer Epson_TM is idle.  enabled since Mon 01 Jan 2024 12:00:00 PM EST
system default destination: Epson_TM
"""
        mock_run.return_value = Mock(returncode=0, stdout=mock_output)
        
        discovery = LinuxPrinterDiscovery()
        printers = discovery.discover_printers()
        
        assert len(printers) == 2
        printer_names = [p.name for p in printers]
        assert "HP_LaserJet" in printer_names
        assert "Epson_TM" in printer_names
        
        # Check default printer
        default_printers = [p for p in printers if p.is_default]
        assert len(default_printers) == 1
        assert default_printers[0].name == "Epson_TM"


@patch('subprocess.run')
class TestMacOSPrinterDiscovery:
    """Test cases for macOS printer discovery."""
    
    def test_discover_printers_success(self, mock_run):
        """Test successful printer discovery on macOS."""
        mock_output = """printer HP_LaserJet is idle.  enabled since Mon 01 Jan 2024 12:00:00 PM EST
printer Epson_TM is idle.  enabled since Mon 01 Jan 2024 12:00:00 PM EST
default destination: Epson_TM
"""
        mock_run.return_value = Mock(returncode=0, stdout=mock_output)
        
        discovery = MacOSPrinterDiscovery()
        printers = discovery.discover_printers()
        
        assert len(printers) == 2
        printer_names = [p.name for p in printers]
        assert "HP_LaserJet" in printer_names
        assert "Epson_TM" in printer_names


@patch('platform.system')
class TestPrinterDiscovery:
    """Test cases for main PrinterDiscovery class."""
    
    def test_windows_initialization(self, mock_system):
        """Test initialization on Windows."""
        mock_system.return_value = 'Windows'
        
        discovery = PrinterDiscovery()
        assert isinstance(discovery._discovery, WindowsPrinterDiscovery)
    
    def test_linux_initialization(self, mock_system):
        """Test initialization on Linux."""
        mock_system.return_value = 'Linux'
        
        discovery = PrinterDiscovery()
        assert isinstance(discovery._discovery, LinuxPrinterDiscovery)
    
    def test_macos_initialization(self, mock_system):
        """Test initialization on macOS."""
        mock_system.return_value = 'Darwin'
        
        discovery = PrinterDiscovery()
        assert isinstance(discovery._discovery, MacOSPrinterDiscovery)
    
    def test_unsupported_platform(self, mock_system):
        """Test unsupported platform raises exception."""
        mock_system.return_value = 'FreeBSD'
        
        with pytest.raises(NotImplementedError):
            PrinterDiscovery()
    
    @patch('pytextprinter.printer_discovery.WindowsPrinterDiscovery.discover_printers')
    def test_discover_all_printers(self, mock_discover, mock_system):
        """Test discovering all printers."""
        mock_system.return_value = 'Windows'
        mock_printers = [
            PrinterInfo("Printer1", "Driver1", "USB", "Ready"),
            PrinterInfo("Printer2", "Driver2", "USB", "Ready"),
        ]
        mock_discover.return_value = mock_printers
        
        discovery = PrinterDiscovery()
        printers = discovery.discover_all_printers()
        
        assert len(printers) == 2
        assert printers == mock_printers
    
    @patch('pytextprinter.printer_discovery.WindowsPrinterDiscovery.filter_text_printers')
    @patch('pytextprinter.printer_discovery.WindowsPrinterDiscovery.discover_printers')
    def test_discover_text_printers(self, mock_discover, mock_filter, mock_system):
        """Test discovering text printers."""
        mock_system.return_value = 'Windows'
        mock_all_printers = [
            PrinterInfo("LaserJet", "HP", "USB", "Ready"),
            PrinterInfo("TM-T88V", "Epson", "USB", "Ready"),
        ]
        mock_text_printers = [
            PrinterInfo("TM-T88V", "Epson", "USB", "Ready"),
        ]
        
        mock_discover.return_value = mock_all_printers
        mock_filter.return_value = mock_text_printers
        
        discovery = PrinterDiscovery()
        printers = discovery.discover_text_printers()
        
        assert len(printers) == 1
        assert printers[0].name == "TM-T88V"