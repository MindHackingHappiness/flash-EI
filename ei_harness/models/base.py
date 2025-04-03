"""
Base model interface for LLM providers.
"""

from abc import ABC, abstractmethod
from typing import Dict, Any, Optional


class BaseModel(ABC):
    """
    Abstract base class for LLM models.
    
    All model implementations should inherit from this class and implement
    the required methods.
    """
    
    def __init__(self, api_key: str):
        """
        Initialize the model.
        
        Args:
            api_key: API key for the model provider.
        """
        self.api_key = api_key
    
    @abstractmethod
    def generate(self, prompt: str, **kwargs) -> str:
        """
        Generate a response from the model.
        
        Args:
            prompt: The prompt to send to the model.
            **kwargs: Additional arguments to pass to the model.
            
        Returns:
            The generated response as a string.
        """
        pass
