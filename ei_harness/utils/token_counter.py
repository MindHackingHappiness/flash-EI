"""
Token counting and cost estimation utilities.
"""

import tiktoken
from typing import Dict, List, Optional, Union, Any

# Current pricing (update from official source)
MODEL_PRICING = {
    "gpt-4-turbo": {"input": 0.01/1e3, "output": 0.03/1e3},
    "gpt-4": {"input": 0.03/1e3, "output": 0.06/1e3},
    "gpt-4-32k": {"input": 0.06/1e3, "output": 0.12/1e3},
    "gpt-3.5-turbo": {"input": 0.0015/1e3, "output": 0.002/1e3},
    "gpt-3.5-turbo-16k": {"input": 0.003/1e3, "output": 0.004/1e3},
}

# Model context window limits
MODEL_CONTEXT_WINDOW = {
    "gpt-4-turbo": 128000,
    "gpt-4": 8192,
    "gpt-4-32k": 32768,
    "gpt-3.5-turbo": 4096,
    "gpt-3.5-turbo-16k": 16384,
}


def count_tokens(text: str, model: str) -> int:
    """
    Count tokens for a text string using the appropriate tokenizer.
    
    Args:
        text: The text to count tokens for.
        model: The model to use for tokenization.
        
    Returns:
        The number of tokens.
    """
    try:
        encoding = tiktoken.encoding_for_model(model)
    except KeyError:
        # Fall back to cl100k_base for models not directly supported
        encoding = tiktoken.get_encoding("cl100k_base")
    
    return len(encoding.encode(text))


def count_message_tokens(messages: List[Dict[str, str]], model: str) -> int:
    """
    Count tokens for a list of messages using OpenAI's tokenizer.
    
    Args:
        messages: The messages to count tokens for.
        model: The model to use for tokenization.
        
    Returns:
        The number of tokens.
    """
    try:
        encoding = tiktoken.encoding_for_model(model)
    except KeyError:
        encoding = tiktoken.get_encoding("cl100k_base")
    
    tokens_per_message = 3  # Base overhead for message formatting
    tokens_per_name = 1     # Additional overhead for role
    
    num_tokens = 0
    for message in messages:
        num_tokens += tokens_per_message
        for key, value in message.items():
            num_tokens += len(encoding.encode(value))
            if key == "name":
                num_tokens += tokens_per_name
    
    # Add completion tokens overhead
    num_tokens += 3
    
    return num_tokens


def estimate_cost(model: str, input_tokens: int, output_tokens: int, cached: bool = False) -> Dict[str, float]:
    """
    Calculate cost estimate with model validation.
    
    Args:
        model: The model name.
        input_tokens: The number of input tokens.
        output_tokens: The number of output tokens.
        cached: Whether the input is cached (50% discount on input tokens).
        
    Returns:
        A dictionary with cost breakdown.
    """
    if model not in MODEL_PRICING:
        raise ValueError(f"Unknown model: {model}")
    
    # Apply 50% discount to input tokens if cached
    input_cost_multiplier = 0.5 if cached else 1.0
    
    input_cost = MODEL_PRICING[model]["input"] * input_tokens * input_cost_multiplier
    output_cost = MODEL_PRICING[model]["output"] * output_tokens
    total_cost = input_cost + output_cost
    
    return {
        "input_cost": round(input_cost, 6),
        "output_cost": round(output_cost, 6),
        "total_cost": round(total_cost, 6),
        "cached": cached,
    }


def format_cost(cost: Dict[str, float]) -> str:
    """
    Format cost information for display.
    
    Args:
        cost: The cost dictionary from estimate_cost.
        
    Returns:
        A formatted string with cost information.
    """
    cached_str = " (50% cached discount applied)" if cost["cached"] else ""
    return (
        f"Cost: ${cost['total_cost']:.6f} total "
        f"(${cost['input_cost']:.6f} input{cached_str} + "
        f"${cost['output_cost']:.6f} output)"
    )


def check_context_window(model: str, token_count: int) -> Dict[str, Any]:
    """
    Check if the token count exceeds the model's context window.
    
    Args:
        model: The model name.
        token_count: The number of tokens.
        
    Returns:
        A dictionary with context window information.
    """
    if model not in MODEL_CONTEXT_WINDOW:
        return {"valid": True, "message": "Unknown model, cannot validate context window."}
    
    max_tokens = MODEL_CONTEXT_WINDOW[model]
    valid = token_count <= max_tokens
    
    if valid:
        percentage = (token_count / max_tokens) * 100
        if percentage > 90:
            message = f"Warning: Using {token_count:,}/{max_tokens:,} tokens ({percentage:.1f}% of context window)"
            level = "warning"
        elif percentage > 75:
            message = f"Note: Using {token_count:,}/{max_tokens:,} tokens ({percentage:.1f}% of context window)"
            level = "info"
        else:
            message = f"Using {token_count:,}/{max_tokens:,} tokens ({percentage:.1f}% of context window)"
            level = "info"
    else:
        message = f"Error: Token count {token_count:,} exceeds model's context window of {max_tokens:,}"
        level = "error"
    
    return {
        "valid": valid,
        "message": message,
        "level": level,
        "percentage": (token_count / max_tokens) * 100 if max_tokens > 0 else 0,
        "tokens": token_count,
        "max_tokens": max_tokens,
    }
