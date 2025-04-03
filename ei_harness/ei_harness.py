"""
Main EI-harness-lite class for using the MHH EI superprompt with various LLMs.
"""

from typing import Optional, Type, Dict, Any, Union

from .models.base import BaseModel
from .models.openai import OpenAIModel
from .utils.prompt_loader import load_prompt_from_url, DEFAULT_PROMPT_URL


class EIHarness:
    """
    Main class for using the MHH EI superprompt with various LLMs.
    """
    
    def __init__(
        self,
        model_provider: Union[Type[BaseModel], str] = "openai",
        api_key: Optional[str] = None,
        model_name: str = "gpt-4",
        prompt_url: Optional[str] = None,
    ):
        """
        Initialize the EI harness.
        
        Args:
            model_provider: The model provider to use. Can be a BaseModel subclass or a string
                           ("openai", "anthropic", "gemini").
            api_key: API key for the model provider.
            model_name: Name of the model to use (e.g., "gpt-4", "claude-2").
            prompt_url: URL to load the superprompt from. If None, uses the default URL.
        """
        self.prompt_url = prompt_url or DEFAULT_PROMPT_URL
        self.superprompt = None
        
        # Handle string model provider
        if isinstance(model_provider, str):
            if model_provider.lower() == "openai":
                self.model = OpenAIModel(api_key, model_name)
            else:
                raise ValueError(f"Unsupported model provider: {model_provider}")
        else:
            # Use the provided model class
            self.model = model_provider(api_key, model_name)
    
    def load_prompt(self) -> str:
        """
        Load the superprompt from the URL.
        
        Returns:
            The superprompt text.
        """
        self.superprompt = load_prompt_from_url(self.prompt_url)
        return self.superprompt
    
    def generate(self, user_input: str, **kwargs) -> str:
        """
        Generate a response using the superprompt and user input.
        
        Args:
            user_input: The user's input to append to the superprompt.
            **kwargs: Additional arguments to pass to the model.
            
        Returns:
            The generated response.
        """
        if not self.superprompt:
            self.load_prompt()
        
        # Combine superprompt with user input
        full_prompt = f"{self.superprompt}\n\nUser: {user_input}"
        
        # Send to model and get response
        return self.model.generate(full_prompt, **kwargs)
