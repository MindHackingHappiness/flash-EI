import hashlib
import logging
from google.genai.types import CreateCachedContentConfig, Content

logger = logging.getLogger(__name__)

class CacheManager:
    """
    Manages the context caching logic for Gemini.
    Caches are keyed by a hash of the system instruction.
    """
    def __init__(self):
        # Internal dictionary mapping system_instruction hash to cache resource name.
        self._cache_map = {}

    def create_or_get_cache(self, client, model, system_instruction, cache_ttl_seconds):
        """
        Create a new cache using the provided system_instruction or return an existing one.
        
        Parameters:
          client: A pre-initialized Gen AI client.
          model: The model identifier to use when creating a cache.
          system_instruction: The system prompt to be cached.
          cache_ttl_seconds: TTL for the cache entry.
          
        Returns:
          The cache resource name, or None if creation failed.
        """
        if not system_instruction or client is None:
            logger.warning("Cache creation skipped: missing system_instruction or client.")
            return None

        system_hash = hashlib.md5(system_instruction.encode()).hexdigest()
        if system_hash in self._cache_map:
            logger.info(f"Using existing cache for system instruction hash {system_hash}")
            return self._cache_map[system_hash]

        # Ensure the cached content meets the minimum token threshold (4096 tokens)
        from ei_harness.utils.token_counter import count_tokens
        token_count = count_tokens(system_instruction, model)
        if token_count < 4096:
            # Generate filler text to pad the content to the minimum required tokens.
            # This filler text is repeated enough times to overcome the deficit.
            filler_text = " This is filler text for padding." * (((4096 - token_count) // 7) + 1)
            padded_content = system_instruction + filler_text
        else:
            padded_content = system_instruction

        # Build the cache contents with the padded content.
        cache_contents = [
            Content(
                role="user",
                parts=[{"text": padded_content}]
            )
        ]
        ttl_str = f"{cache_ttl_seconds}s"
        try:
            cache_config = CreateCachedContentConfig(
                contents=cache_contents,
                system_instruction=system_instruction,
                display_name="flash-2.0-cache",
                ttl=ttl_str
            )
            logger.info("Creating new context cache with TTL %s", ttl_str)
            cache_obj = client.caches.create(model=model, config=cache_config)
            cache_name = cache_obj.name
            self._cache_map[system_hash] = cache_name
            logger.info(f"Created new context cache: {cache_name}")
            return cache_name
        except Exception as e:
            logger.error(f"Error creating context cache: {e}")
            return None
