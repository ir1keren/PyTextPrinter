"""Test cases for formatter utilities."""

import pytest
from pytextprinter.formatters import TableFormatter, BannerFormatter


class TestTableFormatter:
    """Test cases for TableFormatter."""
    
    def setup_method(self):
        """Set up test fixtures."""
        self.formatter = TableFormatter()
    
    def test_format_table_with_headers(self):
        """Test table formatting with headers."""
        data = [["Alice", "25"], ["Bob", "30"]]
        headers = ["Name", "Age"]
        result = self.formatter.format_table(data, headers=headers)
        
        assert "Alice" in result
        assert "Bob" in result
        assert "Name" in result
        assert "Age" in result
        assert "|" in result
        assert "+" in result
        assert "-" in result
    
    def test_format_table_without_headers(self):
        """Test table formatting without headers."""
        data = [["Alice", "25"], ["Bob", "30"]]
        result = self.formatter.format_table(data)
        
        assert "Alice" in result
        assert "Bob" in result
        assert "|" in result
        assert "+" in result
    
    def test_format_empty_table(self):
        """Test empty table formatting."""
        result = self.formatter.format_table([])
        assert result == ""


class TestBannerFormatter:
    """Test cases for BannerFormatter."""
    
    def setup_method(self):
        """Set up test fixtures."""
        self.formatter = BannerFormatter()
    
    def test_create_banner(self):
        """Test banner creation."""
        result = self.formatter.create_banner("Test", width=20)
        lines = result.split('\n')
        
        assert len(lines) == 3
        assert all(len(line) == 20 for line in lines)
        assert "Test" in lines[1]
        assert lines[0] == "=" * 20
        assert lines[2] == "=" * 20
    
    def test_create_simple_banner(self):
        """Test simple banner creation."""
        result = self.formatter.create_simple_banner("Test")
        lines = result.split('\n')
        
        assert len(lines) == 2
        assert lines[0] == "Test"
        assert lines[1] == "-" * 4