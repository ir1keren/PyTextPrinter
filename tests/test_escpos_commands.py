"""Test cases for ESC/POS command functionality."""

import pytest
from pytextprinter.escpos_commands import (
    ESCPOSCommands, ESCPOSCommandBuilder, TextAlignment, BarcodeType
)


class TestESCPOSCommands:
    """Test cases for ESC/POS command constants."""
    
    def test_basic_commands(self):
        """Test basic ESC/POS command constants."""
        assert ESCPOSCommands.ESC == b'\x1b'
        assert ESCPOSCommands.GS == b'\x1d'
        assert ESCPOSCommands.LF == b'\n'
        assert ESCPOSCommands.INIT == b'\x1b@'
    
    def test_formatting_commands(self):
        """Test text formatting commands."""
        assert ESCPOSCommands.BOLD_ON == b'\x1bE\x01'
        assert ESCPOSCommands.BOLD_OFF == b'\x1bE\x00'
        assert ESCPOSCommands.UNDERLINE_ON == b'\x1b-\x01'
        assert ESCPOSCommands.UNDERLINE_OFF == b'\x1b-\x00'
    
    def test_alignment_commands(self):
        """Test text alignment commands."""
        assert ESCPOSCommands.ALIGN_LEFT == b'\x1ba\x00'
        assert ESCPOSCommands.ALIGN_CENTER == b'\x1ba\x01'
        assert ESCPOSCommands.ALIGN_RIGHT == b'\x1ba\x02'


class TestESCPOSCommandBuilder:
    """Test cases for ESC/POS command builder."""
    
    def setup_method(self):
        """Set up test fixtures."""
        self.builder = ESCPOSCommandBuilder()
    
    def test_initialization(self):
        """Test builder initialization."""
        assert len(self.builder.commands) == 0
        assert self.builder.get_commands() == b''
    
    def test_clear(self):
        """Test clearing commands."""
        self.builder.text("test")
        assert len(self.builder.commands) > 0
        
        self.builder.clear()
        assert len(self.builder.commands) == 0
    
    def test_init_printer(self):
        """Test printer initialization command."""
        commands = self.builder.init_printer().get_commands()
        assert commands == ESCPOSCommands.INIT
    
    def test_text(self):
        """Test adding text."""
        commands = self.builder.text("Hello").get_commands()
        assert commands == b"Hello"
    
    def test_text_with_encoding(self):
        """Test adding text with encoding."""
        commands = self.builder.text("Café", encoding='utf-8').get_commands()
        assert b"Caf" in commands
    
    def test_line(self):
        """Test adding line with line feed."""
        commands = self.builder.line("Hello").get_commands()
        assert commands == b"Hello\n"
    
    def test_empty_line(self):
        """Test adding empty line."""
        commands = self.builder.line().get_commands()
        assert commands == b"\n"
    
    def test_bold_formatting(self):
        """Test bold text formatting."""
        commands = (self.builder
                   .bold(True)
                   .text("Bold")
                   .bold(False)
                   .text("Normal")
                   .get_commands())
        
        expected = ESCPOSCommands.BOLD_ON + b"Bold" + ESCPOSCommands.BOLD_OFF + b"Normal"
        assert commands == expected
    
    def test_underline_formatting(self):
        """Test underline text formatting."""
        commands = (self.builder
                   .underline(True)
                   .text("Underlined")
                   .underline(False)
                   .get_commands())
        
        expected = ESCPOSCommands.UNDERLINE_ON + b"Underlined" + ESCPOSCommands.UNDERLINE_OFF
        assert commands == expected
    
    def test_alignment(self):
        """Test text alignment."""
        commands = (self.builder
                   .align_center()
                   .text("Centered")
                   .align_left()
                   .get_commands())
        
        expected = ESCPOSCommands.ALIGN_CENTER + b"Centered" + ESCPOSCommands.ALIGN_LEFT
        assert commands == expected
    
    def test_alignment_enum(self):
        """Test alignment using enum."""
        commands = (self.builder
                   .align(TextAlignment.RIGHT)
                   .text("Right")
                   .get_commands())
        
        expected = ESCPOSCommands.ALIGN_RIGHT + b"Right"
        assert commands == expected
    
    def test_double_size_formatting(self):
        """Test double size text formatting."""
        commands = (self.builder
                   .double_size(True)
                   .text("Big")
                   .normal_size()
                   .get_commands())
        
        expected = ESCPOSCommands.DOUBLE_SIZE_ON + b"Big" + ESCPOSCommands.NORMAL_SIZE
        assert commands == expected
    
    def test_feed_lines(self):
        """Test feeding lines."""
        # Single line
        commands = self.builder.clear().feed_lines(1).get_commands()
        assert commands == ESCPOSCommands.FEED_LINE
        
        # Multiple lines
        commands = self.builder.clear().feed_lines(3).get_commands()
        expected = ESCPOSCommands.FEED_LINES + b'\x03'
        assert commands == expected
        
        # Zero lines
        commands = self.builder.clear().feed_lines(0).get_commands()
        assert commands == b''
    
    def test_line_spacing(self):
        """Test line spacing commands."""
        commands = (self.builder
                   .set_line_spacing(30)
                   .text("Spaced")
                   .default_line_spacing()
                   .get_commands())
        
        expected = (ESCPOSCommands.SET_LINE_SPACING + b'\x1e' + 
                   b"Spaced" + ESCPOSCommands.DEFAULT_LINE_SPACING)
        assert commands == expected
    
    def test_paper_cut(self):
        """Test paper cutting commands."""
        # Full cut
        commands = self.builder.paper_cut(True).get_commands()
        assert commands == ESCPOSCommands.PAPER_CUT_FULL
        
        # Partial cut
        commands = self.builder.clear().paper_cut(False).get_commands()
        assert commands == ESCPOSCommands.PAPER_CUT_PARTIAL
    
    def test_barcode(self):
        """Test barcode printing."""
        commands = (self.builder
                   .barcode("123456789", BarcodeType.CODE128, height=100, width=3)
                   .get_commands())
        
        # Should contain barcode height, width, and print commands
        assert ESCPOSCommands.BARCODE_HEIGHT in commands
        assert ESCPOSCommands.BARCODE_WIDTH in commands
        assert ESCPOSCommands.PRINT_BARCODE in commands
        assert b"123456789" in commands
    
    def test_qr_code(self):
        """Test QR code printing."""
        commands = self.builder.qr_code("Hello QR", size=4).get_commands()
        
        # Should contain QR code commands and data
        assert b"Hello QR" in commands
        # QR code commands are complex, just verify data is included
    
    def test_open_drawer(self):
        """Test cash drawer opening."""
        # Drawer 1
        commands = self.builder.open_drawer(1).get_commands()
        assert commands == ESCPOSCommands.OPEN_DRAWER_1
        
        # Drawer 2
        commands = self.builder.clear().open_drawer(2).get_commands()
        assert commands == ESCPOSCommands.OPEN_DRAWER_2
    
    def test_raw_command(self):
        """Test adding raw commands."""
        raw_data = b'\x1b\x21\x30'  # Some ESC/POS command
        commands = self.builder.raw_command(raw_data).get_commands()
        assert commands == raw_data
    
    def test_status_request(self):
        """Test status request commands."""
        commands = self.builder.status_request('printer').get_commands()
        assert commands == ESCPOSCommands.STATUS_PRINTER
        
        commands = self.builder.clear().status_request('paper').get_commands()
        assert commands == ESCPOSCommands.STATUS_PAPER
    
    def test_charset_selection(self):
        """Test character set selection."""
        commands = self.builder.charset('usa').get_commands()
        assert commands == ESCPOSCommands.SELECT_CHARSET_USA
        
        commands = self.builder.clear().charset('germany').get_commands()
        assert commands == ESCPOSCommands.SELECT_CHARSET_GERMANY
    
    def test_codepage_selection(self):
        """Test code page selection."""
        commands = self.builder.codepage('cp437').get_commands()
        assert commands == ESCPOSCommands.SELECT_CODEPAGE_CP437
        
        commands = self.builder.clear().codepage('win1252').get_commands()
        assert commands == ESCPOSCommands.SELECT_CODEPAGE_WIN1252
    
    def test_method_chaining(self):
        """Test that methods return self for chaining."""
        result = (self.builder
                 .init_printer()
                 .bold(True)
                 .align_center()
                 .text("Hello")
                 .line()
                 .paper_cut())
        
        assert result is self.builder
        
        commands = result.get_commands()
        assert len(commands) > 0
    
    def test_complex_receipt(self):
        """Test building a complex receipt."""
        commands = (self.builder
                   .init_printer()
                   .align_center()
                   .bold(True)
                   .line("STORE NAME")
                   .bold(False)
                   .line("123 Main St")
                   .line()
                   .align_left()
                   .line("Item 1          $10.00")
                   .line("Item 2           $5.00")
                   .line("--------------------")
                   .line("Total:          $15.00")
                   .line()
                   .align_center()
                   .line("Thank you!")
                   .feed_lines(3)
                   .paper_cut()
                   .get_commands())
        
        # Verify receipt contains expected elements
        assert b"STORE NAME" in commands
        assert b"Total:" in commands
        assert b"Thank you!" in commands
        assert ESCPOSCommands.PAPER_CUT_FULL in commands


class TestEnums:
    """Test cases for enums."""
    
    def test_text_alignment_enum(self):
        """Test TextAlignment enum values."""
        assert TextAlignment.LEFT.value == 0
        assert TextAlignment.CENTER.value == 1
        assert TextAlignment.RIGHT.value == 2
    
    def test_barcode_type_enum(self):
        """Test BarcodeType enum values."""
        assert BarcodeType.UPC_A.value == 0
        assert BarcodeType.CODE128.value == 8
        assert BarcodeType.EAN13.value == 2