"""
Tests for the token counter utility.
"""

import pytest
from ei_harness.utils.token_counter import (
    count_tokens,
    count_message_tokens,
    estimate_cost,
    check_context_window,
    MODEL_PRICING,
    MODEL_CONTEXT_WINDOW
)


def test_count_tokens():
    """Test the count_tokens function."""
    # Test with a simple string
    text = "This is a test sentence."
    tokens = count_tokens(text, "gpt-4")
    assert tokens > 0, "Token count should be greater than 0"
    assert isinstance(tokens, int), "Token count should be an integer"
    
    # Test with an empty string
    empty_text = ""
    empty_tokens = count_tokens(empty_text, "gpt-4")
    assert empty_tokens == 0, "Empty string should have 0 tokens"
    
    # Test with a longer text
    long_text = "This is a much longer text that should have more tokens. " * 10
    long_tokens = count_tokens(long_text, "gpt-4")
    assert long_tokens > tokens, "Longer text should have more tokens"


def test_count_message_tokens():
    """Test the count_message_tokens function."""
    # Test with a simple message
    messages = [{"role": "user", "content": "Hello, how are you?"}]
    tokens = count_message_tokens(messages, "gpt-4")
    assert tokens > 0, "Token count should be greater than 0"
    assert isinstance(tokens, int), "Token count should be an integer"
    
    # Test with multiple messages
    multi_messages = [
        {"role": "system", "content": "You are a helpful assistant."},
        {"role": "user", "content": "Hello, how are you?"},
        {"role": "assistant", "content": "I'm doing well, thank you for asking!"}
    ]
    multi_tokens = count_message_tokens(multi_messages, "gpt-4")
    assert multi_tokens > tokens, "Multiple messages should have more tokens"


def test_estimate_cost():
    """Test the estimate_cost function."""
    # Test with a valid model
    model = "gpt-4"
    input_tokens = 100
    output_tokens = 50
    
    # Test without caching
    cost = estimate_cost(model, input_tokens, output_tokens, False)
    assert "input_cost" in cost, "Cost should include input_cost"
    assert "output_cost" in cost, "Cost should include output_cost"
    assert "total_cost" in cost, "Cost should include total_cost"
    assert cost["cached"] is False, "Cached flag should be False"
    
    # Calculate expected costs
    expected_input_cost = MODEL_PRICING[model]["input"] * input_tokens
    expected_output_cost = MODEL_PRICING[model]["output"] * output_tokens
    expected_total_cost = expected_input_cost + expected_output_cost
    
    assert cost["input_cost"] == pytest.approx(expected_input_cost, rel=1e-6), "Input cost calculation is incorrect"
    assert cost["output_cost"] == pytest.approx(expected_output_cost, rel=1e-6), "Output cost calculation is incorrect"
    assert cost["total_cost"] == pytest.approx(expected_total_cost, rel=1e-6), "Total cost calculation is incorrect"
    
    # Test with caching
    cached_cost = estimate_cost(model, input_tokens, output_tokens, True)
    assert cached_cost["cached"] is True, "Cached flag should be True"
    assert cached_cost["input_cost"] == pytest.approx(expected_input_cost * 0.5, rel=1e-6), "Cached input cost should be 50% of normal cost"
    assert cached_cost["total_cost"] < cost["total_cost"], "Cached total cost should be less than normal cost"
    
    # Test with invalid model
    with pytest.raises(ValueError):
        estimate_cost("invalid-model", input_tokens, output_tokens)


def test_check_context_window():
    """Test the check_context_window function."""
    # Test with a valid model and tokens within limit
    model = "gpt-4"
    token_count = MODEL_CONTEXT_WINDOW[model] // 2  # Half the context window
    
    result = check_context_window(model, token_count)
    assert result["valid"] is True, "Should be valid when tokens are within limit"
    assert "message" in result, "Result should include a message"
    assert "level" in result, "Result should include a level"
    assert "percentage" in result, "Result should include a percentage"
    assert result["percentage"] == pytest.approx(50.0, rel=1e-6), "Percentage should be around 50%"
    
    # Test with tokens exceeding limit
    over_limit = MODEL_CONTEXT_WINDOW[model] + 100
    over_result = check_context_window(model, over_limit)
    assert over_result["valid"] is False, "Should be invalid when tokens exceed limit"
    assert over_result["level"] == "error", "Level should be 'error' when tokens exceed limit"
    
    # Test with tokens near limit (90%+)
    near_limit = int(MODEL_CONTEXT_WINDOW[model] * 0.95)  # 95% of context window
    near_result = check_context_window(model, near_limit)
    assert near_result["valid"] is True, "Should be valid when tokens are near limit"
    assert near_result["level"] == "warning", "Level should be 'warning' when tokens are near limit"
    
    # Test with invalid model
    invalid_result = check_context_window("invalid-model", token_count)
    assert "valid" in invalid_result, "Result should include valid flag even for invalid model"
    assert "message" in invalid_result, "Result should include a message for invalid model"
