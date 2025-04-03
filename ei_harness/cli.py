"""
Command-line interface for EI-harness-lite.
"""

import argparse
import os
import sys
from typing import List, Optional

from dotenv import load_dotenv

from .ei_harness import EIHarness
from .utils.prompt_loader import DEFAULT_PROMPT_URL
from .utils.color import info, warning, error, success, bold, dim


def parse_args(args: Optional[List[str]] = None) -> argparse.Namespace:
    """
    Parse command-line arguments.
    
    Args:
        args: Command-line arguments. If None, uses sys.argv.
        
    Returns:
        Parsed arguments.
    """
    parser = argparse.ArgumentParser(
        description="EI-harness-lite: A lightweight harness for using the MHH EI superprompt with various LLMs."
    )
    
    parser.add_argument(
        "prompt",
        nargs="?",
        help="Prompt to send to the model. If not provided, enters interactive mode.",
    )
    
    parser.add_argument(
        "--model-provider",
        "-p",
        choices=["openai"],  # Add more as they're implemented
        default="openai",
        help="Model provider to use. Default: openai",
    )
    
    parser.add_argument(
        "--model",
        "-m",
        default="gpt-4",
        help="Model name to use. Default: gpt-4",
    )
    
    parser.add_argument(
        "--api-key",
        "-k",
        help="API key for the model provider. If not provided, looks for environment variable.",
    )
    
    parser.add_argument(
        "--prompt-url",
        "-u",
        default=DEFAULT_PROMPT_URL,
        help=f"URL to load the superprompt from. Default: {DEFAULT_PROMPT_URL}",
    )
    
    parser.add_argument(
        "--no-cache",
        action="store_true",
        help="Disable OpenAI's API-level caching (no 50% discount on input tokens).",
    )
    
    parser.add_argument(
        "--quiet",
        "-q",
        action="store_true",
        help="Suppress token count and cost information.",
    )
    
    return parser.parse_args(args)


def main(args: Optional[List[str]] = None) -> int:
    """
    Main entry point for the CLI.
    
    Args:
        args: Command-line arguments. If None, uses sys.argv.
        
    Returns:
        Exit code.
    """
    # Load environment variables from .env file if it exists
    load_dotenv()
    
    # Parse arguments
    parsed_args = parse_args(args)
    
    # Get API key from arguments or environment
    api_key = parsed_args.api_key
    if not api_key:
        env_var = f"{parsed_args.model_provider.upper()}_API_KEY"
        api_key = os.getenv(env_var)
        if not api_key:
            print(error(f"Error: No API key provided. Please provide an API key with --api-key or set the {env_var} environment variable."))
            return 1
    
    # Initialize EI harness
    harness = EIHarness(
        model_provider=parsed_args.model_provider,
        api_key=api_key,
        model_name=parsed_args.model,
        prompt_url=parsed_args.prompt_url if parsed_args.prompt_url != DEFAULT_PROMPT_URL else None,
        enable_cache=not parsed_args.no_cache,
        verbose=not parsed_args.quiet,
    )
    
    # Load the superprompt
    try:
        if parsed_args.quiet:
            print("Loading superprompt...")
        harness.load_prompt()
        if parsed_args.quiet:
            print(success("Superprompt loaded successfully."))
    except Exception as e:
        print(error(f"Error loading superprompt: {e}"))
        return 1
    
    # Show cache status
    if not parsed_args.quiet and not parsed_args.no_cache:
        print(info("OpenAI API-level caching is enabled (50% discount on cached input tokens)."))
    elif not parsed_args.quiet and parsed_args.no_cache:
        print(warning("OpenAI API-level caching is disabled (no discount on input tokens)."))
    
    # Interactive mode or single prompt
    if parsed_args.prompt:
        # Single prompt mode
        try:
            print("\nGenerating response...")
            response = harness.generate(parsed_args.prompt)
            print("\n" + bold("Response:"))
            print(response)
        except Exception as e:
            print(error(f"Error generating response: {e}"))
            return 1
    else:
        # Interactive mode
        print("\n" + bold("Entering interactive mode. Type 'exit' or 'quit' to exit."))
        while True:
            try:
                user_input = input("\n" + bold("You: "))
                if user_input.lower() in ["exit", "quit"]:
                    break
                
                print("\nGenerating response...")
                response = harness.generate(user_input)
                print("\n" + bold("Assistant:"))
                print(response)
            except KeyboardInterrupt:
                print("\nExiting...")
                break
            except Exception as e:
                print(error(f"Error: {e}"))
    
    return 0


if __name__ == "__main__":
    sys.exit(main())
