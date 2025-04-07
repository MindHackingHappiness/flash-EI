#!/usr/bin/env python3
"""
Command-line script to test Gemini basic API calls and IN-MEMORY caching
functionality in EIHarness using the google-genai SDK.
"""

import os
import time
import sys
from dotenv import load_dotenv

# Add project root to path to allow importing ei_harness
# project_root = os.path.dirname(os.path.abspath(__file__))
# sys.path.insert(0, project_root) # Usually not needed if run from project root

try:
    from ei_harness import EIHarness
    # Import correct color functions
    from ei_harness.utils.color import info, success, warning, error, bold
except ImportError as e:
    print(f"Error importing EIHarness or color utils: {e}")
    print("Please ensure you are running this script from the project root directory")
    print("and that ei_harness is installed or available in the Python path.")
    sys.exit(1)

# --- Configuration ---
# Ensure you have a .env file with GEMINI_API_KEY
load_dotenv()

# Use user-preferred model. Context Caching is currently disabled in GeminiModel.
TEST_MODEL = "gemini-2.0-flash-001"
TEST_PROMPT_1 = "Explain the concept of in-memory caching for API calls briefly."
TEST_PROMPT_2 = "Now, explain the concept of in-memory caching in more detail."
# ---

def run_test():
    """Runs the in-memory caching tests."""

    api_key = os.environ.get("GEMINI_API_KEY")
    if not api_key:
        print(error("GEMINI_API_KEY not found in environment variables. Please set it in your .env file."))
        sys.exit(1)

    print(bold(f"--- Initializing EIHarness with Model: {TEST_MODEL} ---"))
    try:
        # enable_cache=True enables the simple in-memory cache in GeminiModel
        harness = EIHarness(
            model_provider="gemini",
            api_key=api_key,
            model_name=TEST_MODEL,
            enable_cache=True,
            verbose=False # We will print formatted info manually
        )
        print(success("EIHarness initialized successfully."))
    except Exception as e:
        print(error(f"Failed to initialize EIHarness: {e}"))
        sys.exit(1)

    print(bold("\n--- Loading Superprompt ---"))
    try:
        harness.load_prompt()
        print(info(f"Superprompt loaded ({harness.superprompt_tokens} tokens)."))
        # Note: Context Cache is disabled in the current GeminiModel implementation
        print(warning("Context Cache implementation is currently removed/disabled."))

    except Exception as e:
        print(error(f"Failed to load superprompt: {e}"))
        sys.exit(1)

    # --- Test 1: Identical Prompts (Testing In-Memory Cache) ---
    print(bold("\n--- Test 1: Sending Identical Prompts (Testing In-Memory Cache) ---"))
    print(info(f"Prompt: '{TEST_PROMPT_1}'"))

    try:
        print(info("\nSending first request..."))
        response1 = harness.generate(prompt=TEST_PROMPT_1)
        print(success("First response received."))
        print(info("--- Usage Info (Call 1) ---"))
        print(harness.model.format_usage_info())
        print("--------------------------")

        print(info("\nSending second request (identical)..."))
        response2 = harness.generate(prompt=TEST_PROMPT_1)
        print(success("Second response received."))
        print(info("--- Usage Info (Call 2) ---"))
        usage_info2 = harness.get_usage_info()
        print(harness.model.format_usage_info())
        # Check the 'cached' flag which indicates if IN-MEMORY cache was hit
        if usage_info2.get("cached"):
            print(success("✅ In-Memory Cache Hit Expected: Yes. Result: Cache Hit Reported!"))
        else:
            print(error("❌ In-Memory Cache Hit Expected: Yes. Result: Cache Miss Reported."))
        print("--------------------------")

    except Exception as e:
        print(error(f"Error during Test 1: {e}"))


    # --- Test 2: Different Prompt (Testing In-Memory Cache) ---
    print(bold("\n--- Test 2: Sending Different Prompt (Testing In-Memory Cache) ---"))
    print(info(f"Prompt: '{TEST_PROMPT_2}'"))

    try:
        print(info("\nSending third request (different)..."))
        response3 = harness.generate(prompt=TEST_PROMPT_2)
        print(success("Third response received."))
        print(info("--- Usage Info (Call 3) ---"))
        usage_info3 = harness.get_usage_info()
        print(harness.model.format_usage_info())
        # Check the 'cached' flag which indicates if IN-MEMORY cache was hit
        if not usage_info3.get("cached"):
            print(success("✅ In-Memory Cache Hit Expected: No. Result: Cache Miss Reported!"))
        else:
            print(error("❌ In-Memory Cache Hit Expected: No. Result: Cache Hit Reported."))
        print("--------------------------")

    except Exception as e:
        print(error(f"Error during Test 2: {e}"))

    # --- Test 3: Repeat First Prompt (Check In-Memory Cache Again) ---
    print(bold("\n--- Test 3: Repeating First Prompt (Check In-Memory Cache Again) ---"))

    try:
        # Note: Cache clearing for Context Cache was removed. This tests if in-memory cache persists.
        print(warning("Skipping cache clearing step (Context Cache implementation removed)."))

        print(info(f"\nSending first prompt again: '{TEST_PROMPT_1}'"))
        response4 = harness.generate(prompt=TEST_PROMPT_1)
        print(success("Fourth response received."))
        print(info("--- Usage Info (Call 4) ---"))
        usage_info4 = harness.get_usage_info()
        print(harness.model.format_usage_info())
        # We expect this to be an IN-MEMORY cache hit
        if usage_info4.get("cached"):
            print(success("✅ In-Memory Cache Hit Expected: Yes. Result: Cache Hit Reported!"))
        else:
            print(error("❌ In-Memory Cache Hit Expected: Yes. Result: Cache Miss Reported."))
        # Removed check for active_cache_name
        print("--------------------------")

    except Exception as e:
        print(error(f"Error during Test 3: {e}"))

    print(bold("\n--- Test Complete ---"))

if __name__ == "__main__":
    run_test()
