"""Test cases for the TextPrinter class."""

import pytest
import io
import sys
from pytextprinter import TextPrinter


class TestTextPrinter:
    """Test cases for TextPrinter functionality."""
    
    def setup_method(self):
        """Set up test fixtures."""
        self.output = io.StringIO()
        self.printer = TextPrinter(output=self.output)
    
    def test_print_text(self):
        """Test text printing."""
        self.printer.print_text("Hello")
        output = self.output.getvalue()
        assert "Hello" in output
    
    def test_print_text_bold(self):
        """Test bold text printing."""
        self.printer.print_text("Hello", bold=True)
        output = self.output.getvalue()
        assert "Hello" in output
        assert "\033[1m" in output  # Bold code
        assert "\033[0m" in output   # Reset code
    
    def test_print_banner(self):
        """Test banner printing."""
        self.printer.print_banner("Test", width=20)
        output = self.output.getvalue()
        lines = output.strip().split('\n')
        assert len(lines) == 3
        assert all(len(line) == 20 for line in lines)
        assert "Test" in lines[1]
    
    def test_print_table(self):
        """Test table printing."""
        data = [["Alice", "25"], ["Bob", "30"]]
        headers = ["Name", "Age"]
        self.printer.print_table(data, headers=headers)
        output = self.output.getvalue()
        assert "Alice" in output
        assert "Bob" in output
        assert "Name" in output
        assert "Age" in output
        assert "|" in output  # Table borders
    
    def test_print_list(self):
        """Test list printing."""
        items = ["Item 1", "Item 2", "Item 3"]
        self.printer.print_list(items)
        output = self.output.getvalue()
        for item in items:
            assert item in output
        assert "•" in output  # Default bullet
    
    def test_print_dict(self):
        """Test dictionary printing."""
        data = {"key1": "value1", "key2": "value2"}
        self.printer.print_dict(data)
        output = self.output.getvalue()
        assert "key1:" in output
        assert "value1" in output
        assert "key2:" in output
        assert "value2" in output
    
    def test_print_progress_bar(self):
        """Test progress bar printing."""
        self.printer.print_progress_bar(0.5, width=10)
        output = self.output.getvalue()
        assert "50.0%" in output
        assert "█" in output  # Filled character
        assert "░" in output  # Empty character