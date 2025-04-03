"""
Centralized model information for all supported providers.
"""

# Documentation URLs
PROVIDER_DOCS = {
    "openai": "https://platform.openai.com/docs/pricing",
    "anthropic": "https://www.anthropic.com/pricing#anthropic-api",
    "gemini": "https://ai.google.dev/gemini-api/docs/pricing",
    "groq": "https://console.groq.com/docs/pricing",
    "huggingface": "https://huggingface.co/docs/api-inference/index",
    "ollama": "https://github.com/ollama/ollama",
    "llamacpp": "https://github.com/ggerganov/llama.cpp",
    "vllm": "https://github.com/vllm-project/vllm",
}

# Pricing information (per 1K tokens)
MODEL_PRICING = {
    # OpenAI models (from https://platform.openai.com/docs/pricing)
    "gpt-4-turbo": {"input": 0.01/1e3, "output": 0.03/1e3},
    "gpt-4": {"input": 0.03/1e3, "output": 0.06/1e3},
    "gpt-4-32k": {"input": 0.06/1e3, "output": 0.12/1e3},
    "gpt-3.5-turbo": {"input": 0.0015/1e3, "output": 0.002/1e3},
    "gpt-3.5-turbo-16k": {"input": 0.003/1e3, "output": 0.004/1e3},
    
    # Anthropic models (from https://www.anthropic.com/pricing#anthropic-api)
    "claude-3.7-sonnet": {"input": 0.003/1e3, "output": 0.015/1e3},
    "claude-3.5-sonnet": {"input": 0.003/1e3, "output": 0.015/1e3},
    "claude-3.5-haiku": {"input": 0.00080/1e3, "output": 0.004/1e3},
    "claude-3-opus": {"input": 0.015/1e3, "output": 0.075/1e3},
    "claude-3-sonnet": {"input": 0.003/1e3, "output": 0.015/1e3},
    "claude-3-haiku": {"input": 0.00025/1e3, "output": 0.00125/1e3},
    
    # Gemini models (from https://ai.google.dev/gemini-api/docs/pricing)
    "gemini-2.0-flash": {"input": 0.00010/1e3, "output": 0.00040/1e3},
    "gemini-2.0-flash-lite": {"input": 0.000075/1e3, "output": 0.00030/1e3},
    "gemini-1.5-flash": {"input": 0.000075/1e3, "output": 0.00030/1e3},
    "gemini-1.5-flash-8b": {"input": 0.0000375/1e3, "output": 0.00015/1e3},
    "gemini-1.5-pro": {"input": 0.00125/1e3, "output": 0.005/1e3},
    
    # Groq models (from https://console.groq.com/docs/pricing)
    "llama3-8b-8192": {"input": 0.0001/1e3, "output": 0.0002/1e3},
    "llama3-70b-8192": {"input": 0.0007/1e3, "output": 0.0009/1e3},
    "mixtral-8x7b-32768": {"input": 0.0006/1e3, "output": 0.0009/1e3},
    "gemma-7b-it": {"input": 0.0001/1e3, "output": 0.0002/1e3},
    
    # Local models (free to use)
    "ollama:llama3": {"input": 0, "output": 0},
    "ollama:mistral": {"input": 0, "output": 0},
    "ollama:gemma": {"input": 0, "output": 0},
    "llamacpp:llama3": {"input": 0, "output": 0},
    "llamacpp:mistral": {"input": 0, "output": 0},
    "vllm:llama3": {"input": 0, "output": 0},
    "vllm:mistral": {"input": 0, "output": 0},
    
    # Hugging Face models (varies by model)
    "huggingface:mistralai/Mistral-7B-Instruct-v0.2": {"input": 0, "output": 0},
    "huggingface:meta-llama/Llama-2-70b-chat-hf": {"input": 0, "output": 0},
}

# Context window sizes
MODEL_CONTEXT_WINDOW = {
    # OpenAI models
    "gpt-4-turbo": 128000,
    "gpt-4": 8192,
    "gpt-4-32k": 32768,
    "gpt-3.5-turbo": 4096,
    "gpt-3.5-turbo-16k": 16384,
    
    # Anthropic models
    "claude-3.7-sonnet": 200000,
    "claude-3.5-sonnet": 200000,
    "claude-3.5-haiku": 200000,
    "claude-3-opus": 200000,
    "claude-3-sonnet": 200000,
    "claude-3-haiku": 200000,
    
    # Gemini models
    "gemini-2.0-flash": 1000000,
    "gemini-2.0-flash-lite": 1000000,
    "gemini-1.5-flash": 1000000,
    "gemini-1.5-flash-8b": 1000000,
    "gemini-1.5-pro": 2000000,
    
    # Groq models
    "llama3-8b-8192": 8192,
    "llama3-70b-8192": 8192,
    "mixtral-8x7b-32768": 32768,
    "gemma-7b-it": 8192,
    
    # Local models (context window varies by model and configuration)
    "ollama:llama3": 8192,
    "ollama:mistral": 8192,
    "ollama:gemma": 8192,
    "llamacpp:llama3": 8192,
    "llamacpp:mistral": 8192,
    "vllm:llama3": 8192,
    "vllm:mistral": 8192,
    
    # Hugging Face models
    "huggingface:mistralai/Mistral-7B-Instruct-v0.2": 8192,
    "huggingface:meta-llama/Llama-2-70b-chat-hf": 4096,
}

# Caching capabilities
PROVIDER_CACHING = {
    "openai": {
        "supports_caching": True,
        "discount": 0.5,  # 50% discount on input tokens
        "description": "OpenAI applies a 50% discount on input tokens for identical requests within an hour."
    },
    "anthropic": {
        "supports_caching": True,
        "discount": 0.5,  # 50% discount with prompt caching
        "description": "Anthropic offers prompt caching with a 50% discount on input tokens."
    },
    "gemini": {
        "supports_caching": True,
        "discount": 0.75,  # 75% discount with context caching
        "description": "Gemini offers context caching at a 75% discount of the input price."
    },
    "groq": {
        "supports_caching": True,
        "discount": 0.5,  # 50% discount on input tokens (estimated)
        "description": "Groq offers caching for identical requests, reducing costs for repeated queries."
    },
    "huggingface": {
        "supports_caching": False,
        "discount": 0,
        "description": "Hugging Face Inference API does not currently offer built-in caching."
    },
    "ollama": {
        "supports_caching": False,
        "discount": 0,
        "description": "Local Ollama models are already free to use, no caching discount applies."
    },
    "llamacpp": {
        "supports_caching": False,
        "discount": 0,
        "description": "Local LlamaCPP models are already free to use, no caching discount applies."
    },
    "vllm": {
        "supports_caching": False,
        "discount": 0,
        "description": "Local vLLM models are already free to use, no caching discount applies."
    }
}

# Available models by provider
PROVIDER_MODELS = {
    "openai": ["gpt-4-turbo", "gpt-4", "gpt-4-32k", "gpt-3.5-turbo", "gpt-3.5-turbo-16k"],
    "anthropic": ["claude-3.7-sonnet", "claude-3.5-sonnet", "claude-3.5-haiku", "claude-3-opus", "claude-3-sonnet", "claude-3-haiku"],
    "gemini": ["gemini-2.0-flash", "gemini-2.0-flash-lite", "gemini-1.5-flash", "gemini-1.5-flash-8b", "gemini-1.5-pro"],
    "groq": ["llama3-8b-8192", "llama3-70b-8192", "mixtral-8x7b-32768", "gemma-7b-it"],
    "huggingface": ["huggingface:mistralai/Mistral-7B-Instruct-v0.2", "huggingface:meta-llama/Llama-2-70b-chat-hf"],
    "ollama": ["ollama:llama3", "ollama:mistral", "ollama:gemma"],
    "llamacpp": ["llamacpp:llama3", "llamacpp:mistral"],
    "vllm": ["vllm:llama3", "vllm:mistral"]
}

# Configuration options for local providers
LOCAL_PROVIDER_CONFIG = {
    "ollama": {
        "endpoint": "http://localhost:11434",
        "config_options": ["temperature", "top_p", "top_k", "repeat_penalty"]
    },
    "llamacpp": {
        "endpoint": "http://localhost:8080",
        "config_options": ["temperature", "top_p", "top_k", "repeat_penalty"]
    },
    "vllm": {
        "endpoint": "http://localhost:8000",
        "config_options": ["temperature", "top_p", "top_k", "repetition_penalty"]
    }
}
