import logging
from .base import BaseModel
from .gemini_client import init_client
from .gemini_cache import CacheManager
from .gemini_generation import generate_content

logger = logging.getLogger(__name__)

class GeminiModel(BaseModel):
    """
    Refactored Gemini model implementation.
    """

    def __init__(self, model="gemini-2.0-flash-001", api_key=None, enable_cache=True, cache_ttl_seconds=3600, **kwargs):
        super().__init__(api_key=api_key)
        self.model = model
        self.kwargs = kwargs
        self.enable_cache = enable_cache
        self.cache_ttl_seconds = cache_ttl_seconds
        self.client = init_client()
        if self.enable_cache:
            self.cache_manager = CacheManager()
        else:
            self.cache_manager = None
        self._last_response = None

    # Reverted generate method (text-only)
    def generate(self, prompt, system_instruction=None, **kwargs):
        """
        Generate a response using the Gemini API with context caching.
        """
        params = {**self.kwargs, **kwargs}
        cache_name = None
        if self.enable_cache and system_instruction and self.cache_manager:
            cache_name = self.cache_manager.create_or_get_cache(self.client, self.model, system_instruction, self.cache_ttl_seconds)
        
        # Pass prompt directly
        self._last_response = generate_content(self.client, self.model, prompt, system_instruction, cache_name, params) 
        # Check if response has text attribute before accessing
        return self._last_response.text if hasattr(self._last_response, 'text') else str(self._last_response)


    def count_tokens(self, text):
        """
        Count tokens in the given text using the utility function.
        """
        from ..utils.token_counter import count_tokens
        if isinstance(text, str):
            tokens_text = text
        elif isinstance(text, list):
            tokens_text = "\n".join(str(item) for item in text)
        else:
            tokens_text = str(text)
        return count_tokens(tokens_text, self.model)

    def get_usage_info(self):
        """
        Extract usage metadata from the last generation response.
        Returns a dictionary with token counts, caching info, and available metadata fields.
        """
        if not self._last_response or not hasattr(self._last_response, 'usage_metadata'):
             logger.warning("Usage metadata not available in the last response.")
             return {"message": "Usage metadata not available."}
        try:
            usage_metadata = self._last_response.usage_metadata
            if usage_metadata:
                available_fields = [attr for attr in dir(usage_metadata) if not attr.startswith('__')]
                return {
                    "prompt_token_count": getattr(usage_metadata, 'prompt_token_count', 'N/A'),
                    "candidates_token_count": getattr(usage_metadata, 'candidates_token_count', 'N/A'),
                    "total_token_count": getattr(usage_metadata, 'total_token_count', 'N/A'),
                    "cached_content_token_count": getattr(usage_metadata, 'cached_content_token_count', 0), # Use correct attribute name
                    "available_fields": available_fields
                }
            else:
                logger.warning("Usage metadata object is empty.")
                return {"message": "Usage metadata not available."}
        except Exception as e:
            logger.error(f"Error extracting usage info: {e}")
            return {"message": f"Error extracting usage info: {e}"}

    def clear_cache(self, system_instruction=None):
        """
        Clear the context cache for the given system_instruction.
        This method delegates deletion to the client and updates the local cache mapping.
        """
        if not self.enable_cache or not self.cache_manager or not system_instruction:
            logger.info("Cache clearing skipped: missing prerequisites.")
            return
        # The CacheManager holds caches by system hash; here we lookup by system_instruction.
        system_hash = self.cache_manager._hash_instruction(system_instruction) # Use hashing method
        cache_resource_name = self.cache_manager._cache_map.pop(system_hash, None)
        if not cache_resource_name:
            logger.info(f"No cache found for provided system instruction hash: {system_hash}")
            return
        try:
            self.client.caches.delete(name=cache_resource_name)
            logger.info(f"Deleted context cache: {cache_resource_name}")
        except Exception as e:
            logger.error(f"Error deleting context cache {cache_resource_name}: {e}")
