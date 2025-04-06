# Product Context: EI-harness-lite

## Purpose

*   **Original Goal:** To provide a harness for running a large (170Kb) "EI_for_AI" superprompt.
*   **Evolved Goal:** To leverage the capabilities of Google's Gemini Flash 2.0 model, expanding beyond the initial superprompt focus. The project aims to be a demonstration platform for advanced AI features.
*   **Current Focus:** Integrate multi-modal features, starting with image generation, into a user-facing application. The project seeks to showcase the power and versatility of Gemini Flash 2.0.

## Problem Solved

*   Initially, it addressed the need to manage and execute a very large, specific prompt effectively.
*   Currently, it aims to solve the challenge of integrating and demonstrating cutting-edge multi-modal AI capabilities (like image generation) alongside complex text generation within a single, accessible application.

## Intended Functionality

*   **Core:** Interact with the Gemini Flash 2.0 API.
*   **Text Generation:** Execute the large "EI_for_AI" superprompt, handling potential complexities like caching and token limits.
*   **Image Generation:** Allow users to generate images based on prompts using Gemini Flash 2.0.
    *   *Initial Testing:* Command-line interface or script-based testing where images are saved to/read from the filesystem.
    *   *Target Implementation:* Integrate image generation directly into a Streamlit application, displaying generated images inline within the chat interface.
*   **Deployment:** The application (specifically the Streamlit component) is designed to be deployed to Google Cloud Platform using Cloud Build.
*   **Future:** Incorporate image analysis and emotive text-to-speech capabilities.
