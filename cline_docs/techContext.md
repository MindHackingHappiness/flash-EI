# Technical Context: EI-harness-lite

## Core Technologies

*   **Programming Language:** Python (primary, used for backend logic, AI interaction, Streamlit app, testing, scripting)
*   **AI Model API:** Google Gemini API (specifically targeting Flash 2.0)
    *   Likely using the `google-generativeai` Python library (based on typical Gemini integration patterns, needs confirmation by checking `requirements*.txt`).
*   **Web Application Framework:** Streamlit (`gemini_app.py`)
*   **Containerization:** Docker (`Dockerfile`, `Dockerfile.gemini`, `docker-compose.yml`)

## Supporting Libraries & Frameworks (Inferred/Potential)

*   **Python:**
    *   `requests` or `httpx` (for direct API calls if not using the official SDK)
    *   `pytest` (for testing, confirmed by `pytest.ini` and `tests/` structure)
    *   `python-dotenv` (for loading `.env` files, common practice)
    *   Libraries listed in `requirements.txt`, `requirements-gemini.txt`, `requirements.1.txt`, `requirements.2.txt` (Need to inspect these files).
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

*   **Superprompt Size:** The 170Kb "EI_for_AI" superprompt (`prompt.md`) requires careful handling regarding token limits and potentially caching strategies.
*   **API Keys:** Secure management of Google Gemini API keys is necessary (likely via environment variables).
*   **Multi-modality:** Integrating image generation (and later, analysis) requires handling image data alongside text within the application flow and potentially the API calls.
*   **Dependencies:** Managing dependencies across different `requirements*.txt` files needs attention.
