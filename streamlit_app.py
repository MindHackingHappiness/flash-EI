import os
from dotenv import load_dotenv
import streamlit as st
from ei_harness import EIHarness
from ei_harness.utils.color import info, success, warning, error

# Load environment variables from .env
load_dotenv()

# Configuration: Set available models (using stable version for context caching)
AVAILABLE_MODELS = ["gemini-2.0-flash-001"]

def init_harness(model_name, api_key):
    try:
        harness = EIHarness(
            model_provider="gemini",
            api_key=api_key,
            model_name=model_name,
            enable_cache=True,
            verbose=True  # Enable verbose logging for beta transparency
        )
        return harness
    except Exception as e:
        st.error(f"Failed to initialize EIHarness: {e}")
        return None

def update_conversation_history(prompt, response):
    # Maintain conversation history in session state (last 5 rounds)
    if "conversation_history" not in st.session_state:
        st.session_state.conversation_history = []
    st.session_state.conversation_history.append({"prompt": prompt, "response": response})
    # Keep only the last 5 interactions
    st.session_state.conversation_history = st.session_state.conversation_history[-5:]

def display_conversation_history():
    st.markdown("### Conversation History (Last 5 rounds)")
    if "conversation_history" not in st.session_state or not st.session_state.conversation_history:
        st.info("No conversation history yet.")
    else:
        for idx, turn in enumerate(st.session_state.conversation_history, start=1):
            st.markdown(f"**Round {idx}**")
            st.markdown(f"**Prompt:** {turn['prompt']}")
            st.markdown(f"**Response:** {turn['response']}")
            # Feedback buttons for each round (non-functional placeholders)
            col1, col2, col3 = st.columns(3)
            if col1.button("👍", key=f"up_{idx}"):
                st.success("Thanks for your thumbs up!")
            if col2.button("👎", key=f"down_{idx}"):
                st.error("Thanks for your feedback!")
            # Quick copy button using download_button as a workaround
            col3.download_button("📋 Copy", data=turn['response'], file_name=f"response_round_{idx}.txt", mime="text/plain")
            st.markdown("---")

def main():
    st.title("Gemini API Context Caching Demo - Beta")
    st.markdown("""
    This demo shows how context caching works with the Gemini API via Vertex AI.
    **Beta Version** – All metrics, data, and logs are visible for full transparency.
    Select the model and enter your prompt below. The system will use context caching (if applicable)
    to reduce repeated tokens and lower cost, while retaining memory of your last 5 interactions.
    """)

    # Inject custom CSS for improved styling and contrast
    st.markdown(
        """
        <style>
        body {
            background-color: #F0F8FF; /* AliceBlue for a calm, clean background */
            color: #333333; /* Dark grey for clear readability */
        }
        .stButton>button {
            background-color: #4CAF50; /* Vibrant green for positivity and engagement */
            color: white;
            border: none;
            padding: 10px 24px;
            text-align: center;
            display: inline-block;
            font-size: 16px;
            margin: 4px 2px;
            cursor: pointer;
            border-radius: 8px;
        }
        </style>
        """,
        unsafe_allow_html=True
    )

    # Sidebar settings
    st.sidebar.header("Configuration")
    selected_model = st.sidebar.selectbox("Choose a Model", AVAILABLE_MODELS)
    
    # Retrieve GEMINI_API_KEY from environment
    api_key = os.getenv("GEMINI_API_KEY")
    if not api_key:
        st.error("GEMINI_API_KEY not set in environment. Please update your .env file.")
        return

    # Initialize harness using the selected model
    harness = init_harness(selected_model, api_key)
    if harness is None:
        return

    # Option to load superprompt (optional for verbose beta demo)
    if st.button("Load Superprompt"):
        try:
            harness.load_prompt()
            st.success(f"Superprompt loaded ({harness.superprompt_tokens} tokens).")
        except Exception as e:
            st.error(f"Failed to load superprompt: {e}")
            return

    # Input area for prompt
    prompt = st.text_area("Enter your prompt", "Explain the concept of in-memory caching for API calls briefly.")

    if st.button("Generate Response"):
        if not prompt:
            st.warning("Please enter a prompt before generating a response.")
        else:
            # Randomize temperature between 0.61 and 0.82 and set max output tokens to 8000
            import random
            temperature = round(random.uniform(0.61, 0.82), 2)
            max_tokens = 8000
            with st.spinner("Generating response..."):
                try:
                    # Combine conversation history to simulate multi-turn (5 roundtrip) memory
                    if "conversation_history" in st.session_state and st.session_state.conversation_history:
                        conversation_context = ""
                        for turn in st.session_state.conversation_history:
                            conversation_context += "User: " + turn["prompt"] + "\n"
                            conversation_context += "AI: " + turn["response"] + "\n"
                        combined_prompt = conversation_context + "User: " + prompt + "\nAI:"
                    else:
                        combined_prompt = prompt
                    response = harness.generate(prompt=combined_prompt, temperature=temperature, max_output_tokens=max_tokens)
                    st.markdown("### Generation Response:")
                    st.write(response)
                    
                    # Display generation parameters
                    st.markdown("### Generation Parameters:")
                    col1, col2 = st.columns(2)
                    col1.metric("Temperature", temperature)
                    col2.metric("Max Output Tokens", max_tokens)
                    
                    # Append current interaction to the conversation history
                    update_conversation_history(prompt, response)
                    
                    # Display additional feedback options below the response
                    st.markdown("---")
                    st.markdown("#### Your feedback on this response:")
                    col_up, col_down, col_copy = st.columns(3)
                    if col_up.button("👍"):
                        st.success("Thanks for your thumbs up!")
                    if col_down.button("👎"):
                        st.error("Thanks for your feedback!")
                    col_copy.download_button("📋 Copy Response", data=response, file_name="response.txt", mime="text/plain")
                except Exception as e:
                    st.error(f"Error during generation: {e}")

    st.markdown("---")
    st.markdown("This beta demo is fully verbose for transparency. All generated data, metrics, and logs are displayed below.")

    # Display conversation history with the last 5 rounds
    display_conversation_history()
    st.markdown("---")
    if st.button("Clear Conversation History"):
        st.session_state.conversation_history = []
        st.rerun() # Use correct rerun function

if __name__ == "__main__":
    main()
