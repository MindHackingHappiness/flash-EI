# System Patterns: EI-harness-lite

## Architecture Overview

The system appears to follow a layered approach:

1.  **Core AI Interaction:** Logic for interacting with AI models (specifically Gemini) is encapsulated within the `ei_harness/models/` directory, particularly `gemini.py`. This likely handles API calls, request/response formatting, and potentially error handling related to the Gemini API.
2.  **Harness Utilities:** The `ei_harness/utils/` directory likely contains helper functions for tasks such as token counting (`token_counter.py`), prompt loading (`prompt_loader.py`), and potentially caching mechanisms needed for the large superprompt.
3.  **Application Interface:** A Streamlit application (`gemini_app.py`) provides the primary user interface for interacting with the system's capabilities (text generation, and planned image generation).
4.  **Command-Line/Scripting:** Various Python scripts (`.py`) and batch/shell scripts (`.bat`, `.sh`) exist for tasks like running the app (`run_gemini_app.*`), deployment (`deploy_gemini_to_gcp*`), environment setup (`setup_env.py`), and testing (`test_*.py`).
5.  **Testing:** A dedicated `tests/` directory contains unit and integration tests, with specific focus on the Gemini integration (`test_gemini*.py`). Pytest seems to be the testing framework (`pytest.ini`).
6.  **Deployment:** The system is designed for deployment to Google Cloud Platform (GCP) using Cloud Build. Configuration and steps are documented in markdown files (`DEPLOY_*.md`) and implemented via scripts. Docker (`Dockerfile`, `Dockerfile.gemini`, `.dockerignore*`, `docker-compose.yml`) is used for containerization, likely facilitating the Cloud Build process.
7.  **Configuration:** API keys and other sensitive settings are likely managed through environment variables, as indicated by `.env.example` and `.env.sample`.

## Key Technical Decisions (Inferred)

*   **Primary AI Model:** Google Gemini (specifically targeting Flash 2.0).
*   **Application Framework:** Streamlit for the user-facing web application.
*   **Deployment Platform:** Google Cloud Platform (GCP) via Cloud Build.
*   **Containerization:** Docker.
*   **Language:** Python.
*   **Testing Framework:** Pytest.
*   **Modularity:** Separation of concerns between core AI logic (`ei_harness/models`), utilities (`ei_harness/utils`), the application (`gemini_app.py`), and testing/deployment scripts.
*   **Context Caching (Gemini):** Implemented using the `google-genai` SDK's explicit Context Caching feature.
    *   `GeminiModel` manages cache creation (`client.caches.create`) for the `system_instruction` (superprompt) with a configurable TTL.
    *   Subsequent `generate_content` calls reference the created cache via `GenerationConfig(cached_content=...)`, sending only the user prompt/history.
    *   This aims to optimize costs for the large superprompt by leveraging Google's specialized caching.
