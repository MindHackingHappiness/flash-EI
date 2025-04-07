import logging
# Removed problematic imports for GenerateContentConfig and Part

logger = logging.getLogger(__name__)

# Reverted generate_content function (text-only) with GenerateContentConfig workaround
def generate_content(client, model, prompt, system_instruction, cache_name, params):
    """
    Generate a response using the given Gen AI client. WORKAROUND: Uses dict for config.
    
    Parameters:
      client (object): A pre-initialized Gen AI client.
      prompt (str or list): The incremental prompt query, either as a string or as a list of message dictionaries.
      system_instruction (str): The system instruction (prep prompt) for caching.
      cache_name (str or None): The cache resource name if available; otherwise, None.
      params (dict): Additional generation parameters (e.g., temperature, max_tokens, top_p, top_k).
    
    Returns:
      response (object): The response object from the generation call.
    """
    # Build the generation configuration dictionary directly.
    gen_config_dict = {
        "temperature": params.get("temperature", 0.7),
        "max_output_tokens": params.get("max_output_tokens", 8000), # Use correct param name
        "top_p": params.get("top_p", 1.0),
        "top_k": params.get("top_k", 40)
    }
    if cache_name:
        gen_config_dict["cached_content"] = cache_name
    # WORKAROUND: Pass the dictionary directly instead of GenerateContentConfig object
    gen_config = gen_config_dict 
    
    # Format the prompt into the required contents.
    if cache_name and isinstance(prompt, str) and prompt.strip() == system_instruction.strip():
        logger.info("Detected incremental query equals system_instruction. Using a single space to trigger cache hit.")
        contents = [{"role": "user", "parts": [{"text": " "}]}]
    else:
        if isinstance(prompt, str):
            contents = [{"role": "user", "parts": [{"text": prompt}]}]
        elif isinstance(prompt, list):
            # Assuming prompt is already in the correct format [{role: ..., parts: [...]}]
            contents = prompt 
        else:
            raise TypeError("Prompt must be a string or a list of message dictionaries.")
    
    # Invoke the client's generation method.
    try:
        # Pass the config dictionary directly
        response = client.models.generate_content(model=model, generation_config=gen_config, contents=contents) 
        logger.info("Generation response received.")
        return response
    except Exception as e:
        logger.error(f"Error during generation: {e}")
        raise
