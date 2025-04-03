# EI-harness-lite

A lightweight harness for using the MHH EI superprompt with various LLMs, featuring a comprehensive UI, multi-provider support, token counting, cost estimation, and API-level caching.

## Overview

EI-harness-lite provides a simple way to use the [MHH EI for AI](https://github.com/MindHackingHappiness/MHH-EI-for-AI-Language-Enabled-Emotional-Intelligence-and-Theory-of-Mind-Algorithms) superprompt with different language models. It automatically loads the superprompt from the source repository and combines it with user input to generate responses with enhanced emotional intelligence and Theory of Mind capabilities.

![EI-harness-lite UI](https://github.com/MindHackingHappiness/EI-harness-lite/blob/main/docs/images/docs/ui-screenshot.png?raw=true)

## Features

- **Streamlined Design**: Minimal implementation focused on the core functionality
- **Multiple Interfaces**: Use as a Python library, command-line tool, or Streamlit web app
- **Comprehensive UI**: User-friendly interface with model selection, pricing information, and usage metrics
- **Multi-Provider Support**: Works with:
  - **Commercial APIs**: OpenAI, Anthropic, Gemini, Groq, Hugging Face
  - **Local Models**: Ollama, LlamaCPP, vLLM
- **Superprompt Editor**: Edit the superprompt directly or by sections with real-time token counting
- **Dynamic Loading**: Loads the superprompt directly from the source repository
- **Token Counting**: Accurately counts tokens for all supported models
- **Cost Estimation**: Provides transparent cost estimates for API calls
- **Enhanced Caching**: Leverages provider-specific caching with detailed statistics:
  - OpenAI: 50% discount on input tokens
  - Anthropic: 50% discount on input tokens
  - Gemini: 75% discount on input tokens
  - Groq: 50% discount on input tokens (estimated)
- **Context Window Awareness**: Warns when approaching model token limits
- **Colorful Output**: Uses colorama for clear, visual feedback in the terminal

## Installation

### Quick Setup (Recommended)

```bash
# Clone the repository
git clone https://github.com/yourusername/EI-harness-lite.git
cd EI-harness-lite

# Run the setup script
python setup_env.py
```

This script will:
1. Create a virtual environment
2. Install the package and all dependencies
3. Provide instructions for activating the environment and running the app

### Manual Setup

```bash
# Clone the repository
git clone https://github.com/yourusername/EI-harness-lite.git
cd EI-harness-lite

# Create and activate a virtual environment
# For Windows
python -m venv venv
venv\Scripts\activate

# For macOS/Linux
# python -m venv venv
# source venv/bin/activate

# Install the package and dependencies
pip install -e .
```

The virtual environment helps isolate the project dependencies from your system Python installation, preventing conflicts between packages.

## Usage

### As a Python Library

```python
from ei_harness import EIHarness

# Initialize with OpenAI (with API-level caching enabled)
harness = EIHarness(
    model_provider="openai",
    api_key="your-api-key",
    model_name="gpt-4",
    enable_cache=True,  # Enable OpenAI's API-level caching (50% discount on input tokens)
    verbose=True        # Show token counts and cost estimates
)

# Generate a response
response = harness.generate("How would someone feel if their friend forgot their birthday?")
print(response)

# Get usage information
usage_info = harness.get_usage_info()
print(f"Total tokens: {usage_info['usage']['total_tokens']}")
print(f"Estimated cost: ${usage_info['cost']['total_cost']:.6f}")
print(f"Cached: {usage_info['cached']}")
```

### Command-Line Interface

```bash
# Basic usage
ei-harness-lite "How would someone feel if their friend forgot their birthday?" --api-key YOUR_API_KEY

# Interactive mode
ei-harness-lite --api-key YOUR_API_KEY

# Specify a different model
ei-harness-lite --model gpt-3.5-turbo --api-key YOUR_API_KEY

# Disable API-level caching
ei-harness-lite --no-cache --api-key YOUR_API_KEY

# Suppress token count and cost information
ei-harness-lite --quiet --api-key YOUR_API_KEY
```

### Streamlit Web App

```bash
# Make sure your virtual environment is activated
# For Windows: venv\Scripts\activate
# For macOS/Linux: source venv/bin/activate

# Run the Streamlit app
streamlit run app.py
```

The Streamlit app provides a comprehensive user interface with:

#### Model Selection and Configuration
- Support for multiple providers (OpenAI, Anthropic, Gemini, Groq, Hugging Face, Ollama, LlamaCPP, vLLM)
- Dynamic model selection based on the chosen provider
- Provider-specific configuration options (endpoints, temperature settings for local models)
- Detailed model information (pricing, context window size)
- Links to provider documentation

#### Superprompt Editor
- Full-text editor for direct editing of the entire superprompt
- Section-based editor with collapsible sections:
  - Copyright and License
  - Title and Author
  - Foreword
  - Instructions to the LLM (main content)
- Custom message appending with a single click
- Real-time token counting for all edits
- Context window warnings when approaching model limits

#### Enhanced Caching UI
- Visual indicators for cache availability by provider
- Detailed caching information with discount percentages
- Cache hit statistics showing cost savings
- Cache control options (enable/disable, clear cache)
- Transparent display of cached vs. non-cached requests

#### Usage Metrics
- Detailed token usage tracking (input, output, total)
- Cost estimation for each request
- Cumulative usage statistics
- Cache status indicators

### Running Tests

```bash
# Make sure your virtual environment is activated
# For Windows: venv\Scripts\activate
# For macOS/Linux: source venv/bin/activate

# Run the manual test script (no API calls)
python test_harness.py

# Run pytest tests
pytest
```

The test suite includes:
- **Manual tests** (test_harness.py): Quick verification of core functionality
- **Pytest tests**: Comprehensive test suite with:
  - Token counting and cost estimation tests
  - OpenAI model tests with mocked API calls
  - EIHarness class tests
  - API-level caching verification

All pytest tests are designed to run without making actual API calls, so you don't need an API key to run the tests.

## OpenAI API-Level Caching

This project leverages OpenAI's API-level caching feature, which provides a 50% discount on input tokens when the same prompt is used within an hour. This is particularly valuable for the superprompt, which can be quite large.

When caching is enabled (the default):
1. The system generates a deterministic cache ID based on the request parameters
2. OpenAI recognizes identical requests and applies the discount
3. The UI/CLI clearly indicates when caching is being applied

You can disable caching with the `--no-cache` flag in the CLI or by setting `enable_cache=False` in the Python API.

## Environment Variables

You can set the following environment variables in a `.env` file to avoid entering API keys in the UI:

```
# API Keys for Commercial Providers
OPENAI_API_KEY=your-openai-api-key
ANTHROPIC_API_KEY=your-anthropic-api-key
GEMINI_API_KEY=your-gemini-api-key
GROQ_API_KEY=your-groq-api-key
HUGGINGFACE_API_KEY=your-huggingface-api-key

# Endpoints for Local Models (optional)
OLLAMA_ENDPOINT=http://localhost:11434
LLAMACPP_ENDPOINT=http://localhost:8080
VLLM_ENDPOINT=http://localhost:8000
```

A sample `.env.example` file is included in the repository. Copy it to `.env` and add your API keys:

```bash
cp .env.example .env
# Then edit .env with your favorite text editor
```

## License

This project is licensed under the GNU Affero General Public License v3.0 (AGPL-3.0) - see the [LICENSE](LICENSE) file for details.

## Acknowledgements

This project uses the [MHH EI for AI](https://github.com/MindHackingHappiness/MHH-EI-for-AI-Language-Enabled-Emotional-Intelligence-and-Theory-of-Mind-Algorithms) superprompt, which was developed by MindHackingHappiness.
