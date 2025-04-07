"""
Main EI-harness-lite class for using the MHH EI superprompt with various LLMs.
"""

from typing import Optional, Type, Dict, Any, Union, List, Tuple
import os

from .models.base import BaseModel
from .models.openai import OpenAIModel
from .models.anthropic import AnthropicModel
from .models.gemini import GeminiModel
from .utils.prompt_loader import load_prompt_from_url, DEFAULT_PROMPT_URL
from .utils.token_counter import count_tokens, count_message_tokens, check_context_window
from .utils.color import info, warning, error, success, format_tokens
from .utils.model_info import PROVIDER_DOCS, MODEL_PRICING, MODEL_CONTEXT_WINDOW, PROVIDER_CACHING, PROVIDER_MODELS


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
        custom_prompt_text: Optional[str] = None,
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
        self.custom_prompt_text = custom_prompt_text
        self.superprompt = None
        self.superprompt_tokens = 0
        self.enable_cache = enable_cache
        self.verbose = verbose
        self.model_name = model_name
        self.model_provider = model_provider.lower() if isinstance(model_provider, str) else "custom"
        
        # Handle string model provider
        if isinstance(model_provider, str):
            model_provider = model_provider.lower()
            if model_provider == "openai":
                self.model = OpenAIModel(api_key=api_key, model=model_name)
            elif model_provider == "anthropic":
                self.model = AnthropicModel(model=model_name, api_key=api_key, enable_cache=enable_cache)
            elif model_provider == "gemini":
                self.model = GeminiModel(model=model_name, api_key=api_key, enable_cache=enable_cache)
            else:
                raise ValueError(f"Unsupported model provider: {model_provider}. "
                                 f"Supported providers are: openai, anthropic, gemini")
        else:
            # Use the provided model class
            self.model = model_provider(model=model_name, api_key=api_key, enable_cache=enable_cache)
    
    def load_prompt(self) -> str:
        """
        Load the superprompt from the URL or use custom text if provided.
        
        Returns:
            The superprompt text.
        """
        # Use custom prompt text if provided, otherwise load from URL
        if self.custom_prompt_text:
            self.superprompt = self.custom_prompt_text
            source = "custom text"
        else:
            self.superprompt = load_prompt_from_url(self.prompt_url)
            source = f"URL: {self.prompt_url}"
        
        # Count tokens in the superprompt
        if hasattr(self.model, 'model'):
            model_name = self.model.model
        else:
            model_name = self.model_name
            
        self.superprompt_tokens = count_tokens(self.superprompt, model_name)
        
        if self.verbose:
            print(info(f"Loaded superprompt from {source}"))
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

    # Update signature to accept 'prompt' which can be str or list
    def generate(self, prompt: Union[str, List[Dict[str, str]]], image_data: Optional[bytes] = None, **kwargs) -> str:
        """
        Generate a response using the provided prompt/history and optional image data.

        Args:
            prompt: The prompt string or list of message history.
            image_data: Optional image data as bytes.
            **kwargs: Additional arguments to pass to the model, including 'system_instruction'.

        Returns:
            The generated response.
        """

        # Load superprompt if not already loaded
        if self.superprompt is None:
            self.load_prompt()

        # Pass enable_cache parameter
        if "enable_cache" not in kwargs:
            kwargs["enable_cache"] = self.enable_cache

        # Send to model and get response
        # Pass superprompt as system_instruction, prompt as contents
        response = self.model.generate(
            prompt=prompt,  # Pass the original prompt/history
            system_instruction=self.superprompt,  # Pass superprompt separately
            image_data=image_data,
            **kwargs
        )

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
        usage_info["model_provider"] = self.model_provider
        return usage_info
