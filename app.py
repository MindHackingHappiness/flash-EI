"""
Streamlit UI for EI-harness-lite.
"""

import streamlit as st
import os
from dotenv import load_dotenv

from ei_harness import EIHarness
from ei_harness.utils.prompt_loader import DEFAULT_PROMPT_URL

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
        model_name = st.selectbox(
            "Select Model",
            ["gpt-4", "gpt-3.5-turbo"],
            index=0,
        )
    
    # API key input
    api_key = st.text_input(
        f"{model_provider} API Key",
        value=os.getenv(f"{model_provider.upper()}_API_KEY", ""),
        type="password",
        help=f"Enter your {model_provider} API key. This is not stored anywhere.",
    )
    
    # Custom prompt URL (optional)
    st.header("Advanced Settings")
    custom_url = st.text_input(
        "Custom Prompt URL (optional)",
        value=DEFAULT_PROMPT_URL,
        help="Enter a custom URL to load the prompt from.",
    )

# Main content area
st.header("Chat")

# Initialize session state for chat history
if "messages" not in st.session_state:
    st.session_state.messages = []

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
        # Initialize EI harness
        harness = EIHarness(
            model_provider=model_provider.lower(),
            api_key=api_key,
            model_name=model_name,
            prompt_url=custom_url if custom_url != DEFAULT_PROMPT_URL else None,
        )
        
        # Generate response
        with st.chat_message("assistant"):
            with st.spinner("Thinking..."):
                try:
                    response = harness.generate(user_input)
                    st.markdown(response)
                    
                    # Add assistant message to chat history
                    st.session_state.messages.append({"role": "assistant", "content": response})
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
