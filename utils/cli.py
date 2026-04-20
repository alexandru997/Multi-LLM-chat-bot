import argparse
from config import PROVIDERS, MODELS

def parse_args():
    parser = argparse.ArgumentParser(
        description="Multi-LLM Chatbot - Groq, Gemini, Ollama"
    )

    parser.add_argument(
        "--provider",
        choices=PROVIDERS,
        default="groq",
        help="Choose the provider (default: groq)"
    )

    parser.add_argument(
        "--system-prompt",
        type=str,
        default="",
        help="Optional system prompt (ex: 'You are a helpful assistant')"
    )

    return parser.parse_args()