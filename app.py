"""
Streamlit UI for EI-harness-lite.
"""

import streamlit as st
import os
import json
from dotenv import load_dotenv

from ei_harness import EIHarness
from ei_harness.utils.prompt_loader import DEFAULT_PROMPT_URL
from ei_harness.utils.token_counter import MODEL_PRICING, MODEL_CONTEXT_WINDOW

# Load environment variables from .env file if it exists
load_dotenv()

# Set page title and description
st.set_page_config(
    page_title="EI-harness-lite",
    page_icon="🧠",
    layout="wide",
)

st.title("EI-harness-lite")
st.markdown(
    """
    A lightweight harness for using the MHH EI superprompt with various LLMs.
    
    This application loads the superprompt from:
    [MHH EI for AI](https://github.com/MindHackingHappiness/MHH-EI-for-AI-Language-Enabled-Emotional-Intelligence-and-Theory-of-Mind-Algorithms)
    """
)

# Sidebar for model selection and API key
with st.sidebar:
    st.header("Model Settings")
    
    # Model provider selection
    model_provider = st.selectbox(
        "Select Model Provider",
        ["OpenAI"],  # Add more as they're implemented
        index=0,
    )
    
    # Model name selection based on provider
    if model_provider == "OpenAI":
        model_options = list(MODEL_PRICING.keys())
        model_name = st.selectbox(
            "Select Model",
            model_options,
            index=model_options.index("gpt-4") if "gpt-4" in model_options else 0,
            help="Different models have different capabilities, token limits, and pricing."
        )
        
        # Show model information
        if model_name in MODEL_PRICING:
            st.info(
                f"**{model_name}**\n\n"
                f"Input: ${MODEL_PRICING[model_name]['input']*1000:.4f} per 1K tokens\n"
                f"Output: ${MODEL_PRICING[model_name]['output']*1000:.4f} per 1K tokens\n"
                f"Context window: {MODEL_CONTEXT_WINDOW.get(model_name, 'Unknown'):,} tokens"
            )
    
    # API key input
    api_key = st.text_input(
        f"{model_provider} API Key",
        value=os.getenv(f"{model_provider.upper()}_API_KEY", ""),
        type="password",
        help=f"Enter your {model_provider} API key. This is not stored anywhere.",
    )
    
    # Advanced settings
    st.header("Advanced Settings")
    
    # Custom prompt URL (optional)
    custom_url = st.text_input(
        "Custom Prompt URL (optional)",
        value=DEFAULT_PROMPT_URL,
        help="Enter a custom URL to load the prompt from.",
    )
    
    # Caching option
    enable_cache = st.checkbox(
        "Enable API-level caching",
        value=True,
        help="When enabled, OpenAI will apply a 50% discount on input tokens for identical prompts within an hour."
    )
    
    # Usage metrics expander
    with st.expander("Usage Metrics", expanded=False):
        if "usage_info" in st.session_state and st.session_state.usage_info:
            usage = st.session_state.usage_info
            
            st.markdown("### Last Request")
            
            # Format cached status
            cached_status = "🔄 CACHED (50% discount on input tokens)" if usage.get("cached", False) else "🆕 Not cached"
            st.markdown(f"**Cache Status**: {cached_status}")
            
            # Token usage
            if "usage" in usage:
                st.markdown("**Token Usage**:")
                st.markdown(f"- Input tokens: {usage['usage']['prompt_tokens']:,}")
                st.markdown(f"- Output tokens: {usage['usage']['completion_tokens']:,}")
                st.markdown(f"- Total tokens: {usage['usage']['total_tokens']:,}")
            
            # Cost information
            if "cost" in usage:
                st.markdown("**Cost Estimate**:")
                input_cost = usage["cost"]["input_cost"]
                output_cost = usage["cost"]["output_cost"]
                total_cost = usage["cost"]["total_cost"]
                
                st.markdown(f"- Input cost: ${input_cost:.6f}")
                st.markdown(f"- Output cost: ${output_cost:.6f}")
                st.markdown(f"- **Total cost: ${total_cost:.6f}**")
        else:
            st.markdown("No usage data available yet.")

# Main content area
st.header("Chat")

# Initialize session state
if "messages" not in st.session_state:
    st.session_state.messages = []
if "harness" not in st.session_state:
    st.session_state.harness = None
if "superprompt_loaded" not in st.session_state:
    st.session_state.superprompt_loaded = False
if "usage_info" not in st.session_state:
    st.session_state.usage_info = None

# Display chat history
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# User input
user_input = st.chat_input("Your message:")

if user_input:
    # Add user message to chat history
    st.session_state.messages.append({"role": "user", "content": user_input})
    
    # Display user message
    with st.chat_message("user"):
        st.markdown(user_input)
    
    # Check if API key is provided
    if not api_key:
        with st.chat_message("assistant"):
            st.error("Please enter your API key in the sidebar.")
    else:
        # Initialize EI harness if not already initialized or if settings changed
        if (st.session_state.harness is None or 
            st.session_state.harness.model_name != model_name or
            st.session_state.harness.prompt_url != (custom_url if custom_url != DEFAULT_PROMPT_URL else DEFAULT_PROMPT_URL) or
            st.session_state.harness.enable_cache != enable_cache):
            
            st.session_state.harness = EIHarness(
                model_provider=model_provider.lower(),
                api_key=api_key,
                model_name=model_name,
                prompt_url=custom_url if custom_url != DEFAULT_PROMPT_URL else None,
                enable_cache=enable_cache,
                verbose=False,  # Don't print to console in Streamlit
            )
            st.session_state.superprompt_loaded = False
        
        # Generate response
        with st.chat_message("assistant"):
            with st.spinner("Loading superprompt..." if not st.session_state.superprompt_loaded else "Generating response..."):
                try:
                    # Load superprompt if not already loaded
                    if not st.session_state.superprompt_loaded:
                        st.session_state.harness.load_prompt()
                        st.session_state.superprompt_loaded = True
                        
                        # Show superprompt info
                        superprompt_tokens = st.session_state.harness.superprompt_tokens
                        st.info(f"Superprompt loaded: {superprompt_tokens:,} tokens")
                    
                    # Generate response
                    response = st.session_state.harness.generate(user_input)
                    
                    # Store usage info
                    st.session_state.usage_info = st.session_state.harness.get_usage_info()
                    
                    # Display response
                    st.markdown(response)
                    
                    # Add assistant message to chat history
                    st.session_state.messages.append({"role": "assistant", "content": response})
                    
                    # Show usage information
                    if st.session_state.usage_info:
                        usage = st.session_state.usage_info
                        if "cost" in usage and "usage" in usage:
                            cached_str = " (CACHED: 50% discount applied)" if usage.get("cached", False) else ""
                            cost_str = f"${usage['cost']['total_cost']:.6f}"
                            tokens_str = f"{usage['usage']['total_tokens']:,} tokens"
                            
                            st.caption(f"Cost: {cost_str} | {tokens_str}{cached_str}")
                except Exception as e:
                    st.error(f"Error: {str(e)}")

# Footer
st.markdown("---")
st.markdown(
    """
    <div style="text-align: center">
        <p>EI-harness-lite | <a href="https://github.com/MindHackingHappiness/MHH-EI-for-AI-Language-Enabled-Emotional-Intelligence-and-Theory-of-Mind-Algorithms">MHH EI for AI</a></p>
    </div>
    """,
    unsafe_allow_html=True,
)
