"""
Streamlit UI for EI-harness-lite.
"""

import streamlit as st
import os
import json
from dotenv import load_dotenv

from ei_harness import EIHarness
from ei_harness.utils.prompt_loader import DEFAULT_PROMPT_URL
from ei_harness.utils.model_info import PROVIDER_DOCS, MODEL_PRICING, MODEL_CONTEXT_WINDOW, PROVIDER_CACHING, PROVIDER_MODELS

# Load environment variables from .env file if it exists
load_dotenv()

# Initialize session state
if "messages" not in st.session_state:
    st.session_state.messages = []
if "harness" not in st.session_state:
    st.session_state.harness = None
if "superprompt_loaded" not in st.session_state:
    st.session_state.superprompt_loaded = False
if "usage_info" not in st.session_state:
    st.session_state.usage_info = None
if "superprompt_text" not in st.session_state:
    st.session_state.superprompt_text = ""
if "edited_superprompt" not in st.session_state:
    st.session_state.edited_superprompt = ""
if "superprompt_token_count" not in st.session_state:
    st.session_state.superprompt_token_count = 0

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
    provider_options = list(PROVIDER_MODELS.keys())
    provider_options = [p.capitalize() for p in provider_options]  # Capitalize for display
    
    model_provider = st.selectbox(
        "Select Model Provider",
        provider_options,
        index=0,
    )
    
    # Model name selection based on provider
    provider_key = model_provider.lower()
    if provider_key in PROVIDER_MODELS:
        model_options = PROVIDER_MODELS[provider_key]
        default_index = 0
        
        # Set default model for each provider
        if provider_key == "openai" and "gpt-4" in model_options:
            default_index = model_options.index("gpt-4")
        elif provider_key == "anthropic" and "claude-3-sonnet" in model_options:
            default_index = model_options.index("claude-3-sonnet")
        elif provider_key == "gemini" and "gemini-1.5-flash" in model_options:
            default_index = model_options.index("gemini-1.5-flash")
        elif provider_key == "groq" and "llama3-70b-8192" in model_options:
            default_index = model_options.index("llama3-70b-8192")
        
        model_name = st.selectbox(
            "Select Model",
            model_options,
            index=default_index,
            help="Different models have different capabilities, token limits, and pricing."
        )
        
        # Provider-specific configuration
        if provider_key in ["ollama", "llamacpp", "vllm"]:
            from ei_harness.utils.model_info import LOCAL_PROVIDER_CONFIG
            if provider_key in LOCAL_PROVIDER_CONFIG:
                config = LOCAL_PROVIDER_CONFIG[provider_key]
                
                # Endpoint configuration for local models
                endpoint = st.text_input(
                    f"{model_provider} Endpoint",
                    value=config["endpoint"],
                    help=f"Enter the endpoint URL for your {model_provider} server."
                )
                
                # Add temperature slider for local models
                if "temperature" in config["config_options"]:
                    temperature = st.slider(
                        "Temperature",
                        min_value=0.0,
                        max_value=1.0,
                        value=0.7,
                        step=0.1,
                        help="Higher values make output more random, lower values more deterministic."
                    )
        
        # Show model information
        if model_name in MODEL_PRICING:
            st.info(
                f"**{model_name}**\n\n"
                f"Input: ${MODEL_PRICING[model_name]['input']*1000:.4f} per 1K tokens\n"
                f"Output: ${MODEL_PRICING[model_name]['output']*1000:.4f} per 1K tokens\n"
                f"Context window: {MODEL_CONTEXT_WINDOW.get(model_name, 'Unknown'):,} tokens"
            )
        
        # Show caching information
        provider_key = model_provider.lower()
        
        if provider_key in PROVIDER_CACHING:
            caching_info = PROVIDER_CACHING[provider_key]
            
            if caching_info["supports_caching"]:
                # Make caching info more prominent
                st.success(f"### Caching Available\n\n{caching_info['description']}\n\n"
                          f"Discount: {int(caching_info['discount'] * 100)}% off input tokens")
        
        # Show documentation link
        if model_provider.lower() in PROVIDER_DOCS:
            st.markdown(f"[{model_provider} Documentation]({PROVIDER_DOCS[model_provider.lower()]})")
    
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
    
    # Caching section
    st.header("Caching Settings")
    
    # Get caching info for the selected provider
    provider_key = model_provider.lower()
    caching_info = PROVIDER_CACHING.get(provider_key, {"supports_caching": False, "discount": 0, "description": "No caching available"})
    
    # Display caching status
    if caching_info["supports_caching"]:
        st.success(f"✅ Caching Available for {model_provider}")
        
        # Show caching details
        st.markdown(f"**Discount:** {int(caching_info['discount'] * 100)}% off input tokens")
        st.markdown(f"**Details:** {caching_info['description']}")
        
        # Cache control options
        enable_cache = st.checkbox(
            "Enable API-level caching",
            value=True,
            help="Turn caching on/off for this session"
        )
        
        # Cache statistics if available
        if "usage_info" in st.session_state and st.session_state.usage_info:
            usage = st.session_state.usage_info
            if usage.get("cached", False):
                # Calculate savings
                prompt_tokens = usage["usage"]["prompt_tokens"]
                input_cost = MODEL_PRICING.get(model_name, {"input": 0})["input"]
                savings = prompt_tokens * input_cost * caching_info["discount"]
                
                # Display cache hit information
                st.info(f"💰 Last request was cached, saving approximately ${savings:.6f}")
    else:
        st.warning(f"⚠️ {model_provider} does not support caching")
        st.markdown(f"**Details:** {caching_info['description']}")
        enable_cache = False
        
    # Add a clear cache button for providers that support caching
    if caching_info["supports_caching"]:
        if st.button("Clear Cache"):
            # This is just a placeholder - in a real implementation, you would clear the cache
            st.session_state.harness = None  # Force recreation of the harness
            st.success("Cache cleared successfully!")
    
    # Usage metrics expander
    with st.expander("Usage Metrics", expanded=False):
        if "usage_info" in st.session_state and st.session_state.usage_info:
            usage = st.session_state.usage_info
            
            st.markdown("### Last Request")
            
            # Format cached status
            cached_status = "🆕 Not cached"
            if usage.get("cached", False):
                provider = usage.get("model_provider", "openai").lower()
                discount = "50%"  # Default discount
                if provider in PROVIDER_CACHING:
                    discount = f"{int(PROVIDER_CACHING[provider]['discount'] * 100)}%"
                cached_status = f"🔄 CACHED ({discount} discount on input tokens)"
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

# Create tabs for Chat and Superprompt Editor
chat_tab, prompt_tab = st.tabs(["Chat", "Superprompt Editor"])

# Main chat area
with chat_tab:
    st.header("Chat")

# Superprompt editor area
with prompt_tab:
    st.header("Superprompt Editor")
    
    # Function to load superprompt from URL
    def load_superprompt():
        from ei_harness.utils.prompt_loader import load_prompt_from_url
        from ei_harness.utils.token_counter import count_tokens
        
        url = custom_url if custom_url != DEFAULT_PROMPT_URL else DEFAULT_PROMPT_URL
        try:
            st.session_state.superprompt_text = load_prompt_from_url(url)
            if not st.session_state.edited_superprompt:
                st.session_state.edited_superprompt = st.session_state.superprompt_text
            
            # Count tokens
            if model_name:
                st.session_state.superprompt_token_count = count_tokens(st.session_state.superprompt_text, model_name)
            return True
        except Exception as e:
            st.error(f"Error loading superprompt: {str(e)}")
            return False
    
    # Function to split prompt into sections
    def split_prompt_into_sections(prompt_text):
        sections = {}
        
        # Try to find the main sections
        lines = prompt_text.split('\n')
        
        # Initialize section boundaries
        copyright_end = 9   # Default
        title_end = 15      # Default
        foreword_end = 47   # Default
        instructions_start = 50  # Default
        
        # Find the exact "Instructions to the LLM:" line
        for i, line in enumerate(lines):
            if "Instructions to the LLM:" in line:
                instructions_start = i
                # Look for the separator line before instructions
                for j in range(i-1, i-5, -1):
                    if j >= 0 and "—" in lines[j]:
                        foreword_end = j - 1
                        break
                break
        
        # Find copyright section end (look for blank line after copyright)
        for i in range(5, 15):
            if i < len(lines) and lines[i].strip() == "":
                copyright_end = i
                break
        
        # Find title section end (look for "Foreword" or blank line)
        for i in range(copyright_end + 1, copyright_end + 10):
            if i < len(lines) and (lines[i].strip() == "Foreword" or lines[i].strip() == ""):
                title_end = i
                break
        
        # Create sections with better boundaries
        sections["copyright"] = "\n".join(lines[:copyright_end])
        sections["title"] = "\n".join(lines[copyright_end:title_end])
        sections["foreword"] = "\n".join(lines[title_end:foreword_end])
        sections["instructions"] = "\n".join(lines[instructions_start:])
        
        return sections
    
    # Load superprompt button
    if st.button("Load Superprompt from URL"):
        with st.spinner("Loading superprompt..."):
            success = load_superprompt()
            if success:
                # Update prompt sections
                st.session_state.prompt_sections = split_prompt_into_sections(st.session_state.superprompt_text)
                st.success(f"Superprompt loaded successfully! ({st.session_state.superprompt_token_count:,} tokens)")
    
    # If superprompt is not loaded yet, try to load it
    if not st.session_state.superprompt_text:
        with st.spinner("Loading superprompt..."):
            if load_superprompt():
                # Update prompt sections
                st.session_state.prompt_sections = split_prompt_into_sections(st.session_state.superprompt_text)
    
    # Display token count
    if st.session_state.superprompt_token_count > 0:
        st.info(f"Current superprompt size: {st.session_state.superprompt_token_count:,} tokens")
        
        # Context window warning
        if model_name and model_name in MODEL_CONTEXT_WINDOW:
            context_window = MODEL_CONTEXT_WINDOW[model_name]
            if st.session_state.superprompt_token_count > context_window * 0.9:
                st.warning(f"⚠️ Superprompt is using over 90% of the context window for {model_name}!")
            elif st.session_state.superprompt_token_count > context_window * 0.7:
                st.warning(f"⚠️ Superprompt is using over 70% of the context window for {model_name}.")
    
    # Add tabs for different editing modes
    edit_tab, sections_tab = st.tabs(["Full Editor", "Quick Edit"])
    
    with edit_tab:
        # Text editor for the superprompt
        st.text_area(
            "Edit Superprompt",
            value=st.session_state.edited_superprompt,
            height=500,
            key="superprompt_editor",
            help="Edit the superprompt directly. Changes will be applied when you click 'Apply Changes'."
        )
        
        # Update edited superprompt when text area changes
        st.session_state.edited_superprompt = st.session_state.superprompt_editor
    
    with sections_tab:
        st.markdown("### Prompt Sections")
        
        # Initialize sections in session state if not present
        if "prompt_sections" not in st.session_state and st.session_state.superprompt_text:
            st.session_state.prompt_sections = split_prompt_into_sections(st.session_state.superprompt_text)
        
        # Display sections as expandable areas
        if "prompt_sections" in st.session_state:
            sections = st.session_state.prompt_sections
            
            with st.expander("Copyright and License", expanded=False):
                sections["copyright"] = st.text_area(
                    "Edit Copyright Section",
                    value=sections["copyright"],
                    height=150
                )
            
            with st.expander("Title and Author", expanded=False):
                sections["title"] = st.text_area(
                    "Edit Title Section",
                    value=sections["title"],
                    height=150
                )
            
            with st.expander("Foreword", expanded=False):
                sections["foreword"] = st.text_area(
                    "Edit Foreword Section",
                    value=sections["foreword"],
                    height=300
                )
            
            with st.expander("Instructions to the LLM (Main Content)", expanded=True):
                sections["instructions"] = st.text_area(
                    "Edit Instructions Section",
                    value=sections["instructions"],
                    height=400
                )
            
            # Button to apply section changes
            if st.button("Apply Section Changes", type="primary"):
                # Combine sections back into full prompt
                combined_prompt = f"{sections['copyright']}\n\n{sections['title']}\n\n{sections['foreword']}\n\n{sections['instructions']}"
                
                # Update edited superprompt
                st.session_state.edited_superprompt = combined_prompt
                st.session_state.superprompt_editor = combined_prompt
                
                # Count tokens
                if model_name:
                    from ei_harness.utils.token_counter import count_tokens
                    token_count = count_tokens(combined_prompt, model_name)
                    st.session_state.superprompt_token_count = token_count
                    
                st.success(f"Section changes applied! New token count: {token_count:,}")
                
                # Reset the harness to use the new superprompt
                st.session_state.harness = None
                st.session_state.superprompt_loaded = False
        
        st.markdown("---")
        st.markdown("### Quick Edits")
        
        # Initialize custom message in session state if not present
        if "custom_message" not in st.session_state:
            st.session_state.custom_message = "This prompt enhances the model's capabilities for this specific task."
        
        # Custom message input
        custom_message = st.text_area(
            "Custom Message",
            value=st.session_state.custom_message,
            height=100,
            help="Add a custom message to the superprompt. This will be added at the end of the superprompt."
        )
        
        # Update custom message in session state
        st.session_state.custom_message = custom_message
        
        # Button to add custom message to superprompt
        if st.button("Add Custom Message to Superprompt"):
            # Add custom message to the end of the superprompt
            if st.session_state.superprompt_text:
                st.session_state.edited_superprompt = st.session_state.superprompt_text + "\n\n" + custom_message
                st.session_state.superprompt_editor = st.session_state.edited_superprompt
                
                # Count tokens
                if model_name:
                    from ei_harness.utils.token_counter import count_tokens
                    token_count = count_tokens(st.session_state.edited_superprompt, model_name)
                    st.session_state.superprompt_token_count = token_count
                    
                st.success(f"Custom message added to superprompt! New token count: {token_count:,}")
                
                # Reset the harness to use the new superprompt
                st.session_state.harness = None
                st.session_state.superprompt_loaded = False
    
    # Buttons for applying changes or resetting
    col1, col2 = st.columns(2)
    with col1:
        if st.button("Apply Changes", type="primary"):
            # Count tokens in edited superprompt
            if model_name:
                token_count = count_tokens(st.session_state.edited_superprompt, model_name)
                st.session_state.superprompt_token_count = token_count
                st.success(f"Changes applied! New token count: {token_count:,}")
                
                # Reset the harness to use the new superprompt
                st.session_state.harness = None
                st.session_state.superprompt_loaded = False
    
    with col2:
        if st.button("Reset to Original"):
            st.session_state.edited_superprompt = st.session_state.superprompt_text
            st.session_state.superprompt_editor = st.session_state.superprompt_text
            st.info("Reset to original superprompt.")

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
            
            # Use edited superprompt if available and Apply Changes was clicked
            custom_prompt = None
            if "edited_superprompt" in st.session_state and st.session_state.edited_superprompt:
                custom_prompt = st.session_state.edited_superprompt
            
            # Prepare additional configuration for local models
            additional_config = {}
            if provider_key in ["ollama", "llamacpp", "vllm"]:
                # Add endpoint configuration
                if 'endpoint' in locals():
                    additional_config["endpoint"] = endpoint
                
                # Add temperature if available
                if 'temperature' in locals():
                    additional_config["temperature"] = temperature
            
            st.session_state.harness = EIHarness(
                model_provider=model_provider.lower(),
                api_key=api_key,
                model_name=model_name,
                prompt_url=custom_url if custom_url != DEFAULT_PROMPT_URL else None,
                custom_prompt_text=custom_prompt,
                enable_cache=enable_cache,
                verbose=False,  # Don't print to console in Streamlit
                **additional_config  # Add any provider-specific configuration
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
                            cached_str = ""
                            if usage.get("cached", False):
                                provider = usage.get("model_provider", "openai").lower()
                                discount = "50%"  # Default discount
                                if provider in PROVIDER_CACHING:
                                    discount = f"{int(PROVIDER_CACHING[provider]['discount'] * 100)}%"
                                cached_str = f" (CACHED: {discount} discount applied)"
                            
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
