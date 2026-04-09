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
