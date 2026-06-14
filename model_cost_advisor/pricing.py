"""
Pricing database for 30+ LLM models.

All prices are per 1 million tokens (MTok) in USD.
Format: (input_price_per_MTok, output_price_per_MTok, tier, provider)
"""

MODELS: dict[str, dict] = {
    # ──────────────────────────────────────────────
    # OpenAI Models
    # ──────────────────────────────────────────────
    "GPT-4.1": {
        "input": 2.50,
        "output": 10.00,
        "tier": "premium",
        "provider": "OpenAI",
        "context_window": 1048576,
    },
    "GPT-4.1 Mini": {
        "input": 0.40,
        "output": 1.60,
        "tier": "value",
        "provider": "OpenAI",
        "context_window": 1048576,
    },
    "GPT-4.1 Nano": {
        "input": 0.10,
        "output": 0.40,
        "tier": "budget",
        "provider": "OpenAI",
        "context_window": 1048576,
    },
    "GPT-4o": {
        "input": 2.50,
        "output": 10.00,
        "tier": "premium",
        "provider": "OpenAI",
        "context_window": 128000,
    },
    "GPT-4o Mini": {
        "input": 0.15,
        "output": 0.60,
        "tier": "value",
        "provider": "OpenAI",
        "context_window": 128000,
    },
    "GPT-3.5 Turbo": {
        "input": 0.50,
        "output": 1.50,
        "tier": "budget",
        "provider": "OpenAI",
        "context_window": 16385,
    },
    "o3 Mini": {
        "input": 1.10,
        "output": 4.40,
        "tier": "value",
        "provider": "OpenAI",
        "context_window": 200000,
    },
    "o4 Mini": {
        "input": 1.10,
        "output": 4.40,
        "tier": "value",
        "provider": "OpenAI",
        "context_window": 200000,
    },

    # ──────────────────────────────────────────────
    # Anthropic / Claude Models
    # ──────────────────────────────────────────────
    "Claude Opus 4": {
        "input": 15.00,
        "output": 75.00,
        "tier": "premium",
        "provider": "Anthropic",
        "context_window": 200000,
    },
    "Claude Sonnet 4": {
        "input": 3.00,
        "output": 15.00,
        "tier": "quality",
        "provider": "Anthropic",
        "context_window": 200000,
    },
    "Claude Sonnet 3.5": {
        "input": 3.00,
        "output": 15.00,
        "tier": "quality",
        "provider": "Anthropic",
        "context_window": 200000,
    },
    "Claude Haiku 3.5": {
        "input": 0.80,
        "output": 4.00,
        "tier": "value",
        "provider": "Anthropic",
        "context_window": 200000,
    },
    "Claude 3 Haiku": {
        "input": 0.25,
        "output": 1.25,
        "tier": "value",
        "provider": "Anthropic",
        "context_window": 200000,
    },

    # ──────────────────────────────────────────────
    # Google / Gemini Models
    # ──────────────────────────────────────────────
    "Gemini 2.5 Pro": {
        "input": 1.25,
        "output": 10.00,
        "tier": "quality",
        "provider": "Google",
        "context_window": 1048576,
    },
    "Gemini 2.5 Flash": {
        "input": 0.15,
        "output": 0.60,
        "tier": "value",
        "provider": "Google",
        "context_window": 1048576,
    },
    "Gemini 2.0 Flash": {
        "input": 0.10,
        "output": 0.40,
        "tier": "budget",
        "provider": "Google",
        "context_window": 1048576,
    },
    "Gemini 2.0 Flash Lite": {
        "input": 0.075,
        "output": 0.30,
        "tier": "budget",
        "provider": "Google",
        "context_window": 1048576,
    },

    # ──────────────────────────────────────────────
    # DeepSeek Models
    # ──────────────────────────────────────────────
    "DeepSeek V4 Pro": {
        "input": 0.55,
        "output": 2.19,
        "tier": "value",
        "provider": "DeepSeek",
        "context_window": 262144,
    },
    "DeepSeek V4 Flash": {
        "input": 0.14,
        "output": 0.56,
        "tier": "budget",
        "provider": "DeepSeek",
        "context_window": 262144,
    },
    "DeepSeek R1": {
        "input": 0.55,
        "output": 2.19,
        "tier": "quality",
        "provider": "DeepSeek",
        "context_window": 131072,
    },
    "DeepSeek Coder V2": {
        "input": 0.14,
        "output": 0.28,
        "tier": "value",
        "provider": "DeepSeek",
        "context_window": 131072,
    },
    "DeepSeek Chat V3": {
        "input": 0.27,
        "output": 1.10,
        "tier": "value",
        "provider": "DeepSeek",
        "context_window": 131072,
    },

    # ──────────────────────────────────────────────
    # Meta / Llama Models (via Groq or Together)
    # ──────────────────────────────────────────────
    "Llama 4 Maverick": {
        "input": 0.20,
        "output": 0.60,
        "tier": "value",
        "provider": "Meta",
        "context_window": 1048576,
    },
    "Llama 4 Scout": {
        "input": 0.10,
        "output": 0.30,
        "tier": "budget",
        "provider": "Meta",
        "context_window": 10485760,
    },
    "Llama 3.3 70B": {
        "input": 0.59,
        "output": 0.79,
        "tier": "value",
        "provider": "Meta",
        "context_window": 131072,
    },
    "Llama 3.1 8B": {
        "input": 0.05,
        "output": 0.08,
        "tier": "budget",
        "provider": "Meta",
        "context_window": 131072,
    },

    # ──────────────────────────────────────────────
    # Mistral Models
    # ──────────────────────────────────────────────
    "Mistral Large 2": {
        "input": 2.00,
        "output": 6.00,
        "tier": "quality",
        "provider": "Mistral",
        "context_window": 131072,
    },
    "Mistral Small": {
        "input": 0.20,
        "output": 0.60,
        "tier": "value",
        "provider": "Mistral",
        "context_window": 32768,
    },
    "Mistral Nemo": {
        "input": 0.13,
        "output": 0.13,
        "tier": "budget",
        "provider": "Mistral",
        "context_window": 131072,
    },
    "Mixtral 8x22B": {
        "input": 0.90,
        "output": 0.90,
        "tier": "value",
        "provider": "Mistral",
        "context_window": 65536,
    },
    "Codestral": {
        "input": 0.20,
        "output": 0.60,
        "tier": "value",
        "provider": "Mistral",
        "context_window": 32768,
    },

    # ──────────────────────────────────────────────
    # Alibaba / Qwen Models
    # ──────────────────────────────────────────────
    "Qwen 3 Max": {
        "input": 0.40,
        "output": 1.20,
        "tier": "value",
        "provider": "Alibaba",
        "context_window": 32768,
    },
    "Qwen 3 Turbo": {
        "input": 0.05,
        "output": 0.20,
        "tier": "budget",
        "provider": "Alibaba",
        "context_window": 1048576,
    },
    "Qwen Coder": {
        "input": 0.18,
        "output": 0.54,
        "tier": "value",
        "provider": "Alibaba",
        "context_window": 131072,
    },

    # ──────────────────────────────────────────────
    # Other Providers
    # ──────────────────────────────────────────────
    "GLM-4 Flash": {
        "input": 0.055,
        "output": 0.22,
        "tier": "budget",
        "provider": "Zhipu AI",
        "context_window": 131072,
    },
    "Grok 3": {
        "input": 2.00,
        "output": 8.00,
        "tier": "premium",
        "provider": "xAI",
        "context_window": 1048576,
    },
    "Grok 3 Mini": {
        "input": 0.40,
        "output": 1.60,
        "tier": "value",
        "provider": "xAI",
        "context_window": 1048576,
    },
    "Command R+": {
        "input": 2.50,
        "output": 10.00,
        "tier": "quality",
        "provider": "Cohere",
        "context_window": 131072,
    },
    "Command R": {
        "input": 0.50,
        "output": 1.50,
        "tier": "value",
        "provider": "Cohere",
        "context_window": 131072,
    },
}

# Tier ordering for display
TIER_ORDER = ["budget", "value", "quality", "premium"]

# Tier display names
TIER_NAMES = {
    "budget": "Budget",
    "value": "Value",
    "quality": "Quality",
    "premium": "Premium",
}

# Tier descriptions
TIER_DESCRIPTIONS = {
    "budget": "cheapest valid option",
    "value": "best price/performance ratio",
    "quality": "highest accuracy & capability",
    "premium": "absolute best, cost no object",
}
