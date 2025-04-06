"""
Google Gemini model implementation for EI-harness-lite.
"""

import os
import logging
import json # Import json for stable cache key generation
import hashlib # Import hashlib for cache key generation
from typing import Dict, List, Optional, Union, Any

from google.generativeai.types import GenerationConfig # Import GenerationConfig explicitly

from .base import BaseModel
from ..utils.token_counter import count_tokens, estimate_cost
from ..utils.model_info import MODEL_PRICING # Import for cost calculation

# Set up logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class GeminiModel(BaseModel):
    """
    Google Gemini model implementation.

    Note: To use Gemini models, install the google-genai package with `pip install google-genai`.
    """

    def __init__(
        self,
        model: str = "gemini-2.0-flash-001",
        api_key: Optional[str] = None,
        enable_cache: bool = True,
        **kwargs
    ):
        """
        Initialize the Gemini model.

        Args:
            model: The name of the model to use (e.g., "gemini-2.0-flash").
            api_key: The Google API key. If None, will try to get from environment.
            enable_cache: Whether to enable caching for identical requests.
            **kwargs: Additional arguments to pass to the Gemini API.
        """
        super().__init__(api_key=api_key)
        self.model = model
        self.kwargs = kwargs
        self.enable_cache = enable_cache
        self.cache = {} # Use in-memory cache for this version

        # Initialize cache stats
        self.cache_stats_file = os.path.join(os.path.expanduser("~"), ".gemini_cache_stats.json")
        try:
            if os.path.exists(self.cache_stats_file):
                with open(self.cache_stats_file, "r") as f:
                    self.cache_stats = json.load(f)
            else:
                self.cache_stats = {"hits": 0, "misses": 0, "tokens_saved": 0, "cost_saved": 0}
        except Exception as e:
            logger.warning(f"Could not load cache stats from {self.cache_stats_file}: {e}")
            self.cache_stats = {"hits": 0, "misses": 0, "tokens_saved": 0, "cost_saved": 0}


        try:
            # Import the Google GenAI SDK
            import google.generativeai as genai

            # Get API key from parameter or environment
            api_key = self.api_key or os.environ.get("GEMINI_API_KEY") or os.environ.get("GOOGLE_API_KEY")
            if not api_key:
                raise ValueError("API key not provided. Please provide an API key via the api_key parameter or set the GEMINI_API_KEY environment variable.")

            # Configure the API key (new SDK pattern)
            genai.configure(api_key=api_key)
            # No client needed for this pattern
            logger.info(f"Configured Gemini SDK for model: {self.model}")
        except ImportError:
            logger.error("Failed to import google.generativeai. Please install the google-genai package.")
            raise

    # Add system_instruction parameter
    def generate(
        self,
        prompt: Union[str, List[Dict[str, str]]],
        system_instruction: Optional[str] = None,
        **kwargs
    ) -> str:
        """
        Generate a response using the Gemini API.

        Args:
            prompt: The prompt string or list of message dictionaries.
            system_instruction: Optional system instruction to provide context.
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

        # Format cache key components separately
        system_key = hashlib.md5(system_instruction.encode()).hexdigest() if system_instruction else None
        prompt_key = json.dumps(prompt, sort_keys=True) if isinstance(prompt, list) else prompt

        # Create cache key with components
        cache_key_parts = [
            self.model,
            system_key,
            prompt_key,
            params.get('temperature'),
            params.get('max_tokens'),
            params.get('top_p'),
            params.get('top_k')
        ]
        cache_key = json.dumps(cache_key_parts, sort_keys=True)
        cached = False

        if self.enable_cache and cache_key in self.cache:
            logger.info("Using cached response")
            cache_data = self.cache[cache_key]
            response_text = cache_data["response"]
            cached = True

            # Update cache stats
            self.cache_stats["hits"] += 1
            prompt_tokens = cache_data["prompt_tokens"]
            self.cache_stats["tokens_saved"] += prompt_tokens

            # Calculate cost savings (75% of input cost)
            input_price = MODEL_PRICING.get(self.model, {}).get("input", 0)
            savings = (prompt_tokens * input_price * 0.75) / 1000 # per 1K tokens
            self.cache_stats["cost_saved"] += savings
            self._save_cache_stats() # Save stats after update

            # Store usage information for cached response
            completion_tokens = cache_data["completion_tokens"]

            self.last_usage = {
                "usage": {
                    "prompt_tokens": prompt_tokens,
                    "completion_tokens": completion_tokens,
                    "total_tokens": prompt_tokens + completion_tokens
                },
                "model": self.model,
                "cached": cached
            }

            # Calculate cost with cache discount
            self.last_usage["cost"] = estimate_cost(
                self.model,
                prompt_tokens,
                completion_tokens,
                cached
            )

            return response_text
        else:
            # Cache miss
            self.cache_stats["misses"] += 1
            self._save_cache_stats() # Save stats after update

            try:
                import google.generativeai as genai

                # Instantiate the model with system instruction (new SDK pattern)
                model_instance = genai.GenerativeModel(
                    model_name=self.model,
                    system_instruction=system_instruction # Pass system instruction here
                )

                # Create GenerationConfig object (new SDK pattern)
                generation_config = GenerationConfig( # Use imported GenerationConfig
                    temperature=params.get("temperature", 0.7),
                    max_output_tokens=params.get("max_tokens", 1000),
                    top_p=params.get("top_p", 1.0),
                    top_k=params.get("top_k", 40)
                )

                # Log the request details before calling the API
                logger.info("--- Gemini API Request ---")
                logger.info(f"Model: {self.model}")
                if system_instruction:
                     logger.info(f"System Instruction: {system_instruction[:100]}...") # Log truncated system instruction
                logger.info(f"Contents: {json.dumps(prompt, indent=2)}") # Log full contents
                logger.info(f"Generation Config: {generation_config}") # Log config object

                # Call generate_content on the model instance
                # Pass the prompt directly (string or list of dicts)
                response = model_instance.generate_content(
                    contents=prompt, # Pass the original prompt argument
                    generation_config=generation_config # Pass the config object
                )

                # Log the response details
                logger.info("--- Gemini API Response ---")
                try:
                    logger.info(f"Response Text: {response.text[:200]}...") # Log truncated response text
                except Exception:
                     # Handle cases where response might not have text (e.g., blocked)
                     logger.warning(f"Could not extract text from response. Response object: {response}")

                # Extract the response text
                response_text = response.text

                # Get accurate token counts from response metadata if available
                prompt_tokens_api = None
                completion_tokens_api = None
                total_tokens_api = None
                # Log usage metadata if available
                if hasattr(response, 'usage_metadata'):
                     logger.info(f"Usage Metadata: {response.usage_metadata}")
                     prompt_tokens_api = getattr(response.usage_metadata, 'prompt_token_count', None)
                     completion_tokens_api = getattr(response.usage_metadata, 'candidates_token_count', None)
                     total_tokens_api = getattr(response.usage_metadata, 'total_token_count', None)
                else:
                     logger.info("No usage metadata found in response.")


                # Use API counts if available, otherwise fallback to approximate counts
                final_prompt_tokens = prompt_tokens_api if prompt_tokens_api is not None else prompt_tokens # prompt_tokens is the pre-call approximation
                final_completion_tokens = completion_tokens_api if completion_tokens_api is not None else self.count_tokens(response_text)

                # Cache the response (store the accurate tokens if we got them)
                if self.enable_cache:
                    self.cache[cache_key] = {
                        "response": response_text,
                        "prompt_tokens": final_prompt_tokens,
                        "completion_tokens": final_completion_tokens
                    }

                # Store usage information using the best available token counts
                self.last_usage = {
                    "usage": {
                        "prompt_tokens": final_prompt_tokens,
                        "completion_tokens": final_completion_tokens,
                        "total_tokens": total_tokens_api if total_tokens_api is not None else final_prompt_tokens + final_completion_tokens
                    },
                    "model": self.model,
                    "cached": cached
                }

                # Calculate cost using the best available token counts
                self.last_usage["cost"] = estimate_cost(
                    self.model,
                    final_prompt_tokens,
                    final_completion_tokens,
                    cached
                )

                logger.info(f"Generated response with {final_prompt_tokens} input tokens and {final_completion_tokens} output tokens (best estimate)")

            except Exception as e:
                logger.error(f"Error generating response: {e}")
                raise

        return response_text

    def count_tokens(self, text: str) -> int:
        """
        Count the number of tokens in the text using Gemini's built-in token counter.

        Args:
            text: The text to count tokens for.

        Returns:
            The number of tokens.
        """
        try:
            import google.generativeai as genai
            # Instantiate the model
            model_instance = genai.GenerativeModel(model_name=self.model)
            # Use the model instance to compute tokens (new SDK pattern)
            response = model_instance.count_tokens(
                contents=text # Pass the raw string or list
            )
            return response.total_tokens

        except (ImportError, AttributeError) as e:
            logger.warning(f"⚠️ IMPORTANT: Could not use Gemini's built-in token counter: {e}")
            logger.warning(f"⚠️ Falling back to approximate token counting method. Token counts may be less accurate.")
            # Fall back to our token counter
            fallback_count = count_tokens(text, self.model)
            logger.warning(f"⚠️ Used fallback token counter: {fallback_count} tokens")
            return fallback_count

    def get_usage_info(self) -> Dict[str, Any]:
        """
        Get information about the last API call.

        Returns:
            A dictionary with usage information.
        """
        usage_info = {}
        if hasattr(self, 'last_usage') and self.last_usage:
            usage_info = self.last_usage.copy() # Make a copy to avoid modifying original
        else:
            usage_info = {"message": "Usage information not available for this model"}

        # Add cache stats
        if hasattr(self, 'cache_stats'):
            usage_info["cache_stats"] = self.cache_stats

        return usage_info

    def _save_cache_stats(self):
        """Save cache statistics to a file."""
        try:
            with open(self.cache_stats_file, "w") as f:
                json.dump(self.cache_stats, f)
        except Exception as e:
            logger.warning(f"Could not save cache stats to {self.cache_stats_file}: {e}")

    def format_usage_info(self) -> str:
        """
        Format usage information for display.

        Returns:
            A formatted string with usage information.
        """
        usage_info = self.get_usage_info() # Get combined usage and cache stats

        if "message" in usage_info and usage_info["message"] == "Usage information not available for this model":
            return usage_info["message"]

        model = usage_info.get("model", self.model)
        cached = usage_info.get("cached", False)
        cache_stats = usage_info.get("cache_stats", {})

        output_lines = []
        output_lines.append(f"Model: {model}")

        if "usage" in usage_info:
            prompt_tokens = usage_info["usage"].get("prompt_tokens", 0)
            completion_tokens = usage_info["usage"].get("completion_tokens", 0)
            total_tokens = usage_info["usage"].get("total_tokens", 0)
            output_lines.append(f"Tokens: {prompt_tokens} (input) + {completion_tokens} (output) = {total_tokens} total")

            cost_info = ""
            if "cost" in usage_info:
                input_cost = usage_info["cost"].get("input_cost", 0)
                output_cost = usage_info["cost"].get("output_cost", 0)
                total_cost = usage_info["cost"].get("total_cost", 0)
                cost_info = f"Cost: ${input_cost:.6f} (input) + ${output_cost:.6f} (output) = ${total_cost:.6f}"

                if cached:
                    cost_info += f" (cached, 75% discount applied)"
                output_lines.append(cost_info)

        # Add cache stats info
        if cache_stats:
            hits = cache_stats.get("hits", 0)
            misses = cache_stats.get("misses", 0)
            total_calls = hits + misses
            hit_rate = hits / total_calls if total_calls > 0 else 0
            tokens_saved = cache_stats.get("tokens_saved", 0)
            cost_saved = cache_stats.get("cost_saved", 0)

            output_lines.append(f"Cache Hits: {hits} ({hit_rate:.1%})")
            output_lines.append(f"Cache Savings: {tokens_saved:,} tokens / ${cost_saved:.4f}")

        return "\n".join(output_lines)
