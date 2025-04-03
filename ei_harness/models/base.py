"""
Base model interface for LLM providers.
"""

from abc import ABC, abstractmethod
from typing import Dict, Any, Optional, List, Union


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
    def generate(self, prompt: Union[str, List[Dict[str, str]]], **kwargs) -> str:
        """
        Generate a response from the model.
        
        Args:
            prompt: The prompt to send to the model. Can be a string or a list of message dictionaries.
            **kwargs: Additional arguments to pass to the model.
            
        Returns:
            The generated response as a string.
        """
        pass
    
    def get_usage_info(self) -> Dict[str, Any]:
        """
        Get information about the last API call.
        
        Returns:
            A dictionary with usage information.
        """
        return {"message": "Usage information not available for this model"}
    
    def format_usage_info(self) -> str:
        """
        Format usage information for display.
        
        Returns:
            A formatted string with usage information.
        """
        return "Usage information not available for this model"
