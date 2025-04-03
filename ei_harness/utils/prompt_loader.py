"""
Utility for loading prompts from URLs.
"""

import requests
from typing import Optional

# Default URL for the MHH EI superprompt
DEFAULT_PROMPT_URL = "https://raw.githubusercontent.com/MindHackingHappiness/MHH-EI-for-AI-Language-Enabled-Emotional-Intelligence-and-Theory-of-Mind-Algorithms/main/mhh_ei_for_ai_model.md"

def load_prompt_from_url(url: Optional[str] = None) -> str:
    """
    Load a prompt from a URL.
    
    Args:
        url: The URL to load the prompt from. If None, uses the default URL.
        
    Returns:
        The prompt text.
        
    Raises:
        requests.exceptions.RequestException: If the request fails.
    """
    url = url or DEFAULT_PROMPT_URL
    response = requests.get(url)
    response.raise_for_status()  # Raise an exception for HTTP errors
    return response.text
