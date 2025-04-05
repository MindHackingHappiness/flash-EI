"""
Anthropic model implementation for EI-harness-lite.
"""

import os
import logging
from typing import Dict, List, Optional, Union, Any

from .base import BaseModel
from ..utils.token_counter import count_tokens, estimate_cost

# Set up logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class AnthropicModel(BaseModel):
    """
    Anthropic model implementation.
    
    Note: To use Anthropic models, install the anthropic package with `pip install anthropic`.
    """
    
    def __init__(
        self,
        model: str = "claude-3-sonnet",
        api_key: Optional[str] = None,
        enable_cache: bool = True,
        **kwargs
    ):
        """
        Initialize the Anthropic model.
        
        Args:
            model: The name of the model to use (e.g., "claude-3-sonnet").
            api_key: The Anthropic API key. If None, will try to get from environment.
            enable_cache: Whether to enable caching for identical requests.
            **kwargs: Additional arguments to pass to the Anthropic API.
        """
        super().__init__(api_key=api_key)
        self.model = model
        self.kwargs = kwargs
        self.enable_cache = enable_cache
        self.cache = {}
        
        try:
            import anthropic
            self.client = anthropic.Anthropic(api_key=self.api_key or os.environ.get("ANTHROPIC_API_KEY"))
            logger.info(f"Initialized Anthropic model: {self.model}")
        except ImportError:
            logger.error("Failed to import anthropic. Please install the anthropic package.")
            raise
    
    def generate(self, prompt: str, **kwargs) -> str:
        """
        Generate a response using the Anthropic API.
        
        Args:
            prompt: The prompt to send to the model.
            **kwargs: Additional arguments to pass to the Anthropic API.
        
        Returns:
            The generated response.
        """
        # Merge kwargs with self.kwargs, with kwargs taking precedence
        params = {**self.kwargs, **kwargs}
        
        # Set default parameters if not provided
        if "temperature" not in params:
            params["temperature"] = 0.7
        if "max_tokens" not in params:
            params["max_tokens"] = 1000
        
        # Check cache for identical prompts
        cache_key = f"{self.model}:{prompt}:{params.get('temperature')}:{params.get('max_tokens')}"
        cached = False
        
        if self.enable_cache and cache_key in self.cache:
            logger.info("Using cached response")
            response_text = self.cache[cache_key]["response"]
            cached = True
        else:
            try:
                import anthropic
                
                # Format the prompt according to Anthropic's requirements
                # For Claude 3 models, we use the messages API
                messages = [
                    {
                        "role": "user",
                        "content": prompt
                    }
                ]
                
                # Generate the response
                response = self.client.messages.create(
                    model=self.model,
                    messages=messages,
                    max_tokens=params.get("max_tokens", 1000),
                    temperature=params.get("temperature", 0.7),
                )
                
                # Extract the response text
                response_text = response.content[0].text
                
                # Cache the response
                if self.enable_cache:
                    self.cache[cache_key] = {
                        "response": response_text,
                        "prompt_tokens": response.usage.input_tokens,
                        "completion_tokens": response.usage.output_tokens
                    }
                
                # Store usage information
                self.last_usage = {
                    "usage": {
                        "prompt_tokens": response.usage.input_tokens,
                        "completion_tokens": response.usage.output_tokens,
                        "total_tokens": response.usage.input_tokens + response.usage.output_tokens
                    },
                    "model": self.model,
                    "cached": cached
                }
                
                # Calculate cost
                self.last_usage["cost"] = estimate_cost(
                    self.model,
                    response.usage.input_tokens,
                    response.usage.output_tokens,
                    cached
                )
                
                logger.info(f"Generated response with {response.usage.input_tokens} input tokens and {response.usage.output_tokens} output tokens")
                
            except Exception as e:
                logger.error(f"Error generating response: {e}")
                raise
        
        return response_text
    
    def count_tokens(self, text: str) -> int:
        """
        Count the number of tokens in the text.
        
        Args:
            text: The text to count tokens for.
        
        Returns:
            The number of tokens.
        """
        try:
            import anthropic
            # Use the anthropic tokenizer if available
            return anthropic.count_tokens(text)
        except (ImportError, AttributeError):
            logger.warning("anthropic.count_tokens not available. Using approximate token count.")
            # Fall back to our token counter
            return count_tokens(text, self.model)
