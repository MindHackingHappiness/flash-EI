# Technical Context: EI-harness-lite

## Core Technologies

*   **Programming Language:** Python (primary, used for backend logic, AI interaction, Streamlit app, testing, scripting)
*   **AI Model API:** Google Gemini API (specifically targeting Flash 1.5 / 2.0)
    *   Using the **`google-genai`** Python SDK (v1.0+). Migrated from older `google-generativeai`.
    *   Local SDK source code and documentation available in `./gSDK/`.
*   **Web Application Framework:** Streamlit (`gemini_app.py`)
*   **Containerization:** Docker (`Dockerfile.gemini`, `docker-compose.yml`)

## Supporting Libraries & Frameworks (Confirmed for Gemini App)

*   **Python (`requirements-gemini.txt`):**
    *   `streamlit>=1.30.0`
    *   `pandas>=2.0.0`
    *   `matplotlib>=3.7.0`
    *   `plotly>=5.18.0`
    *   `python-dotenv>=1.0.0`
    *   `google-genai>=1.0.0` (New SDK)
    *   `protobuf>=4.25.0`
    *   `pytest` (for testing, confirmed by `pytest.ini` and `tests/` structure)
*   **JavaScript (in `js-client/`):**
    *   Node.js runtime environment (implied by `package.json`, `index.js`)
    *   Likely uses a Gemini client library for JavaScript if interacting directly from JS. Dependencies listed in `js-client/package.json`. (The purpose of `js-client` needs clarification - is it actively used or separate?)

## Development & Deployment Tools

*   **Version Control:** Git (implied by `.gitignore`)
*   **Package Management:**
    *   Python: `pip` (implied by `requirements*.txt`)
    *   JavaScript: `npm` or `yarn` (implied by `js-client/package.json`)
*   **Deployment Platform:** Google Cloud Platform (GCP)
*   **CI/CD:** Google Cloud Build (configured via scripts like `deploy_gemini_to_gcp_cloudbuild.py`)
*   **Shell:** Windows CMD (`.bat` scripts), Bash/Shell (`.sh` scripts) - suggests cross-platform considerations or development environments.

## Technical Constraints & Considerations

*   **Superprompt Size:** The ~125K token "EI_for_AI" superprompt (`prompt.md`) requires careful handling regarding token limits. Context Caching is implemented to mitigate costs.
*   **API Keys:** Secure management of Google Gemini API keys is necessary (via environment variables, loaded by `python-dotenv`). Key is stored in GCP Secret Manager for deployment.
*   **Context Caching:** Requires specific model versions (e.g., `gemini-1.5-flash-001`). Implemented using `google-genai` SDK's caching features.
*   **Multi-modality:** Integrating image generation/analysis is deferred.
*   **Dependencies:** Primarily managed via `requirements-gemini.txt` for the Streamlit app. Other `requirements*.txt` files might be for different components or outdated.
