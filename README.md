# EI-harness-lite

A lightweight harness for using the MHH EI superprompt with various LLMs.

## Overview

EI-harness-lite provides a simple way to use the [MHH EI for AI](https://github.com/MindHackingHappiness/MHH-EI-for-AI-Language-Enabled-Emotional-Intelligence-and-Theory-of-Mind-Algorithms) superprompt with different language models. It automatically loads the superprompt from the source repository and combines it with user input to generate responses with enhanced emotional intelligence and Theory of Mind capabilities.

## Features

- **Streamlined Design**: Minimal implementation focused on the core functionality
- **Multiple Interfaces**: Use as a Python library, command-line tool, or Streamlit web app
- **Model Flexibility**: Currently supports OpenAI models, with more providers planned
- **Dynamic Loading**: Loads the superprompt directly from the source repository

## Installation

```bash
# Clone the repository
git clone https://github.com/yourusername/EI-harness-lite.git
cd EI-harness-lite

# Install the package
pip install -e .
```

## Usage

### As a Python Library

```python
from ei_harness import EIHarness

# Initialize with OpenAI
harness = EIHarness(
    model_provider="openai",
    api_key="your-api-key",
    model_name="gpt-4"
)

# Generate a response
response = harness.generate("How would someone feel if their friend forgot their birthday?")
print(response)
```

### Command-Line Interface

```bash
# Basic usage
ei-harness-lite "How would someone feel if their friend forgot their birthday?" --api-key YOUR_API_KEY

# Interactive mode
ei-harness-lite --api-key YOUR_API_KEY

# Specify a different model
ei-harness-lite --model-provider openai --model gpt-3.5-turbo --api-key YOUR_API_KEY
```

### Streamlit Web App

```bash
# Run the Streamlit app
streamlit run app.py
```

## Environment Variables

You can set the following environment variables in a `.env` file:

```
OPENAI_API_KEY=your-openai-api-key
```

## License

This project is licensed under the GNU Affero General Public License v3.0 (AGPL-3.0) - see the [LICENSE](LICENSE) file for details.

## Acknowledgements

This project uses the [MHH EI for AI](https://github.com/MindHackingHappiness/MHH-EI-for-AI-Language-Enabled-Emotional-Intelligence-and-Theory-of-Mind-Algorithms) superprompt, which was developed by MindHackingHappiness.
