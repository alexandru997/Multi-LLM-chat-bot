import os
from dotenv import load_dotenv

load_dotenv()

GROQ_API_KEY = os.getenv("GROQ_API_KEY")
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")

MODELS = {
    "groq": "llama-3.3-70b-versatile",
     "gemini": "gemini-2.0-flash-lite",
    "ollama": "llama3.2",
}

PROVIDERS = ["groq", "gemini", "ollama"]