"""
Google Gemini model implementation for EI-harness-lite.
"""

import os
import logging
from typing import Dict, List, Optional, Union, Any

from .base import BaseModel
from ..utils.token_counter import count_tokens, estimate_cost

# Set up logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class GeminiModel(BaseModel):
    """
    Google Gemini model implementation.
    
    Note: To use Gemini models, install the google-generativeai package with `pip install google-generativeai`.
    """
    
    def __init__(
        self,
        model: str = "gemini-1.5-flash",
        api_key: Optional[str] = None,
        enable_cache: bool = True,
        **kwargs
    ):
        """
        Initialize the Gemini model.
        
        Args:
            model: The name of the model to use (e.g., "gemini-1.5-flash").
            api_key: The Google API key. If None, will try to get from environment.
            enable_cache: Whether to enable caching for identical requests.
            **kwargs: Additional arguments to pass to the Gemini API.
        """
        super().__init__(model=model, api_key=api_key, **kwargs)
        self.enable_cache = enable_cache
        self.cache = {}
        
        try:
            import google.generativeai as genai
            genai.configure(api_key=self.api_key or os.environ.get("GOOGLE_API_KEY"))
            self.model_client = genai.GenerativeModel(model_name=self.model)
            logger.info(f"Initialized Gemini model: {self.model}")
        except ImportError:
            logger.error("Failed to import google.generativeai. Please install the google-generativeai package.")
            raise
    
    def generate(self, prompt: str, **kwargs) -> str:
        """
        Generate a response using the Gemini API.
        
        Args:
            prompt: The prompt to send to the model.
            **kwargs: Additional arguments to pass to the Gemini API.
        
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
                import google.generativeai as genai
                
                # Count tokens in the prompt (approximate)
                prompt_tokens = self.count_tokens(prompt)
                logger.info(f"Prompt tokens (approximate): {prompt_tokens}")
                
                # Generate the response
                generation_config = genai.GenerationConfig(
                    temperature=params.get("temperature", 0.7),
                    max_output_tokens=params.get("max_tokens", 1000),
                    top_p=params.get("top_p", 1.0),
                    top_k=params.get("top_k", 40),
                )
                
                response = self.model_client.generate_content(
                    prompt,
                    generation_config=generation_config,
                )
                
                # Extract the response text
                response_text = response.text
                
                # Count tokens in the response (approximate)
                completion_tokens = self.count_tokens(response_text)
                logger.info(f"Completion tokens (approximate): {completion_tokens}")
                
                # Cache the response
                if self.enable_cache:
                    self.cache[cache_key] = {
                        "response": response_text,
                        "prompt_tokens": prompt_tokens,
                        "completion_tokens": completion_tokens
                    }
                
                # Store usage information
                self.last_usage = {
                    "usage": {
                        "prompt_tokens": prompt_tokens,
                        "completion_tokens": completion_tokens,
                        "total_tokens": prompt_tokens + completion_tokens
                    },
                    "model": self.model,
                    "cached": cached
                }
                
                # Calculate cost
                self.last_usage["cost"] = estimate_cost(
                    self.model,
                    prompt_tokens,
                    completion_tokens,
                    cached
                )
                
                logger.info(f"Generated response with {prompt_tokens} input tokens and {completion_tokens} output tokens")
                
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
            import google.generativeai as genai
            
            # Note: As of my knowledge cutoff, Google's API doesn't provide a direct
            # way to count tokens. This is an approximation.
            # In a real implementation, you might want to use a more accurate method.
            
            # Use our token counter
            return count_tokens(text, self.model)
            
        except ImportError:
            logger.warning("google-generativeai package not installed. Using approximate token count.")
            # Approximate token count (4 characters per token)
            return len(text) // 4
