"""
Model implementations for different LLM providers.
"""

from .base import BaseModel
from .openai import OpenAIModel

# Import Anthropic model if the package is available
try:
    from .anthropic import AnthropicModel
except ImportError:
    # This allows the package to work without the anthropic package installed
    class AnthropicModel:
        def __init__(self, *args, **kwargs):
            raise ImportError(
                "The anthropic package is required to use AnthropicModel. "
                "Install it with `pip install anthropic`."
            )

# Import Gemini model if the package is available
try:
    from .gemini import GeminiModel
except ImportError:
    # This allows the package to work without the google-generativeai package installed
    class GeminiModel:
        def __init__(self, *args, **kwargs):
            raise ImportError(
                "The google-generativeai package is required to use GeminiModel. "
                "Install it with `pip install google-generativeai`."
            )
