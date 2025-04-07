import os
from dotenv import load_dotenv
import streamlit as st
from ei_harness import EIHarness
from ei_harness.utils.color import info, success, warning, error
import random # Keep random import

# Load environment variables from .env
load_dotenv()

# Configuration: Set available models (using stable version for context caching)
AVAILABLE_MODELS = ["gemini-2.0-flash-001"]

# --- init_harness, update_conversation_history, display_conversation_history (Keep as they were) ---
def init_harness(model_name, api_key):
    try:
        harness = EIHarness(
            model_provider="gemini",
            api_key=api_key,
            model_name=model_name,
            enable_cache=True,
            verbose=True
        )
        return harness
    except Exception as e:
        st.error(f"Failed to initialize EIHarness: {e}")
        return None

def update_conversation_history(prompt, response):
    if "conversation_history" not in st.session_state:
        st.session_state.conversation_history = []
    st.session_state.conversation_history.append({"prompt": prompt, "response": response})
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
            col1, col2, col3 = st.columns(3)
            if col1.button("👍", key=f"up_{idx}"): st.success("Thanks!")
            if col2.button("👎", key=f"down_{idx}"): st.error("Thanks!")
            col3.download_button("📋 Copy", data=turn['response'], file_name=f"response_round_{idx}.txt", mime="text/plain")
            st.markdown("---")
# --- End of helper functions ---

def main():
    st.title("Gemini Vision Demo (UI Screenshot Version)")
    st.markdown("""
    Displaying image gallery UI for screenshot purposes. **Analysis generation is disabled due to import errors.**
    """)

    # Inject custom CSS
    st.markdown(
        """
        <style>
        body { background-color: #F0F8FF; color: #333333; }
        .stButton>button { background-color: #4CAF50; color: white; border: none; padding: 10px 24px; text-align: center; display: inline-block; font-size: 16px; margin: 4px 2px; cursor: pointer; border-radius: 8px; }
        </style>
        """, unsafe_allow_html=True
    )

    # Sidebar settings (keep minimal for screenshot focus)
    st.sidebar.header("Configuration")
    selected_model = st.sidebar.selectbox("Model (Not Used)", AVAILABLE_MODELS)
    api_key = os.getenv("GEMINI_API_KEY") # Still needed for harness init maybe
    # harness = init_harness(selected_model, api_key) # Comment out harness init if it causes import cascade

    # --- Image Gallery and Selection ---
    st.markdown("### Select an Artwork for Analysis")
    image_dir = os.path.join("docs", "images", "Art")
    supported_formats = ('.jpg', '.jpeg', '.png')
    try:
        image_files = [f for f in os.listdir(image_dir) if os.path.isfile(os.path.join(image_dir, f)) and f.lower().endswith(supported_formats)]
    except FileNotFoundError:
        st.error(f"Image directory not found: {image_dir}")
        image_files = []

    if not image_files:
        st.warning("No images found in the specified directory.")
        return

    if "selected_image_path" not in st.session_state:
        st.session_state.selected_image_path = os.path.join(image_dir, image_files[0])

    cols_per_row = 5
    cols = st.columns(cols_per_row)
    for i, img_file in enumerate(image_files):
        col_index = i % cols_per_row
        full_path = os.path.join(image_dir, img_file)
        with cols[col_index]:
            st.image(full_path, width=100, caption=img_file[:15] + "...")
            if st.button("Select", key=f"select_{img_file}"):
                st.session_state.selected_image_path = full_path
                st.rerun()

    st.markdown("---")

    # --- Display Selected Image and Analysis Area ---
    st.markdown("### Selected Artwork")
    selected_image_path = st.session_state.selected_image_path
    st.image(selected_image_path, use_column_width=True)

    # Input area for prompt
    prompt = st.text_area("Enter your analysis prompt", "Provide an insightful and emotionally intelligent analysis of this artwork, rivaling human expertise.")

    if st.button("Generate Analysis"):
        # --- DISABLED ANALYSIS LOGIC ---
        st.info("Analysis generation is currently disabled due to import errors.")
        st.warning("Cannot generate response. Please wait for library fix.")
        # --- ORIGINAL LOGIC (COMMENTED OUT) ---
        # if not prompt:
        #     st.warning("Please enter a prompt before generating analysis.")
        # elif not selected_image_path:
        #      st.warning("Please select an image first.")
        # else:
        #     temperature = round(random.uniform(0.61, 0.82), 2)
        #     max_tokens = 8000
        #     with st.spinner("Generating analysis..."):
        #         # Combine conversation history... (keep if needed for UI)
        #         # Load and encode image... (keep if needed for UI)
        #         try:
        #             # --- THIS LINE WOULD CAUSE THE IMPORT ERROR ---
        #             # response = harness.generate(prompt=combined_prompt, image_data=image_data, temperature=temperature, max_output_tokens=max_tokens) 
        #             st.markdown("### Generation Response:")
        #             st.write("--- Analysis generation disabled ---") # Placeholder
        #             # Display generation parameters...
        #             # update_conversation_history(...)
        #             # Display feedback buttons...
        #         except Exception as e:
        #             st.error(f"Error during generation: {e}")
        # --- END OF DISABLED LOGIC ---

    st.markdown("---")
    st.markdown("This beta demo shows the UI layout. Generation is disabled.")

    # Display conversation history (optional for screenshot)
    # display_conversation_history() 
    # st.markdown("---")
    # if st.button("Clear Conversation History"):
    #     st.session_state.conversation_history = []
    #     st.rerun()

if __name__ == "__main__":
    main()
