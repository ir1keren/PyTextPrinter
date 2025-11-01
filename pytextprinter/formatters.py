"""Text formatting utilities for tables, banners, and other layouts."""

from typing import List, Optional


class TableFormatter:
    """Formatter for creating ASCII tables."""
    
    def format_table(self, data: List[List[str]], headers: Optional[List[str]] = None,
                    title: Optional[str] = None) -> str:
        """Format data as an ASCII table.
        
        Args:
            data: 2D list of table data
            headers: Optional list of column headers
            title: Optional table title
            
        Returns:
            Formatted table as string
        """
        if not data:
            return ""
        
        # Combine headers and data for width calculation
        all_rows = []
        if headers:
            all_rows.append(headers)
        all_rows.extend(data)
        
        # Calculate column widths
        col_widths = []
        for col_idx in range(len(all_rows[0])):
            width = max(len(str(row[col_idx])) for row in all_rows if col_idx < len(row))
            col_widths.append(width)
        
        # Create table
        lines = []
        
        # Add title if provided
        if title:
            total_width = sum(col_widths) + 3 * (len(col_widths) - 1) + 4
            lines.append("+" + "-" * (total_width - 2) + "+")
            title_line = f"| {title:^{total_width - 4}} |"
            lines.append(title_line)
        
        # Create separator line
        separator = "+" + "+".join("-" * (width + 2) for width in col_widths) + "+"
        lines.append(separator)
        
        # Add headers if provided
        if headers:
            header_line = "|" + "|".join(f" {headers[i]:<{col_widths[i]}} " for i in range(len(headers))) + "|"
            lines.append(header_line)
            lines.append(separator)
        
        # Add data rows
        for row in data:
            row_line = "|" + "|".join(f" {str(row[i]):<{col_widths[i]}} " if i < len(row) else f" {'':<{col_widths[i]}} " for i in range(len(col_widths))) + "|"
            lines.append(row_line)
        
        lines.append(separator)
        return "\n".join(lines)


class BannerFormatter:
    """Formatter for creating text banners."""
    
    def create_banner(self, text: str, char: str = '=', width: int = 50) -> str:
        """Create a banner with the given text.
        
        Args:
            text: Text for the banner
            char: Character to use for the banner border
            width: Width of the banner
            
        Returns:
            Formatted banner as string
        """
        # Ensure width is at least as long as text + padding
        min_width = len(text) + 4
        if width < min_width:
            width = min_width
        
        border = char * width
        padding = (width - len(text) - 2) // 2
        text_line = char + ' ' * padding + text + ' ' * (width - len(text) - padding - 2) + char
        
        return f"{border}\n{text_line}\n{border}"
    
    def create_simple_banner(self, text: str, char: str = '-') -> str:
        """Create a simple underlined banner.
        
        Args:
            text: Text for the banner
            char: Character to use for underlining
            
        Returns:
            Simple banner as string
        """
        underline = char * len(text)
        return f"{text}\n{underline}"