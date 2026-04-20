# Multi-LLM Chatbot

A lightweight, extensible command-line chatbot that lets you talk to multiple Large Language Model providers through a single interface — **Groq**, **Google Gemini**, and **Ollama** (local models) — without changing your workflow.

Switch providers with a single flag, track token usage per session, and plug in new providers by dropping a file into `providers/`.

---

## Features

- **Multi-provider support** — Groq (cloud), Gemini (cloud), Ollama (local). Swap with `--provider`.
- **Streaming responses** where the provider supports it (Groq streams token-by-token).
- **Conversation memory** — the full chat history is sent on every turn so the model can follow context.
- **Session commands** — clear history or view token usage without restarting.
- **Cost / usage tracking** — running totals of input tokens, output tokens, and message count.
- **System prompts** — set the assistant's persona or instructions via `--system-prompt`.
- **Clean architecture** — abstract `LLMProvider` base class; adding a new provider is a single file.
- **No cost when it matters** — Groq and Gemini both offer generous free tiers; Ollama runs fully offline on your machine.

---

## Supported Providers

| Provider | Type  | Default Model            | Requires           |
|----------|-------|--------------------------|--------------------|
| `groq`   | Cloud | `llama-3.3-70b-versatile` | `GROQ_API_KEY`     |
| `gemini` | Cloud | `gemini-2.0-flash-lite`   | `GEMINI_API_KEY`   |
| `ollama` | Local | `llama3.2`                | Ollama running locally |

Change the model for any provider by editing `MODELS` in `config.py`.

---

## Requirements

- **Python 3.10+** (the code uses `list[dict]` built-in generics)
- A free **Groq** API key — https://console.groq.com/keys
- A free **Gemini** API key — https://aistudio.google.com/apikey
- *(Optional)* **Ollama** installed locally — https://ollama.com/download

You only need the API key(s) for the provider(s) you actually plan to use.

---

## Installation

```bash
# 1. Clone or download the project
cd multi-llm-chatbot

# 2. Create and activate a virtual environment
python -m venv .venv
# Windows (bash):
source .venv/Scripts/activate
# Linux / macOS:
source .venv/bin/activate

# 3. Install dependencies
pip install -r requirements.txt
```

---

## Configuration

Create a `.env` file in the project root with your API keys:

```env
GROQ_API_KEY=gsk_your_groq_key_here
GEMINI_API_KEY=your_gemini_key_here
```

Only the key for the provider you plan to use is required. Ollama needs no key — just make sure `ollama serve` is running.

To change a model, edit `config.py`:

```python
MODELS = {
    "groq":   "llama-3.3-70b-versatile",
    "gemini": "gemini-2.0-flash-lite",
    "ollama": "llama3.2",
}
```

---

## Usage

### Basic

```bash
python main.py
```

Starts a chat with the default provider (`groq`).

### Choose a provider

```bash
python main.py --provider gemini
python main.py --provider ollama
```

### With a system prompt

```bash
python main.py --provider groq --system-prompt "You are a senior Python code reviewer."
```

### In-chat commands

While chatting, type any of these at the `You:` prompt:

| Command  | What it does                                         |
|----------|------------------------------------------------------|
| `/quit`  | Print session summary and exit                       |
| `/clear` | Wipe the conversation history (keeps the session alive) |
| `/cost`  | Print the running token/message summary              |

`Ctrl+C` also exits cleanly and prints the summary.

### Full help

```bash
python main.py --help
```

---

## Examples

**Quick question with Groq:**
```bash
python main.py --provider groq
You: Explain Python decorators in one paragraph.
```

**Local, offline, private — with Ollama:**
```bash
ollama serve          # in another terminal, if not already running
ollama pull llama3.2  # once
python main.py --provider ollama
```

**Long-form assistant persona:**
```bash
python main.py --provider gemini --system-prompt "You are a friendly Romanian → English translator. Always reply with both the translation and a one-line grammar note."
```

---

## Project Structure

```
multi-llm-chatbot/
├── main.py                    # Entry point — wires everything together
├── config.py                  # API keys, model names, provider list
├── requirements.txt
├── .env                       # Your secrets (gitignored)
│
├── chat/
│   ├── session.py             # ChatSession — the interactive loop
│   └── cost_tracker.py        # Token / message counters
│
├── providers/
│   ├── base.py                # Abstract LLMProvider interface
│   ├── groq_provider.py       # Groq implementation (streaming)
│   ├── gemini_provider.py     # Gemini implementation
│   ├── ollama_provider.py     # Ollama implementation (local HTTP)
│   └── __init__.py            # get_provider() factory
│
└── utils/
    └── cli.py                 # argparse CLI definition
```

---

## How It Works

1. `main.py` parses CLI arguments, asks the `providers` factory for the selected provider, and hands it to a new `ChatSession`.
2. `ChatSession.run()` loops on `input("You: ")`. Each user message is appended to `self.messages`, passed to the provider's `stream_chat`, and the response is appended back — so every turn carries the full conversation.
3. `CostTracker` estimates tokens (`len(text) // 4`) and keeps per-session totals.
4. Providers inherit from `LLMProvider` (`providers/base.py`), which requires `name`, `model`, and `stream_chat(messages, system_prompt)`.

---

## Adding a New Provider

1. Create `providers/myprovider_provider.py`:

   ```python
   from providers.base import LLMProvider

   class MyProvider(LLMProvider):
       def __init__(self):
           self._model = "my-model-id"

       @property
       def name(self) -> str:
           return "myprovider"

       @property
       def model(self) -> str:
           return self._model

       def stream_chat(self, messages: list[dict], system_prompt: str = "") -> str:
           # Call your API, print the output, return the full text
           ...
   ```

2. Register it in `providers/__init__.py`:

   ```python
   from providers.myprovider_provider import MyProvider

   PROVIDER_MAP = {
       "groq":       GroqProvider,
       "gemini":     GeminiProvider,
       "ollama":     OllamaProvider,
       "myprovider": MyProvider,   # <-- add this line
   }
   ```

3. Add it to `config.py`:

   ```python
   MODELS["myprovider"] = "my-model-id"
   PROVIDERS.append("myprovider")
   ```

That's it — `python main.py --provider myprovider` now works.

---

## Troubleshooting

| Symptom                                                           | Fix                                                                                  |
|-------------------------------------------------------------------|--------------------------------------------------------------------------------------|
| `[Gemini: Quota exceeded. Wait a few minutes or use --provider groq]` | Free Gemini tier is rate-limited — wait or switch provider.                        |
| `[Gemini: Model not found. Check config.py -> MODELS['gemini']]`  | The model ID in `config.py` is no longer valid. Pick a current one from AI Studio.   |
| `[Ollama is not running. Run 'ollama serve' in the terminal.]`    | Start the Ollama daemon in a separate terminal, then retry.                          |
| `Unknown provider: '...'`                                         | Typo in `--provider`. Valid values: `groq`, `gemini`, `ollama`.                      |
| `GROQ_API_KEY`/`GEMINI_API_KEY` is `None`                         | `.env` is missing or not in the project root. Activate your venv from the root too. |

---

## License

MIT — do whatever you want, just don't blame the author if your chatbot becomes sentient.
