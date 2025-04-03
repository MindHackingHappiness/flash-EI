"""
Main EI-harness-lite class for using the MHH EI superprompt with various LLMs.
"""

from typing import Optional, Type, Dict, Any, Union, List, Tuple
import os

from .models.base import BaseModel
from .models.openai import OpenAIModel
from .utils.prompt_loader import load_prompt_from_url, DEFAULT_PROMPT_URL
from .utils.token_counter import count_tokens, count_message_tokens, check_context_window
from .utils.color import info, warning, error, success, format_tokens


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
        enable_cache: bool = True,
        verbose: bool = True,
    ):
        """
        Initialize the EI harness.
        
        Args:
            model_provider: The model provider to use. Can be a BaseModel subclass or a string
                           ("openai", "anthropic", "gemini").
            api_key: API key for the model provider.
            model_name: Name of the model to use (e.g., "gpt-4", "claude-2").
            prompt_url: URL to load the superprompt from. If None, uses the default URL.
            enable_cache: Whether to enable OpenAI's API-level caching (50% discount on input tokens).
            verbose: Whether to print token counts and cost estimates.
        """
        self.prompt_url = prompt_url or DEFAULT_PROMPT_URL
        self.superprompt = None
        self.superprompt_tokens = 0
        self.enable_cache = enable_cache
        self.verbose = verbose
        self.model_name = model_name
        
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
        
        # Count tokens in the superprompt
        if hasattr(self.model, 'model'):
            model_name = self.model.model
        else:
            model_name = self.model_name
            
        self.superprompt_tokens = count_tokens(self.superprompt, model_name)
        
        if self.verbose:
            print(info(f"Loaded superprompt from {self.prompt_url}"))
            print(info(f"Superprompt size: {format_tokens(self.superprompt_tokens)} tokens"))
            
            # Check context window
            context_check = check_context_window(model_name, self.superprompt_tokens)
            if context_check["level"] == "warning":
                print(warning(context_check["message"]))
            elif context_check["level"] == "error":
                print(error(context_check["message"]))
            else:
                print(info(context_check["message"]))
        
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
        
        # Pass enable_cache parameter
        if "enable_cache" not in kwargs:
            kwargs["enable_cache"] = self.enable_cache
        
        # Send to model and get response
        response = self.model.generate(full_prompt, **kwargs)
        
        # Print usage information if verbose
        if self.verbose:
            print("\n" + self.model.format_usage_info())
        
        return response
    
    def get_usage_info(self) -> Dict[str, Any]:
        """
        Get information about the last API call.
        
        Returns:
            A dictionary with usage information.
        """
        usage_info = self.model.get_usage_info()
        usage_info["superprompt_tokens"] = self.superprompt_tokens
        usage_info["superprompt_url"] = self.prompt_url
        return usage_info
