# Agastya

> LLM-powered knowledge agent with persistent, compounding manas.

**Agastya** is a terminal-based Python agent (TUI via Textual) that incrementally builds and maintains persistent, interlinked markdown knowledge bases called **manas**. It ingests raw sources, synthesizes knowledge pages, and provides an intelligent conversational interface for querying and managing your knowledge.

All terminal commands use `mana` as the entry point.

---

## Tech Stack

| Category | Choice |
|----------|--------|
| Language | Python 3.12+ |
| Package Manager | `uv` |
| TUI Framework | `textual` |
| LLM (OpenAI-compat) | `openai` SDK |
| LLM (Anthropic) | `anthropic` SDK |
| Config | `pyyaml` |
| Testing | `pytest`, `pytest-asyncio` |

---

## Project Structure

```
agastya/
├── pyproject.toml          # Project metadata, deps, scripts
├── .python-version         # Pinned to 3.12
├── README.md
├── src/
│   └── agastya/            # Main package (required by uv_build)
│       ├── __init__.py
│       ├── core/           # Config, agent loop, context, conversation
│       ├── llm/            # LLM client abstraction + provider implementations
│       ├── shell/          # Shell command execution with user confirmation
│       ├── builtins/       # Built-in ops (file ops, inbox) — no confirmation needed
│       ├── mana/           # Mana registry, discovery, NAV.md, git, inbox, ingest
│       ├── features/       # Toggleable features (blog, tweets)
│       ├── tui/            # Textual TUI app, screens, widgets
│       │   ├── screens/    # Main, review, briefing screens
│       │   └── widgets/    # Chat, mana_tree, backlinks, status_bar
│       └── utils/          # Shared utilities (markdown, epub, fs helpers)
└── tests/                  # All tests (separate from src, mirrors src structure)
```

## Mana System

A **mana** is an independent knowledge directory (like a wiki). A directory is identified as a mana if it contains a `NAV.md` file at its root. 

### Registering and Initializing Manas

```bash
# Register an existing directory as a mana
mana register /path/to/my-research

# See all known manas
mana list

# Initialize a completely new mana
mana init /path/to/new-project
```

### Directory Structure

A generated mana contains the following components:
- `NAV.md`: Navigation index (identifies dir as a mana, agent reads this first)
- `schema.md`: LLM conventions for this domain
- `log.md`: Chronological activity log
- `inbox.md`: Append-and-review capture area
- `raw/`: Directory for immutable source documents
- `pages/`: Directory for LLM-generated synthesized knowledge pages
- `.agastya/`: Mana-local configuration

---

## Configuration

Agastya reads its configuration from `~/.agastya/config.yaml`.

```yaml
default_profile: deep
profiles:
  deep:
    provider: anthropic
    model: claude-3-opus-20240229
    description: "Deep thinking"
  local:
    provider: ollama
    model: llama3
    base_url: http://localhost:11434
    description: "Offline, private"

features:
  blog_generation: true
  tweet_generation: true
  tweet_generation_locked: false
```

## LLM Providers

Agastya abstracts all text generation behind a unified `LLMClient` protocol. Multiple LLM providers are natively supported:

| Provider | Client Implementation | Notes |
|----------|-----------------------|-------|
| OpenAI | OpenAI-compatible | Default GPT-4/o1 endpoints |
| Gemini | OpenAI-compatible | Requires Google base URL override |
| Ollama | OpenAI-compatible | Local offline open-source models |
| OpenRouter | OpenAI-compatible | Multi-model routing |
| Anthropic | Anthropic SDK native | For Claude (Sonnet, Opus) |

You can specify which provider to use per `Profile` configured in `config.yaml`.

---

## Getting Started

```bash
# Install dependencies
uv sync

# Run tests
uv run pytest

# (future) Launch TUI
uv run mana
```

---

## Development Status

🚧 **Phase 1: Project Scaffolding** — in progress
