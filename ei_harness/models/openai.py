"""
OpenAI model implementation with token counting, cost estimation, and caching support.
"""

import openai
from typing import Dict, Any, Optional, List, Tuple, Union
import json
import hashlib

from .base import BaseModel
from ..utils.token_counter import (
    count_tokens, 
    count_message_tokens, 
    estimate_cost, 
    check_context_window
)
from ..utils.color import (
    format_cost, 
    format_tokens, 
    info, 
    warning, 
    error, 
    success
)


class OpenAIModel(BaseModel):
    """
    OpenAI model implementation with token counting, cost estimation, and caching support.
    """
    
    def __init__(self, api_key: str, model: str = "gpt-4"):
        """
        Initialize the OpenAI model.
        
        Args:
            api_key: OpenAI API key.
            model: Model name to use (e.g., "gpt-4", "gpt-3.5-turbo").
        """
        super().__init__(api_key)
        self.model = model
        self.client = openai.OpenAI(api_key=api_key)
        self.last_usage = None
        self.last_cost = None
        self.last_cached = False
    
    def generate(self, prompt: str, **kwargs) -> str:
        """
        Generate a response using the OpenAI API.
        
        Args:
            prompt: The prompt to send to the model.
            **kwargs: Additional arguments to pass to the OpenAI API.
            
        Returns:
            The generated response as a string.
            
        Raises:
            openai.OpenAIError: If the API request fails.
        """
        # Prepare messages
        if isinstance(prompt, str):
            messages = [{"role": "user", "content": prompt}]
        elif isinstance(prompt, list):
            messages = prompt
        else:
            raise ValueError("Prompt must be a string or a list of message dictionaries")
        
        # Count tokens before API call
        input_tokens = count_message_tokens(messages, self.model)
        
        # Check context window
        context_check = check_context_window(self.model, input_tokens)
        if not context_check["valid"]:
            raise ValueError(context_check["message"])
        
        # Set default parameters
        params = {
            "model": self.model,
            "messages": messages,
            "temperature": 0.7,
            "max_tokens": 1000,
        }
        
        # Override with any provided kwargs
        params.update(kwargs)
        
        # Enable OpenAI's API-level caching by adding cache_id parameter
        # This gives a 50% discount on input tokens when the same prompt is used within an hour
        cache_id = None
        if kwargs.get("enable_cache", True):
            # Create a deterministic cache ID based on the request parameters
            cache_data = {
                "model": params["model"],
                "messages": params["messages"],
                "temperature": params["temperature"],
                "max_tokens": params["max_tokens"],
                # Include other parameters that affect the response
                "top_p": params.get("top_p", 1.0),
                "frequency_penalty": params.get("frequency_penalty", 0.0),
                "presence_penalty": params.get("presence_penalty", 0.0),
            }
            cache_id = hashlib.sha256(json.dumps(cache_data, sort_keys=True).encode()).hexdigest()
            params["cache_id"] = cache_id
        
        # Make the API call
        response = self.client.chat.completions.create(**params)
        
        # Store usage information
        self.last_usage = {
            "prompt_tokens": response.usage.prompt_tokens,
            "completion_tokens": response.usage.completion_tokens,
            "total_tokens": response.usage.total_tokens,
        }
        
        # Check if the response was cached (50% discount on input tokens)
        self.last_cached = hasattr(response, 'cached') and response.cached
        
        # Calculate cost
        self.last_cost = estimate_cost(
            self.model,
            self.last_usage["prompt_tokens"],
            self.last_usage["completion_tokens"],
            self.last_cached
        )
        
        # Extract and return the response text
        return response.choices[0].message.content.strip()
    
    def get_usage_info(self) -> Dict[str, Any]:
        """
        Get information about the last API call.
        
        Returns:
            A dictionary with usage information.
        """
        if not self.last_usage:
            return {"message": "No API calls made yet"}
        
        return {
            "usage": self.last_usage,
            "cost": self.last_cost,
            "cached": self.last_cached,
            "model": self.model,
        }
    
    def format_usage_info(self) -> str:
        """
        Format usage information for display.
        
        Returns:
            A formatted string with usage information.
        """
        if not self.last_usage:
            return "No API calls made yet"
        
        cached_str = " (CACHED: 50% discount on input tokens)" if self.last_cached else ""
        
        lines = [
            f"Model: {self.model}",
            f"Input tokens: {format_tokens(self.last_usage['prompt_tokens'])}{cached_str}",
            f"Output tokens: {format_tokens(self.last_usage['completion_tokens'])}",
            f"Total tokens: {format_tokens(self.last_usage['total_tokens'])}",
            f"Estimated cost: {format_cost(self.last_cost['total_cost'], self.last_cached)}",
        ]
        
        return "\n".join(lines)
