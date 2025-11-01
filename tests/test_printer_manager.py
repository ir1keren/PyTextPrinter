"""Test cases for printer manager functionality."""

import pytest
from unittest.mock import Mock, patch, MagicMock
from pytextprinter.printer_manager import PrinterManager
from pytextprinter.printer_discovery import PrinterInfo


class TestPrinterManager:
    """Test cases for PrinterManager functionality."""
    
    def setup_method(self):
        """Set up test fixtures."""
        self.manager = PrinterManager()
        
        # Mock printers for testing
        self.mock_printers = [
            PrinterInfo("HP LaserJet", "HP Driver", "USB001", "Ready", is_default=True),
            PrinterInfo("Epson TM-T88V", "Epson Thermal", "USB002", "Ready"),
            PrinterInfo("Canon Inkjet", "Canon Driver", "USB003", "Ready"),
            PrinterInfo("Star TSP100", "Star Receipt", "USB004", "Ready"),
        ]
    
    @patch('pytextprinter.printer_manager.PrinterDiscovery')
    def test_initialization(self, mock_discovery_class):
        """Test PrinterManager initialization."""
        mock_discovery = Mock()
        mock_discovery_class.return_value = mock_discovery
        mock_discovery.discover_all_printers.return_value = self.mock_printers
        
        manager = PrinterManager()
        
        assert manager.discovery == mock_discovery
        assert manager._selected_printer is None
        mock_discovery.discover_all_printers.assert_called_once()
    
    @patch.object(PrinterManager, '_refresh_cache')
    def test_list_all_printers(self, mock_refresh):
        """Test listing all printers."""
        self.manager._printer_cache = {p.name: p for p in self.mock_printers}
        
        printers = self.manager.list_all_printers(refresh=False)
        
        assert len(printers) == 4
        mock_refresh.assert_not_called()
        
        # Test with refresh
        self.manager.list_all_printers(refresh=True)
        mock_refresh.assert_called_once()
    
    @patch.object(PrinterManager, '_refresh_cache')
    def test_list_text_printers(self, mock_refresh):
        """Test listing text printers only."""
        self.manager._printer_cache = {p.name: p for p in self.mock_printers}
        
        # Mock the filter method
        with patch.object(self.manager.discovery._discovery, 'filter_text_printers') as mock_filter:
            mock_filter.return_value = [self.mock_printers[1], self.mock_printers[3]]  # Thermal printers
            
            printers = self.manager.list_text_printers()
            
            assert len(printers) == 2
            assert "Epson TM-T88V" in [p.name for p in printers]
            assert "Star TSP100" in [p.name for p in printers]
    
    @patch.object(PrinterManager, '_refresh_cache')
    @patch('pytextprinter.printer_manager.PrinterDiscovery')
    def test_select_printer_success(self, mock_discovery_class, mock_refresh):
        """Test successful printer selection."""
        mock_discovery = Mock()
        mock_discovery_class.return_value = mock_discovery
        mock_discovery.is_printer_available.return_value = True
        
        self.manager._printer_cache = {p.name: p for p in self.mock_printers}
        
        result = self.manager.select_printer("Epson TM-T88V")
        
        assert result == True
        assert self.manager._selected_printer.name == "Epson TM-T88V"
        mock_discovery.is_printer_available.assert_called_with("Epson TM-T88V")
    
    @patch.object(PrinterManager, '_refresh_cache')
    @patch('pytextprinter.printer_manager.PrinterDiscovery')
    def test_select_printer_not_available(self, mock_discovery_class, mock_refresh):
        """Test selecting unavailable printer."""
        mock_discovery = Mock()
        mock_discovery_class.return_value = mock_discovery
        mock_discovery.is_printer_available.return_value = False
        
        self.manager._printer_cache = {p.name: p for p in self.mock_printers}
        
        result = self.manager.select_printer("Epson TM-T88V")
        
        assert result == False
        assert self.manager._selected_printer is None
    
    @patch.object(PrinterManager, '_refresh_cache')
    def test_select_printer_not_found(self, mock_refresh):
        """Test selecting non-existent printer."""
        self.manager._printer_cache = {p.name: p for p in self.mock_printers}
        
        result = self.manager.select_printer("Non-existent Printer")
        
        assert result == False
        assert self.manager._selected_printer is None
    
    @patch.object(PrinterManager, '_refresh_cache')
    @patch('pytextprinter.printer_manager.PrinterDiscovery')
    def test_select_default_printer(self, mock_discovery_class, mock_refresh):
        """Test selecting default printer."""
        mock_discovery = Mock()
        mock_discovery_class.return_value = mock_discovery
        mock_discovery.is_printer_available.return_value = True
        
        self.manager._printer_cache = {p.name: p for p in self.mock_printers}
        
        result = self.manager.select_default_printer()
        
        assert result == True
        assert self.manager._selected_printer.name == "HP LaserJet"
    
    @patch.object(PrinterManager, 'list_text_printers')
    @patch('pytextprinter.printer_manager.PrinterDiscovery')
    def test_auto_select_text_printer(self, mock_discovery_class, mock_list):
        """Test auto-selecting text printer."""
        mock_discovery = Mock()
        mock_discovery_class.return_value = mock_discovery
        mock_discovery.is_printer_available.return_value = True
        
        mock_list.return_value = [self.mock_printers[1]]  # Epson thermal printer
        
        result = self.manager.auto_select_text_printer()
        
        assert result == True
        assert self.manager._selected_printer.name == "Epson TM-T88V"
    
    def test_get_selected_printer(self):
        """Test getting selected printer."""
        assert self.manager.get_selected_printer() is None
        
        self.manager._selected_printer = self.mock_printers[0]
        selected = self.manager.get_selected_printer()
        
        assert selected.name == "HP LaserJet"
    
    def test_is_printer_selected(self):
        """Test checking if printer is selected."""
        assert self.manager.is_printer_selected() == False
        
        self.manager._selected_printer = self.mock_printers[0]
        assert self.manager.is_printer_selected() == True
    
    @patch('pytextprinter.printer_manager.PrinterDiscovery')
    def test_get_printer_status(self, mock_discovery_class):
        """Test getting printer status."""
        mock_discovery = Mock()
        mock_discovery_class.return_value = mock_discovery
        mock_discovery.get_printer_info.return_value = self.mock_printers[0]
        
        # Test with specific printer name
        status = self.manager.get_printer_status("HP LaserJet")
        assert status == "Ready"
        
        # Test with selected printer
        self.manager._selected_printer = self.mock_printers[1]
        status = self.manager.get_printer_status()
        mock_discovery.get_printer_info.assert_called_with("Epson TM-T88V")
    
    @patch('builtins.print')
    def test_print_printer_list(self, mock_print):
        """Test printing printer list."""
        self.manager._printer_cache = {p.name: p for p in self.mock_printers}
        
        with patch.object(self.manager.discovery, 'is_printer_available', return_value=True):
            self.manager.print_printer_list(text_only=False)
        
        # Verify print was called (exact content checking is complex due to formatting)
        assert mock_print.called
    
    @patch('builtins.input', return_value='1')
    @patch('builtins.print')
    @patch.object(PrinterManager, 'select_printer', return_value=True)
    def test_select_printer_interactive_success(self, mock_select, mock_print, mock_input):
        """Test interactive printer selection success."""
        self.manager._printer_cache = {p.name: p for p in self.mock_printers[:2]}
        
        with patch.object(self.manager, 'list_text_printers', return_value=self.mock_printers[:2]):
            result = self.manager.select_printer_interactive()
        
        assert result == True
        mock_select.assert_called_once()
    
    @patch('builtins.input', return_value='q')
    @patch('builtins.print')
    def test_select_printer_interactive_quit(self, mock_print, mock_input):
        """Test interactive printer selection quit."""
        self.manager._printer_cache = {p.name: p for p in self.mock_printers[:2]}
        
        with patch.object(self.manager, 'list_text_printers', return_value=self.mock_printers[:2]):
            result = self.manager.select_printer_interactive()
        
        assert result == False
    
    @patch('builtins.input', return_value='invalid')
    @patch('builtins.print')
    def test_select_printer_interactive_invalid_input(self, mock_print, mock_input):
        """Test interactive printer selection with invalid input."""
        self.manager._printer_cache = {p.name: p for p in self.mock_printers[:2]}
        
        with patch.object(self.manager, 'list_text_printers', return_value=self.mock_printers[:2]):
            result = self.manager.select_printer_interactive()
        
        assert result == False
    
    @patch('pytextprinter.printer_manager.PrinterDiscovery')
    def test_get_printer_capabilities(self, mock_discovery_class):
        """Test getting printer capabilities."""
        mock_discovery = Mock()
        mock_discovery_class.return_value = mock_discovery
        mock_discovery.get_printer_info.return_value = self.mock_printers[1]  # Thermal printer
        
        capabilities = self.manager.get_printer_capabilities("Epson TM-T88V")
        
        assert capabilities['name'] == "Epson TM-T88V"
        assert capabilities['is_thermal'] == True
        assert 'supports_graphics' in capabilities
    
    def test_thermal_printer_detection(self):
        """Test thermal printer detection."""
        thermal_printer = PrinterInfo("Epson TM-T88V", "Epson Thermal", "USB", "Ready")
        laser_printer = PrinterInfo("HP LaserJet", "HP Driver", "USB", "Ready")
        
        assert self.manager._is_thermal_printer(thermal_printer) == True
        assert self.manager._is_thermal_printer(laser_printer) == False