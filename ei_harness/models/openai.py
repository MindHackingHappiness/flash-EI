"""
OpenAI model implementation.
"""

import openai
from typing import Dict, Any, Optional, List

from .base import BaseModel


class OpenAIModel(BaseModel):
    """
    OpenAI model implementation.
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
        openai.api_key = api_key
    
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
        # Set default parameters
        params = {
            "model": self.model,
            "messages": [{"role": "user", "content": prompt}],
            "temperature": 0.7,
            "max_tokens": 1000,
        }
        
        # Override with any provided kwargs
        params.update(kwargs)
        
        # Make the API call
        response = openai.ChatCompletion.create(**params)
        
        # Extract and return the response text
        return response.choices[0].message.content.strip()
