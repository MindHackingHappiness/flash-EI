"""
Tests for the OpenAI model implementation.
"""

import pytest
from unittest.mock import patch, MagicMock
from ei_harness.models.openai import OpenAIModel


@pytest.fixture
def mock_openai_client():
    """Create a mock OpenAI client."""
    with patch('openai.OpenAI') as mock_client:
        # Mock the chat completions create method
        mock_create = MagicMock()
        mock_client.return_value.chat.completions.create = mock_create
        
        # Mock the response
        mock_response = MagicMock()
        mock_response.choices = [MagicMock()]
        mock_response.choices[0].message.content = "Test response"
        mock_response.usage.prompt_tokens = 10
        mock_response.usage.completion_tokens = 5
        mock_response.usage.total_tokens = 15
        mock_create.return_value = mock_response
        
        yield mock_client


def test_openai_model_initialization():
    """Test OpenAI model initialization."""
    with patch('openai.OpenAI'):
        model = OpenAIModel(api_key="test_key", model="gpt-4")
        assert model.api_key == "test_key"
        assert model.model == "gpt-4"
        assert model.last_usage is None
        assert model.last_cost is None
        assert model.last_cached is False


def test_generate_method(mock_openai_client):
    """Test the generate method."""
    model = OpenAIModel(api_key="test_key", model="gpt-4")
    
    # Test with a simple prompt
    response = model.generate("Hello, world!")
    
    # Check that the client was called with the correct parameters
    mock_openai_client.return_value.chat.completions.create.assert_called_once()
    call_args = mock_openai_client.return_value.chat.completions.create.call_args[1]
    assert call_args["model"] == "gpt-4"
    assert call_args["messages"][0]["content"] == "Hello, world!"
    assert "cache_id" in call_args  # Should include cache_id for API-level caching
    
    # Check the response
    assert response == "Test response"
    
    # Check usage information
    assert model.last_usage is not None
    assert model.last_usage["prompt_tokens"] == 10
    assert model.last_usage["completion_tokens"] == 5
    assert model.last_usage["total_tokens"] == 15
    
    # Check cost information
    assert model.last_cost is not None
    assert "input_cost" in model.last_cost
    assert "output_cost" in model.last_cost
    assert "total_cost" in model.last_cost


def test_get_usage_info(mock_openai_client):
    """Test the get_usage_info method."""
    model = OpenAIModel(api_key="test_key", model="gpt-4")
    
    # Before any API calls
    initial_info = model.get_usage_info()
    assert "message" in initial_info
    
    # After an API call
    model.generate("Hello, world!")
    usage_info = model.get_usage_info()
    
    assert "usage" in usage_info
    assert "cost" in usage_info
    assert "cached" in usage_info
    assert "model" in usage_info
    assert usage_info["model"] == "gpt-4"


def test_format_usage_info(mock_openai_client):
    """Test the format_usage_info method."""
    model = OpenAIModel(api_key="test_key", model="gpt-4")
    
    # Before any API calls
    initial_info = model.format_usage_info()
    assert isinstance(initial_info, str)
    
    # After an API call
    model.generate("Hello, world!")
    formatted_info = model.format_usage_info()
    
    assert isinstance(formatted_info, str)
    assert "Model: gpt-4" in formatted_info
    assert "Input tokens:" in formatted_info
    assert "Output tokens:" in formatted_info
    assert "Total tokens:" in formatted_info
    assert "Estimated cost:" in formatted_info


def test_caching_parameter(mock_openai_client):
    """Test that the enable_cache parameter works correctly."""
    model = OpenAIModel(api_key="test_key", model="gpt-4")
    
    # Test with caching enabled (default)
    model.generate("Hello, world!")
    assert "cache_id" in mock_openai_client.return_value.chat.completions.create.call_args[1]
    
    # Test with caching disabled
    mock_openai_client.reset_mock()
    model.generate("Hello, world!", enable_cache=False)
    assert "cache_id" not in mock_openai_client.return_value.chat.completions.create.call_args[1]
