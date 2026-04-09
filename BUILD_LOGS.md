# Agastya Build Logs

## Phase 1: Project Scaffolding
- Initialized `uv` project targeting Python 3.12.
- Configured flat `src/agastya/` layout to properly interface with `uv_build`.
- Set up CLI entry point `mana`.
- Configured testing with `pytest` and `pytest-asyncio`.
- Created package skeletons (`core`, `llm`, `shell`, `builtins`, `mana`, `features`, `tui`, `utils`).
- Added initial `README.md` containing project overview and structure.
- Successfully verified project with `uv sync` and `uv run pytest` (0 tests collected as expected).
- Pushed changes to `build` branch under commit "feat: project scaffolding with uv and src layout".

## Phase 2: Core Config
- Implemented `AgastyaConfig`, `Profile`, and `FeaturesConfig` dataclasses.
- Implemented `ConfigLoader` parsing configuration from `~/.agastya/config.yaml`.
- Wrote full test coverage in `tests/test_config.py`.
- Updated `README.md` with Configuration section.
- Verified test success.
- Committed and pushed to `build` branch under commit "feat: config loading with profiles and feature flags".

## Phase 3: Mana Discovery & Validation
- Created `ManaInfo` and `ManaManager` classes.
- Implemented core mana functionality: checking if a dir is a mana (`NAV.md` existence), memory yaml registry management (register, unregister, list_all).
- Implemented mana initialization setting up directory structure (`schema.md`, `log.md`, `inbox.md`, `raw/`, etc.).
- Wrapped it all inside comprehensive pytest cases.
- Updated `README.md` with "Mana System" documentation.
- Committed and pushed to `build` branch under "feat: mana discovery, registration, and init".

## Phase 4: LLM Client Abstraction
- Implemented `Message` dataclass representing a chat query.
- Implemented `LLMClient` protocol establishing inference methods (chat and streaming).
- Implemented `LLMClientFactory` serving provider models.
- Wrote full test coverage in `tests/test_llm_base.py`.
- Updated `README.md` to add LLM Providers.
- Committed and pushed to `build` branch under "feat: LLM client protocol and factory".

## Phase 5: OpenAI-Compatible Client
- Updated `pyproject.toml` with `openai` SDK dependency.
- Mapped OpenAI API interface via `AsyncOpenAI` instance mapping our abstract `Message` to completion creation.
- Implemented streaming iterator bridging API delta chunks to our system's generator context.
- Implemented bypass logic for proxy models requiring dummy api_keys.
- Instantiated `OpenAIClient` properly inside the factory replacing dummy stubs.
- Wrote full mock-based test suite verifying API call parity.
- Committed and pushed to `build` branch.

## Phase 6: Anthropic Client
- Updated `pyproject.toml` with `anthropic` SDK dependency.
- Mapped Anthropic API interface via `AsyncAnthropic` client.
- Implemented `_extract_system_and_messages` separating system-role contexts per API requirements.
- Implemented streaming delta yielding mechanism.
- Created fully mocked tests in `tests/test_llm_anthropic.py` targeting API endpoints accurately.
- Committed and pushed to `build` branch.

## Phase 7: Built-in File Operations
- Implemented abstract functions in `builtins/file_ops.py` for safe python module extraction (`read_file`, `write_file`, `list_dir`).
- Designed tools evaluating missing dependencies effectively rendering non-destructive prompt errors instead.
- Created comprehensive edge-case pytest suite targeting file creation logic internally (`tests/test_builtins_file_ops.py`).
- Committed and pushed to `build` branch.

## Phase 8: Inbox System
- Implemented `append_to_inbox` built-in handler under `builtins/inbox.py`.
- Formatted payload successfully injecting UTC datetimes into the target appending files mapping robust context constraints seamlessly.
- Wrote completely covered test suite checking missing NAV requirements and auto-creation fallback behaviors of missing inbox components.
- Committed and pushed to `build` branch natively prioritizing safety checks bypassing raw execution blocks.
