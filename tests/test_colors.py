"""Test cases for color utilities."""

import pytest
from pytextprinter.colors import Colors


class TestColors:
    """Test cases for Colors class."""
    
    def test_get_color(self):
        """Test color code retrieval."""
        assert Colors.get_color("red") == Colors.RED
        assert Colors.get_color("green") == Colors.GREEN
        assert Colors.get_color("blue") == Colors.BLUE
        assert Colors.get_color("unknown") == Colors.WHITE  # Default
    
    def test_color_constants(self):
        """Test that color constants are defined."""
        assert Colors.RED == '\033[31m'
        assert Colors.GREEN == '\033[32m'
        assert Colors.BLUE == '\033[34m'
        assert Colors.RESET == '\033[0m'
    
    def test_bold_colors(self):
        """Test bold color constants."""
        assert Colors.BOLD_RED == '\033[1;31m'
        assert Colors.BOLD_GREEN == '\033[1;32m'
        assert Colors.BOLD_BLUE == '\033[1;34m'