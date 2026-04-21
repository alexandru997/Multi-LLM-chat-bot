# Multi-LLM Chatbot

[![CI](https://github.com/alexandrubesliu/multi-llm-chatbot/actions/workflows/ci.yml/badge.svg)](https://github.com/alexandrubesliu/multi-llm-chatbot/actions/workflows/ci.yml)
[![Python 3.10+](https://img.shields.io/badge/python-3.10%2B-blue.svg)](https://www.python.org/downloads/)
[![Ruff](https://img.shields.io/endpoint?url=https://raw.githubusercontent.com/astral-sh/ruff/main/assets/badge/v2.json)](https://github.com/astral-sh/ruff)
[![Checked with mypy](https://www.mypy-lang.org/static/mypy_badge.svg)](https://mypy-lang.org/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

A lightweight, extensible command-line chatbot that lets you talk to multiple Large Language Model providers through a single interface — **Groq**, **Google Gemini**, and **Ollama** (local models) — without changing your workflow.

Switch providers with a single flag, track real token usage and estimated cost per session, and plug in new providers by dropping a single file into `providers/`.

---

## Features

- **Multi-provider support** — Groq (cloud), Gemini (cloud), Ollama (local). Swap with `--provider`.
- **Streaming responses** — token-by-token output for all three providers.
- **Conversation memory** — the full chat history is sent on every turn so the model can follow context.
- **Session commands** — clear history or view token usage without restarting.
- **Real token accounting** — input / output tokens pulled from each provider's API, with per-provider pricing for cost estimation.
- **System prompts** — set the assistant's persona or instructions via `--system-prompt`.
- **Clean architecture** — abstract `LLMProvider` base class; adding a new provider is a single file.
- **Fully tested & type-checked** — `pytest` suite, `mypy --strict`, `ruff` linting, all run in CI.
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

# 3. Install the project (runtime deps only)
pip install -e .

# Or, to install with development tools (pytest, ruff, mypy):
pip install -e ".[dev]"
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

Set `LOG_LEVEL=DEBUG` in the environment to see verbose internal logging.

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
├── config.py                  # API keys, model names, provider list, pricing
├── pyproject.toml             # Packaging + ruff + mypy + pytest configuration
├── .env                       # Your secrets (gitignored)
│
├── chat/
│   ├── session.py             # ChatSession — the interactive loop
│   └── cost_tracker.py        # Real token counters + $ cost estimation
│
├── providers/
│   ├── base.py                # Abstract LLMProvider interface + Usage/ChatResult dataclasses
│   ├── groq_provider.py       # Groq implementation (streaming)
│   ├── gemini_provider.py     # Gemini implementation (streaming)
│   ├── ollama_provider.py     # Ollama implementation (local HTTP, streaming)
│   └── __init__.py            # get_provider() factory + PROVIDER_MAP
│
├── utils/
│   ├── cli.py                 # argparse CLI definition
│   └── logging_config.py      # setup_logging() helper
│
├── tests/                     # pytest suite (mocks all external APIs)
│
└── .github/workflows/ci.yml   # ruff + mypy + pytest on Python 3.10 / 3.11 / 3.12
```

---

## Architecture & Design Patterns

The project is intentionally small but demonstrates several patterns that scale:

- **Abstract Factory** — `providers.get_provider(name)` decouples callers from concrete provider classes. Adding a new backend touches exactly one map entry.
- **Strategy** — `ChatSession` holds an `LLMProvider` polymorphically; provider is swappable at runtime via a CLI flag.
- **Template Method** (implicit) — `LLMProvider.stream_chat` defines the contract (stream output, return `ChatResult`, raise `ProviderError` on failure); concrete providers fill in API-specific request formatting and error translation.
- **Dependency Injection** — `ChatSession(provider=..., cost_tracker=...)` takes its collaborators as constructor args, which is exactly what makes the unit tests trivial to write (`MagicMock(spec=LLMProvider)` → no network).
- **Error wrapping** — every provider-specific exception (`GroqError`, `genai_errors.*`, `requests.*`) is caught and translated into a single `ProviderError` with a user-facing message. The session loop and `main()` never need provider-specific `except` blocks.
- **Typed-dataclass value objects** — `Usage` and `ChatResult` are frozen dataclasses; `CostTracker.add(usage)` can't be called with the wrong shape, and `mypy --strict` catches drift.

```
┌──────────┐   parse_args   ┌──────────┐   get_provider   ┌─────────────┐
│ main.py  │ ─────────────▶ │ utils.cli │ ──────────────▶ │ providers   │
└──────────┘                └──────────┘                  │  factory    │
     │                                                    └──────┬──────┘
     │ ChatSession(provider, cost_tracker)                       │ instantiates
     ▼                                                           ▼
┌──────────────────┐   stream_chat(messages)   ┌───────────────────────┐
│ chat.ChatSession │ ────────────────────────▶ │ Groq/Gemini/Ollama   │
│   run() loop     │ ◀──── ChatResult + Usage  │  Provider (stream)    │
└──────────────────┘                           └───────────────────────┘
     │ cost_tracker.add(usage)
     ▼
┌──────────────────┐
│ CostTracker      │  real tokens × provider pricing → $ estimate
└──────────────────┘
```

---

## How It Works

1. `main.py` configures logging, parses CLI arguments, asks the `providers` factory for the selected provider, and hands it to a new `ChatSession`.
2. `ChatSession.run()` loops on `input("You: ")`. Each user message is appended to `self.messages`, passed to the provider's `stream_chat`, and the response is appended back — so every turn carries the full conversation.
3. `CostTracker` receives a `Usage(input_tokens, output_tokens)` value returned by the provider (real counts from the API, not estimates) and multiplies by per-provider pricing from `config.PRICING`.
4. Providers inherit from `LLMProvider` (`providers/base.py`), which requires `name`, `model`, and `stream_chat(messages, system_prompt) -> ChatResult`. On failure they raise `ProviderError` with a user-facing message.

---

## Development

All dev tools are installed via the `dev` optional-dependencies extra:

```bash
pip install -e ".[dev]"
```

Then, from the project root:

```bash
# Run the test suite
pytest

# Lint the codebase
ruff check .

# Auto-fix lint issues where possible
ruff check --fix .

# Type-check (strict mode — see pyproject.toml)
mypy .
```

The same three commands run in CI on every push and pull request across Python 3.10, 3.11, and 3.12 (`.github/workflows/ci.yml`).

### Test strategy

- `tests/test_cost_tracker.py` — pure-logic tests on `CostTracker`, no mocks.
- `tests/test_session.py` — `ChatSession` driven by a `MagicMock(spec=LLMProvider)`; asserts history accumulation, error rollback, system-prompt wiring.
- `tests/test_providers_factory.py` — `get_provider` happy/error paths.
- `tests/test_groq_provider.py` — `Groq` SDK client fully mocked via `pytest-mock`; verifies streaming accumulation, usage extraction, and `GroqError → ProviderError` wrapping.
- `tests/test_cli.py` — `argparse` wiring.

No external API is hit during tests. Everything that touches network is mocked at the SDK boundary.

---

## Adding a New Provider

1. Create `providers/myprovider_provider.py`:

   ```python
   from providers.base import ChatResult, LLMProvider, Usage

   class MyProvider(LLMProvider):
       def __init__(self) -> None:
           self._model = "my-model-id"

       @property
       def name(self) -> str:
           return "myprovider"

       @property
       def model(self) -> str:
           return self._model

       def stream_chat(
           self, messages: list[dict[str, str]], system_prompt: str = ""
       ) -> ChatResult:
           # Call your API, print the output, return the full text + Usage
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
   PRICING["myprovider"] = {"input": ..., "output": ...}
   ```

That's it — `python main.py --provider myprovider` now works.

---

## Troubleshooting

| Symptom                                                           | Fix                                                                                  |
|-------------------------------------------------------------------|--------------------------------------------------------------------------------------|
| `Gemini: Quota exceeded. Wait a few minutes or use --provider groq` | Free Gemini tier is rate-limited — wait or switch provider.                        |
| `Gemini: Model not found. Check config.py -> MODELS['gemini']`  | The model ID in `config.py` is no longer valid. Pick a current one from AI Studio.   |
| `Ollama is not running. Run 'ollama serve' in the terminal.`    | Start the Ollama daemon in a separate terminal, then retry.                          |
| `Unknown provider: '...'`                                         | Typo in `--provider`. Valid values: `groq`, `gemini`, `ollama`.                      |
| `GROQ_API_KEY is missing` / `GEMINI_API_KEY is missing`           | `.env` is missing or not in the project root. Activate your venv from the root too. |
| `mypy` / `ruff` / `pytest` command not found                      | You installed the runtime extras only — run `pip install -e ".[dev]"`.               |

---

## License

MIT — do whatever you want, just don't blame the author if your chatbot becomes sentient.
