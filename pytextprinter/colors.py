"""Color constants and utilities for text printing."""

class Colors:
    """ANSI color codes for terminal text coloring."""
    
    # Reset
    RESET = '\033[0m'
    
    # Regular colors
    BLACK = '\033[30m'
    RED = '\033[31m'
    GREEN = '\033[32m'
    YELLOW = '\033[33m'
    BLUE = '\033[34m'
    MAGENTA = '\033[35m'
    CYAN = '\033[36m'
    WHITE = '\033[37m'
    
    # Bold colors
    BOLD_BLACK = '\033[1;30m'
    BOLD_RED = '\033[1;31m'
    BOLD_GREEN = '\033[1;32m'
    BOLD_YELLOW = '\033[1;33m'
    BOLD_BLUE = '\033[1;34m'
    BOLD_MAGENTA = '\033[1;35m'
    BOLD_CYAN = '\033[1;36m'
    BOLD_WHITE = '\033[1;37m'
    
    # Background colors
    BG_BLACK = '\033[40m'
    BG_RED = '\033[41m'
    BG_GREEN = '\033[42m'
    BG_YELLOW = '\033[43m'
    BG_BLUE = '\033[44m'
    BG_MAGENTA = '\033[45m'
    BG_CYAN = '\033[46m'
    BG_WHITE = '\033[47m'
    
    @classmethod
    def get_color(cls, color_name: str) -> str:
        """Get color code by name.
        
        Args:
            color_name: Name of the color (e.g., 'red', 'green', 'blue')
            
        Returns:
            ANSI color code string
        """
        color_map = {
            'black': cls.BLACK,
            'red': cls.RED,
            'green': cls.GREEN,
            'yellow': cls.YELLOW,
            'blue': cls.BLUE,
            'magenta': cls.MAGENTA,
            'cyan': cls.CYAN,
            'white': cls.WHITE,
        }
        return color_map.get(color_name.lower(), cls.WHITE)