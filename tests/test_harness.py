"""
Tests for the main EIHarness class.
"""

import pytest
from unittest.mock import patch, MagicMock
from ei_harness import EIHarness
from ei_harness.models.openai import OpenAIModel


@pytest.fixture
def mock_prompt_loader():
    """Create a mock prompt loader."""
    with patch('ei_harness.utils.prompt_loader.load_prompt_from_url') as mock_loader:
        mock_loader.return_value = "This is a test superprompt."
        yield mock_loader


@pytest.fixture
def mock_openai_model():
    """Create a mock OpenAI model."""
    with patch('ei_harness.models.openai.OpenAIModel') as mock_model_class:
        mock_model = MagicMock()
        mock_model.generate.return_value = "Test response"
        mock_model.get_usage_info.return_value = {
            "usage": {
                "prompt_tokens": 10,
                "completion_tokens": 5,
                "total_tokens": 15
            },
            "cost": {
                "input_cost": 0.0003,
                "output_cost": 0.0001,
                "total_cost": 0.0004
            },
            "cached": False,
            "model": "gpt-4"
        }
        mock_model_class.return_value = mock_model
        yield mock_model_class, mock_model


def test_harness_initialization(mock_openai_model):
    """Test EIHarness initialization."""
    mock_model_class, _ = mock_openai_model
    
    # Test with default parameters
    harness = EIHarness(api_key="test_key")
    mock_model_class.assert_called_once_with("test_key", "gpt-4")
    
    # Check default values
    assert harness.prompt_url is not None
    assert harness.superprompt is None
    assert harness.superprompt_tokens == 0
    assert harness.enable_cache is True
    assert harness.verbose is True
    assert harness.model_name == "gpt-4"


def test_load_prompt(mock_prompt_loader, mock_openai_model):
    """Test the load_prompt method."""
    _, mock_model = mock_openai_model
    mock_model.model = "gpt-4"
    
    harness = EIHarness(api_key="test_key")
    result = harness.load_prompt()
    
    # Check that the prompt loader was called
    mock_prompt_loader.assert_called_once()
    
    # Check the result
    assert result == "This is a test superprompt."
    assert harness.superprompt == "This is a test superprompt."
    assert harness.superprompt_tokens > 0


def test_generate(mock_prompt_loader, mock_openai_model):
    """Test the generate method."""
    _, mock_model = mock_openai_model
    
    harness = EIHarness(api_key="test_key")
    
    # Test without loading prompt first
    response = harness.generate("Hello, world!")
    
    # Check that the prompt was loaded automatically
    assert harness.superprompt is not None
    
    # Check that the model's generate method was called with the correct parameters
    mock_model.generate.assert_called_once()
    args, kwargs = mock_model.generate.call_args
    assert "This is a test superprompt." in args[0]
    assert "Hello, world!" in args[0]
    assert kwargs["enable_cache"] is True
    
    # Check the response
    assert response == "Test response"


def test_get_usage_info(mock_prompt_loader, mock_openai_model):
    """Test the get_usage_info method."""
    _, mock_model = mock_openai_model
    
    harness = EIHarness(api_key="test_key")
    harness.load_prompt()
    harness.generate("Hello, world!")
    
    usage_info = harness.get_usage_info()
    
    # Check that the model's get_usage_info method was called
    mock_model.get_usage_info.assert_called_once()
    
    # Check the result
    assert "usage" in usage_info
    assert "cost" in usage_info
    assert "cached" in usage_info
    assert "model" in usage_info
    assert "superprompt_tokens" in usage_info
    assert "superprompt_url" in usage_info
    assert usage_info["superprompt_tokens"] > 0


def test_caching_parameter(mock_prompt_loader, mock_openai_model):
    """Test that the enable_cache parameter works correctly."""
    _, mock_model = mock_openai_model
    
    # Test with caching enabled (default)
    harness = EIHarness(api_key="test_key", enable_cache=True)
    harness.generate("Hello, world!")
    args, kwargs = mock_model.generate.call_args
    assert kwargs["enable_cache"] is True
    
    # Test with caching disabled
    mock_model.reset_mock()
    harness = EIHarness(api_key="test_key", enable_cache=False)
    harness.generate("Hello, world!")
    args, kwargs = mock_model.generate.call_args
    assert kwargs["enable_cache"] is False
    
    # Test overriding in generate method
    mock_model.reset_mock()
    harness = EIHarness(api_key="test_key", enable_cache=True)
    harness.generate("Hello, world!", enable_cache=False)
    args, kwargs = mock_model.generate.call_args
    assert kwargs["enable_cache"] is False
