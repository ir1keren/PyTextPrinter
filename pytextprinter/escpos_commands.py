"""ESC/POS command module for sending raw commands to thermal and text printers."""

import struct
from typing import Union, List, Optional, Tuple
from enum import Enum


class ESCPOSCommands:
    """ESC/POS command constants and utilities."""
    
    # Basic ESC/POS commands
    ESC = b'\x1b'
    GS = b'\x1d'
    FS = b'\x1c'
    DLE = b'\x10'
    LF = b'\n'
    CR = b'\r'
    FF = b'\x0c'
    NULL = b'\x00'
    
    # Initialize printer
    INIT = ESC + b'@'
    
    # Text formatting
    BOLD_ON = ESC + b'E' + b'\x01'
    BOLD_OFF = ESC + b'E' + b'\x00'
    UNDERLINE_ON = ESC + b'-' + b'\x01'
    UNDERLINE_OFF = ESC + b'-' + b'\x00'
    ITALIC_ON = ESC + b'4'
    ITALIC_OFF = ESC + b'5'
    DOUBLE_HEIGHT_ON = ESC + b'!' + b'\x10'
    DOUBLE_WIDTH_ON = ESC + b'!' + b'\x20'
    DOUBLE_SIZE_ON = ESC + b'!' + b'\x30'
    NORMAL_SIZE = ESC + b'!' + b'\x00'
    
    # Character sets
    SELECT_CHARSET_USA = ESC + b'R' + b'\x00'
    SELECT_CHARSET_FRANCE = ESC + b'R' + b'\x01'
    SELECT_CHARSET_GERMANY = ESC + b'R' + b'\x02'
    SELECT_CHARSET_UK = ESC + b'R' + b'\x03'
    
    # Code pages
    SELECT_CODEPAGE_CP437 = ESC + b't' + b'\x00'
    SELECT_CODEPAGE_CP850 = ESC + b't' + b'\x02'
    SELECT_CODEPAGE_CP858 = ESC + b't' + b'\x13'
    SELECT_CODEPAGE_WIN1252 = ESC + b't' + b'\x10'
    
    # Alignment
    ALIGN_LEFT = ESC + b'a' + b'\x00'
    ALIGN_CENTER = ESC + b'a' + b'\x01'
    ALIGN_RIGHT = ESC + b'a' + b'\x02'
    
    # Line spacing
    DEFAULT_LINE_SPACING = ESC + b'2'
    SET_LINE_SPACING = ESC + b'3'  # + 1 byte for spacing value
    
    # Feed commands
    PAPER_CUT_PARTIAL = GS + b'V' + b'A'
    PAPER_CUT_FULL = GS + b'V' + b'B'
    FEED_LINE = LF
    FEED_LINES = ESC + b'd'  # + 1 byte for number of lines
    FEED_TO_CUT_POSITION = GS + b'V' + b'\x00'
    
    # Barcode commands
    BARCODE_HEIGHT = GS + b'h'  # + 1 byte for height
    BARCODE_WIDTH = GS + b'w'   # + 1 byte for width
    BARCODE_POSITION = GS + b'H'  # + 1 byte for position
    BARCODE_FONT = GS + b'f'    # + 1 byte for font
    PRINT_BARCODE = GS + b'k'   # + barcode type + data
    
    # QR Code commands
    QR_MODEL = GS + b'(k' + b'\x04\x00' + b'1A'  # + model (1 or 2)
    QR_SIZE = GS + b'(k' + b'\x03\x00' + b'1C'   # + size (1-16)
    QR_ERROR_CORRECTION = GS + b'(k' + b'\x03\x00' + b'1E'  # + level
    QR_STORE_DATA = GS + b'(k'  # + length + '1P0' + data
    QR_PRINT = GS + b'(k' + b'\x03\x00' + b'1Q' + b'0'
    
    # Drawer control
    OPEN_DRAWER_1 = ESC + b'p' + b'\x00' + b'\x19' + b'\xfa'
    OPEN_DRAWER_2 = ESC + b'p' + b'\x01' + b'\x19' + b'\xfa'
    
    # Status commands
    STATUS_PRINTER = DLE + b'\x04' + b'\x01'
    STATUS_OFFLINE = DLE + b'\x04' + b'\x02'
    STATUS_ERROR = DLE + b'\x04' + b'\x03'
    STATUS_PAPER = DLE + b'\x04' + b'\x04'


class TextAlignment(Enum):
    """Text alignment options."""
    LEFT = 0
    CENTER = 1
    RIGHT = 2


class BarcodeType(Enum):
    """Supported barcode types."""
    UPC_A = 0
    UPC_E = 1
    EAN13 = 2
    EAN8 = 3
    CODE39 = 4
    ITF = 5
    CODABAR = 6
    CODE93 = 7
    CODE128 = 8


class ESCPOSCommandBuilder:
    """Builder class for creating ESC/POS command sequences."""
    
    def __init__(self):
        """Initialize the command builder."""
        self.commands = bytearray()
    
    def clear(self) -> 'ESCPOSCommandBuilder':
        """Clear all commands."""
        self.commands.clear()
        return self
    
    def get_commands(self) -> bytes:
        """Get the built command sequence."""
        return bytes(self.commands)
    
    def init_printer(self) -> 'ESCPOSCommandBuilder':
        """Initialize the printer."""
        self.commands.extend(ESCPOSCommands.INIT)
        return self
    
    def text(self, text: str, encoding: str = 'cp437') -> 'ESCPOSCommandBuilder':
        """Add text to the command sequence.
        
        Args:
            text: Text to print
            encoding: Character encoding to use
        """
        try:
            encoded_text = text.encode(encoding)
            self.commands.extend(encoded_text)
        except UnicodeEncodeError:
            # Fallback to UTF-8 with error replacement
            encoded_text = text.encode('utf-8', errors='replace')
            self.commands.extend(encoded_text)
        return self
    
    def line(self, text: str = "", encoding: str = 'cp437') -> 'ESCPOSCommandBuilder':
        """Add a line of text with line feed.
        
        Args:
            text: Text to print
            encoding: Character encoding to use
        """
        if text:
            self.text(text, encoding)
        self.commands.extend(ESCPOSCommands.LF)
        return self
    
    def bold(self, enabled: bool = True) -> 'ESCPOSCommandBuilder':
        """Set bold text formatting."""
        if enabled:
            self.commands.extend(ESCPOSCommands.BOLD_ON)
        else:
            self.commands.extend(ESCPOSCommands.BOLD_OFF)
        return self
    
    def underline(self, enabled: bool = True) -> 'ESCPOSCommandBuilder':
        """Set underline text formatting."""
        if enabled:
            self.commands.extend(ESCPOSCommands.UNDERLINE_ON)
        else:
            self.commands.extend(ESCPOSCommands.UNDERLINE_OFF)
        return self
    
    def italic(self, enabled: bool = True) -> 'ESCPOSCommandBuilder':
        """Set italic text formatting."""
        if enabled:
            self.commands.extend(ESCPOSCommands.ITALIC_ON)
        else:
            self.commands.extend(ESCPOSCommands.ITALIC_OFF)
        return self
    
    def double_height(self, enabled: bool = True) -> 'ESCPOSCommandBuilder':
        """Set double height text."""
        if enabled:
            self.commands.extend(ESCPOSCommands.DOUBLE_HEIGHT_ON)
        else:
            self.commands.extend(ESCPOSCommands.NORMAL_SIZE)
        return self
    
    def double_width(self, enabled: bool = True) -> 'ESCPOSCommandBuilder':
        """Set double width text."""
        if enabled:
            self.commands.extend(ESCPOSCommands.DOUBLE_WIDTH_ON)
        else:
            self.commands.extend(ESCPOSCommands.NORMAL_SIZE)
        return self
    
    def double_size(self, enabled: bool = True) -> 'ESCPOSCommandBuilder':
        """Set double size (width and height) text."""
        if enabled:
            self.commands.extend(ESCPOSCommands.DOUBLE_SIZE_ON)
        else:
            self.commands.extend(ESCPOSCommands.NORMAL_SIZE)
        return self
    
    def normal_size(self) -> 'ESCPOSCommandBuilder':
        """Reset text to normal size."""
        self.commands.extend(ESCPOSCommands.NORMAL_SIZE)
        return self
    
    def align(self, alignment: TextAlignment) -> 'ESCPOSCommandBuilder':
        """Set text alignment."""
        if alignment == TextAlignment.LEFT:
            self.commands.extend(ESCPOSCommands.ALIGN_LEFT)
        elif alignment == TextAlignment.CENTER:
            self.commands.extend(ESCPOSCommands.ALIGN_CENTER)
        elif alignment == TextAlignment.RIGHT:
            self.commands.extend(ESCPOSCommands.ALIGN_RIGHT)
        return self
    
    def align_left(self) -> 'ESCPOSCommandBuilder':
        """Set left text alignment."""
        return self.align(TextAlignment.LEFT)
    
    def align_center(self) -> 'ESCPOSCommandBuilder':
        """Set center text alignment."""
        return self.align(TextAlignment.CENTER)
    
    def align_right(self) -> 'ESCPOSCommandBuilder':
        """Set right text alignment."""
        return self.align(TextAlignment.RIGHT)
    
    def feed_lines(self, lines: int = 1) -> 'ESCPOSCommandBuilder':
        """Feed specified number of lines."""
        if lines <= 0:
            return self
        elif lines == 1:
            self.commands.extend(ESCPOSCommands.FEED_LINE)
        else:
            self.commands.extend(ESCPOSCommands.FEED_LINES)
            self.commands.append(min(lines, 255))
        return self
    
    def set_line_spacing(self, spacing: int) -> 'ESCPOSCommandBuilder':
        """Set line spacing.
        
        Args:
            spacing: Line spacing value (0-255)
        """
        self.commands.extend(ESCPOSCommands.SET_LINE_SPACING)
        self.commands.append(max(0, min(spacing, 255)))
        return self
    
    def default_line_spacing(self) -> 'ESCPOSCommandBuilder':
        """Reset to default line spacing."""
        self.commands.extend(ESCPOSCommands.DEFAULT_LINE_SPACING)
        return self
    
    def paper_cut(self, full_cut: bool = True) -> 'ESCPOSCommandBuilder':
        """Cut paper."""
        if full_cut:
            self.commands.extend(ESCPOSCommands.PAPER_CUT_FULL)
        else:
            self.commands.extend(ESCPOSCommands.PAPER_CUT_PARTIAL)
        return self
    
    def barcode(self, data: str, barcode_type: BarcodeType = BarcodeType.CODE128,
                height: int = 162, width: int = 3) -> 'ESCPOSCommandBuilder':
        """Print a barcode.
        
        Args:
            data: Barcode data
            barcode_type: Type of barcode
            height: Barcode height (1-255)
            width: Barcode width (2-6)
        """
        # Set barcode height
        self.commands.extend(ESCPOSCommands.BARCODE_HEIGHT)
        self.commands.append(max(1, min(height, 255)))
        
        # Set barcode width
        self.commands.extend(ESCPOSCommands.BARCODE_WIDTH)
        self.commands.append(max(2, min(width, 6)))
        
        # Print barcode
        self.commands.extend(ESCPOSCommands.PRINT_BARCODE)
        self.commands.append(barcode_type.value)
        self.commands.extend(data.encode('ascii'))
        self.commands.append(0)  # Null terminator
        
        return self
    
    def qr_code(self, data: str, size: int = 3, error_correction: int = 1) -> 'ESCPOSCommandBuilder':
        """Print a QR code.
        
        Args:
            data: QR code data
            size: QR code size (1-16)
            error_correction: Error correction level (0-3)
        """
        # Set QR code model
        self.commands.extend(ESCPOSCommands.QR_MODEL + b'\x02')
        
        # Set QR code size
        self.commands.extend(ESCPOSCommands.QR_SIZE)
        self.commands.append(max(1, min(size, 16)))
        
        # Set error correction level
        self.commands.extend(ESCPOSCommands.QR_ERROR_CORRECTION)
        self.commands.append(max(0, min(error_correction, 3)))
        
        # Store QR code data
        data_bytes = data.encode('utf-8')
        data_length = len(data_bytes) + 3
        self.commands.extend(ESCPOSCommands.QR_STORE_DATA)
        self.commands.extend(struct.pack('<H', data_length))
        self.commands.extend(b'1P0')
        self.commands.extend(data_bytes)
        
        # Print QR code
        self.commands.extend(ESCPOSCommands.QR_PRINT)
        
        return self
    
    def open_drawer(self, drawer_number: int = 1) -> 'ESCPOSCommandBuilder':
        """Open cash drawer.
        
        Args:
            drawer_number: Drawer number (1 or 2)
        """
        if drawer_number == 2:
            self.commands.extend(ESCPOSCommands.OPEN_DRAWER_2)
        else:
            self.commands.extend(ESCPOSCommands.OPEN_DRAWER_1)
        return self
    
    def raw_command(self, command: bytes) -> 'ESCPOSCommandBuilder':
        """Add raw command bytes.
        
        Args:
            command: Raw command bytes
        """
        self.commands.extend(command)
        return self
    
    def status_request(self, status_type: str = 'printer') -> 'ESCPOSCommandBuilder':
        """Request printer status.
        
        Args:
            status_type: Type of status to request ('printer', 'offline', 'error', 'paper')
        """
        status_commands = {
            'printer': ESCPOSCommands.STATUS_PRINTER,
            'offline': ESCPOSCommands.STATUS_OFFLINE,
            'error': ESCPOSCommands.STATUS_ERROR,
            'paper': ESCPOSCommands.STATUS_PAPER
        }
        
        command = status_commands.get(status_type, ESCPOSCommands.STATUS_PRINTER)
        self.commands.extend(command)
        return self
    
    def charset(self, charset: str = 'usa') -> 'ESCPOSCommandBuilder':
        """Set character set.
        
        Args:
            charset: Character set name ('usa', 'france', 'germany', 'uk')
        """
        charset_commands = {
            'usa': ESCPOSCommands.SELECT_CHARSET_USA,
            'france': ESCPOSCommands.SELECT_CHARSET_FRANCE,
            'germany': ESCPOSCommands.SELECT_CHARSET_GERMANY,
            'uk': ESCPOSCommands.SELECT_CHARSET_UK
        }
        
        command = charset_commands.get(charset.lower(), ESCPOSCommands.SELECT_CHARSET_USA)
        self.commands.extend(command)
        return self
    
    def codepage(self, codepage: str = 'cp437') -> 'ESCPOSCommandBuilder':
        """Set code page.
        
        Args:
            codepage: Code page name ('cp437', 'cp850', 'cp858', 'win1252')
        """
        codepage_commands = {
            'cp437': ESCPOSCommands.SELECT_CODEPAGE_CP437,
            'cp850': ESCPOSCommands.SELECT_CODEPAGE_CP850,
            'cp858': ESCPOSCommands.SELECT_CODEPAGE_CP858,
            'win1252': ESCPOSCommands.SELECT_CODEPAGE_WIN1252
        }
        
        command = codepage_commands.get(codepage.lower(), ESCPOSCommands.SELECT_CODEPAGE_CP437)
        self.commands.extend(command)
        return self