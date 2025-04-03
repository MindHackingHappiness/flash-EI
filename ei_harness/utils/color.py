"""
Color utilities for terminal output.
"""

import os
from colorama import Fore, Back, Style, init

# Initialize colorama
init(autoreset=True)

# Check if we're in a terminal that supports colors
SUPPORTS_COLOR = os.isatty(1) if hasattr(os, 'isatty') else False

# Define color functions that are safe to use even if terminal doesn't support colors
def colorize(text, color=None, background=None, style=None):
    """
    Colorize text if the terminal supports it.
    
    Args:
        text: The text to colorize.
        color: The foreground color (Fore.X).
        background: The background color (Back.X).
        style: The text style (Style.X).
        
    Returns:
        Colorized text if supported, otherwise the original text.
    """
    if not SUPPORTS_COLOR:
        return text
    
    result = ""
    if color:
        result += color
    if background:
        result += background
    if style:
        result += style
    
    result += str(text)
    result += Style.RESET_ALL
    
    return result


# Predefined color functions
def info(text):
    """Format text as info (cyan)."""
    return colorize(text, Fore.CYAN)

def success(text):
    """Format text as success (green)."""
    return colorize(text, Fore.GREEN)

def warning(text):
    """Format text as warning (yellow)."""
    return colorize(text, Fore.YELLOW)

def error(text):
    """Format text as error (red)."""
    return colorize(text, Fore.RED)

def bold(text):
    """Format text as bold."""
    return colorize(text, style=Style.BRIGHT)

def dim(text):
    """Format text as dim."""
    return colorize(text, style=Style.DIM)

# Cost-specific formatting
def format_cost(cost, cached=False):
    """
    Format a cost value with appropriate color based on amount.
    
    Args:
        cost: The cost value as a float.
        cached: Whether the cost includes caching discount.
        
    Returns:
        Colorized cost string.
    """
    cost_str = f"${cost:.6f}"
    
    if cost >= 0.1:
        return colorize(cost_str, Fore.RED, style=Style.BRIGHT)
    elif cost >= 0.01:
        return colorize(cost_str, Fore.YELLOW)
    else:
        color = Fore.GREEN if not cached else Fore.CYAN
        return colorize(cost_str, color)

def format_tokens(tokens, max_tokens=None):
    """
    Format token count with appropriate color based on percentage of context window.
    
    Args:
        tokens: The token count.
        max_tokens: The maximum tokens (context window size).
        
    Returns:
        Colorized token count string.
    """
    token_str = f"{tokens:,}"
    
    if max_tokens:
        percentage = (tokens / max_tokens) * 100
        if percentage > 90:
            return colorize(token_str, Fore.RED, style=Style.BRIGHT)
        elif percentage > 75:
            return colorize(token_str, Fore.YELLOW)
        elif percentage > 50:
            return colorize(token_str, Fore.CYAN)
        else:
            return colorize(token_str, Fore.GREEN)
    else:
        if tokens > 50000:
            return colorize(token_str, Fore.RED, style=Style.BRIGHT)
        elif tokens > 10000:
            return colorize(token_str, Fore.YELLOW)
        elif tokens > 4000:
            return colorize(token_str, Fore.CYAN)
        else:
            return colorize(token_str, Fore.GREEN)
