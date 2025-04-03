"""
Test script for EI-harness-lite.
"""

import os
from dotenv import load_dotenv

from ei_harness import EIHarness
from ei_harness.utils.prompt_loader import load_prompt_from_url
from ei_harness.utils.token_counter import count_tokens, estimate_cost
from ei_harness.utils.color import info, success, warning, error, bold

# Load environment variables from .env file if it exists
load_dotenv()

def test_prompt_loader():
    """Test the prompt loader."""
    print(bold("Testing prompt loader..."))
    try:
        prompt = load_prompt_from_url()
        print(success(f"Successfully loaded prompt ({len(prompt)} characters)"))
        print(info(f"First 100 characters: {prompt[:100]}..."))
        
        # Count tokens
        tokens = count_tokens(prompt, "gpt-4")
        print(info(f"Token count: {tokens:,} tokens"))
        
        return True
    except Exception as e:
        print(error(f"Error loading prompt: {e}"))
        return False

def test_token_counter():
    """Test the token counter."""
    print(bold("\nTesting token counter..."))
    try:
        test_text = "This is a test sentence for token counting."
        tokens = count_tokens(test_text, "gpt-4")
        print(info(f"Text: '{test_text}'"))
        print(info(f"Token count: {tokens} tokens"))
        
        # Test cost estimation
        cost = estimate_cost("gpt-4", tokens, 20, False)
        print(info(f"Cost estimate (no cache): ${cost['total_cost']:.6f}"))
        
        cost_cached = estimate_cost("gpt-4", tokens, 20, True)
        print(info(f"Cost estimate (with cache): ${cost_cached['total_cost']:.6f}"))
        
        # Verify cache discount
        if cost_cached['input_cost'] == cost['input_cost'] * 0.5:
            print(success("Cache discount correctly applied (50% off input tokens)"))
        else:
            print(error("Cache discount not applied correctly"))
        
        return True
    except Exception as e:
        print(error(f"Error testing token counter: {e}"))
        return False

def test_harness():
    """Test the EI harness."""
    # Get API key from environment
    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key:
        print(error("Error: No API key provided. Please set the OPENAI_API_KEY environment variable."))
        return False
    
    print(bold("\nTesting EI harness..."))
    try:
        # Initialize harness
        harness = EIHarness(
            api_key=api_key,
            model_name="gpt-3.5-turbo",  # Use cheaper model for testing
            enable_cache=True,
            verbose=True
        )
        
        # Load prompt
        print("Loading prompt...")
        harness.load_prompt()
        print(success("Prompt loaded successfully."))
        
        # Check token count
        print(info(f"Superprompt token count: {harness.superprompt_tokens:,}"))
        
        # Generate response (commented out to avoid API charges)
        # print("Generating response...")
        # response = harness.generate("How are you feeling today?")
        # print(f"Response: {response}")
        # 
        # # Check usage info
        # usage_info = harness.get_usage_info()
        # print(info(f"Total tokens: {usage_info['usage']['total_tokens']:,}"))
        # print(info(f"Cached: {usage_info['cached']}"))
        # print(info(f"Cost: ${usage_info['cost']['total_cost']:.6f}"))
        
        return True
    except Exception as e:
        print(error(f"Error: {e}"))
        return False

if __name__ == "__main__":
    print(bold("=== EI-harness-lite Test ==="))
    
    # Test prompt loader
    prompt_loader_success = test_prompt_loader()
    
    # Test token counter
    token_counter_success = test_token_counter()
    
    # Test harness (if API key is available)
    if os.getenv("OPENAI_API_KEY"):
        harness_success = test_harness()
    else:
        print(warning("\nSkipping harness test (no API key)"))
        harness_success = None
    
    print()
    print(bold("=== Test Results ==="))
    print(f"Prompt Loader: {success('✓ PASS') if prompt_loader_success else error('✗ FAIL')}")
    print(f"Token Counter: {success('✓ PASS') if token_counter_success else error('✗ FAIL')}")
    if harness_success is not None:
        print(f"EI Harness: {success('✓ PASS') if harness_success else error('✗ FAIL')}")
    else:
        print(f"EI Harness: {warning('SKIPPED')}")
