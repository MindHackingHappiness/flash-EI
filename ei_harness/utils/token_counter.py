"""
Token counting and cost estimation utilities.
"""

import tiktoken
from typing import Dict, List, Optional, Union, Any

# Import model information from model_info.py
from .model_info import MODEL_PRICING, MODEL_CONTEXT_WINDOW


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
        cached: Whether the input is cached (100% discount on input tokens for Gemini models, 50% for others).
        
    Returns:
        A dictionary with cost breakdown.
    """
    if model not in MODEL_PRICING:
        raise ValueError(f"Unknown model: {model}")
    
    # Apply appropriate discount to input tokens if cached
    # Gemini models get 100% discount (free), others get 50%
    if cached:
        if model.startswith("gemini"):
            input_cost_multiplier = 0.0  # 100% discount (free)
        else:
            input_cost_multiplier = 0.5  # 50% discount
    else:
        input_cost_multiplier = 1.0
    
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
    if cost["cached"]:
        if cost["input_cost"] == 0:
            cached_str = " (100% cached discount applied)"
        else:
            cached_str = " (50% cached discount applied)"
    else:
        cached_str = ""
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
        return {
            "valid": True, 
            "message": "Unknown model, cannot validate context window.",
            "level": "info",  # Always include level key
            "percentage": 0,
            "tokens": token_count,
            "max_tokens": 0
        }
    
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
