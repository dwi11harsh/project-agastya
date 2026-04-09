# Agastya — LLM Knowledge Agent Plan

> **Status**: DISCUSSION PHASE — Not ready for implementation
> **Last Updated**: 2026-04-06T22:16
> **Project Name**: Agastya
> **Terminology**: "wiki" is now **mana** (knowledge base unit)

---

## Vision

**Agastya** is a terminal-based Python agent (TUI via Textual) that implements the **LLM knowledge base** pattern (inspired by Karpathy's LLM Wiki & Farza's Farzapedia): an agent that incrementally builds and maintains persistent, interlinked markdown knowledge bases (**manas**) from raw sources. Incorporates the **append-and-review** note-taking philosophy as a lightweight capture mechanism.

Key insight from Farzapedia: the knowledge base should be optimized for **agent consumption** — structured so the LLM can navigate, drill into, and synthesize from it naturally. This file-system-based approach outperforms RAG.

The agent is extensible — anyone can add new tools to the `tools/` directory. A manifest file (`0.TOOLS_MANIFEST.md`) gives the LLM a lightweight index of all available tools. The LLM only loads full tool details when it actually needs to use one — or falls back to its own pre-existing knowledge. Supports multiple LLM providers. Designed for macOS initially, with future `pip install agastya` distribution in mind.

---

## Glossary

| Term                  | Meaning                                                                                                   |
| --------------------- | --------------------------------------------------------------------------------------------------------- |
| **mana**              | A knowledge base unit — a directory containing `NAV.md` + structured content. Replaces "wiki" everywhere. |
| **NAV.md**            | Navigation file that identifies a directory as a mana and serves as its table of contents.                |
| **raw/**              | Immutable source documents within a mana (articles, papers, images, epubs).                               |
| **schema.md**         | LLM conventions and workflows for a specific mana's domain.                                               |
| **inbox.md**          | Append-and-review capture file within a mana.                                                             |
| **TOOLS_MANIFEST.md** | Lightweight index of all available tools — name + one-line description. The LLM reads this first.         |
| **blogs/**            | Directory containing user-controlled blog posts (toggleable feature).                                     |
| **tweets/**           | Directory containing generated tweets, numbered sequentially: `1.relevant-name.md`, `2.another-topic.md`. |
| **agent**             | Agastya itself — the LLM-powered knowledge agent.                                                         |

---

## Architecture Overview

```
┌──────────────────────────────────────────────────────────┐
│                 Textual TUI (async)                      │
│  ┌────────────┬──────────────────────────────────────┐   │
│  │ Mana Tree  │ Chat / Conversation (streaming)      │   │
│  │ + Backlinks│ + Markdown rendering                 │   │
│  │            │ + Inline chart/image display         │   │
│  ├────────────┴──────────────────────────────────────┤   │
│  │ Status: provider/model │ manas │ tools │ profile  │   │
│  └───────────────────────────────────────────────────┘   │
├──────────────────────────────────────────────────────────┤
│                      Agent Core                          │
│  ┌────────────┐  ┌────────────┐  ┌──────────────────┐    │
│  │ LLM Client │  │ Tool Loader│  │ Context Manager  │    │
│  │ (2 impls)  │  │ (YAML+Py)  │  │ (NAV + log)      │    │
│  │ +Profiles  │  │ +built-ins │  │ +cross-mana      │    │
│  └────────────┘  └────────────┘  └──────────────────┘    │
│  ┌────────────┐  ┌────────────┐  ┌──────────────────┐    │
│  │ Git Manager│  │ Chart Eng. │  │ Source Watcher   │    │
│  │ (auto-cmit)│  │ (matplotlib)│ │ (fsevents)       │    │
│  └────────────┘  └────────────┘  └──────────────────┘    │
├──────────────────────────────────────────────────────────┤
│              Federated Mana Layer                        │
│                                                          │
│  Registered Manas (each is an independent directory):    │
│  ┌──────────────┐ ┌──────────────┐ ┌──────────────┐      │
│  │ ~/research/  │ │ ~/personal/  │ │ ~/work/      │      │
│  │  NAV.md ✓    │ │  NAV.md ✓    │ │  NAV.md ✓    │      │
│  │  raw/        │ │  raw/        │ │  raw/        │      │
│  │  pages/      │ │  pages/      │ │  pages/      │      │
│  │  schema.md   │ │  schema.md   │ │  schema.md   │      │
│  │  log.md      │ │  log.md      │ │  log.md      │      │
│  └──────────────┘ └──────────────┘ └──────────────┘      │
│                                                          │
│  Meta-Layer (unified view across all manas):             │
│  ┌────────────────────────────────────────────────┐      │
│  │ Unified search │ Cross-mana refs │ Master view │      │
│  └────────────────────────────────────────────────┘      │
└──────────────────────────────────────────────────────────┘
```

---

## Federated Mana System

### Mana Discovery Convention

A directory becomes an Agastya mana if and only if it contains a **`NAV.md`** file at its root. This file serves as:
1. **Identity marker** — signals "this is an Agastya mana"
2. **Navigation index** — the table of contents / directory map for the agent to crawl
3. **Agent-optimized** — structured so the LLM can efficiently find relevant pages without reading everything

Manas are **registered** with Agastya (stored in `~/.agastya/manas.yaml`):
```
> mana register /path/to/my-research
> mana list
> mana init /path/to/new-project
```

### Mana Directory Structure

Each mana is an independent directory (may or may not be its own git repo):

```
my-research/
├── NAV.md              # Navigation index (REQUIRED — makes this a mana)
├── schema.md           # LLM conventions for this mana's domain
├── log.md              # Chronological activity log
├── inbox.md            # Append-and-review inbox
├── raw/                # Immutable source documents
│   ├── articles/       # .md files (clipped articles, notes)
│   ├── books/          # .epub files
│   └── assets/         # Images, PDFs, etc.
├── blogs/              # User-controlled blog posts (toggleable)
│   ├── blog-1/
│   │   ├── draft.md
│   │   └── published.md
│   └── blog-2/
│       └── draft.md
├── tweets/             # Generated tweets, numbered (toggleable)
│   ├── 1.scaling-laws-insight.md
│   ├── 2.attention-mechanism-explained.md
│   └── 3.new-paper-summary.md
├── pages/              # LLM-generated knowledge pages
│   ├── transformers.md
│   ├── scaling-laws.md
│   └── assets/
│       └── charts/     # Generated matplotlib charts
└── .agastya/           # Mana-local config & state
    └── state.json      # Last sync, commit hash, etc.
```

### NAV.md Structure

Optimized for agent crawling (inspired by Farzapedia: the agent reads NAV.md first, then drills into specific pages):

```markdown
# Research Mana

> Domain: Machine Learning Research
> Created: 2026-04-05
> Sources: 23 | Pages: 47

## Navigation

### Core Concepts
- [Transformers](pages/transformers.md) — Architecture, attention, positional encoding
- [Scaling Laws](pages/scaling-laws.md) — Chinchilla, compute-optimal training

### Source Summaries
- [Attention Is All You Need](pages/summaries/attention-paper.md)
- [Scaling Laws for Neural LMs](pages/summaries/scaling-paper.md)

### Analysis
- [Attention vs SSM Comparison](pages/analysis/attn-vs-ssm.md)

## Cross-Mana Links
- Related to [Personal/Learning Goals](agastya://personal/pages/goals.md)
```

### Operating Modes

Agastya operates in one of two modes. The user can switch between them freely at any time:

#### 1. Focused Mode (`mana focus <name>`)
- Agent operates within a **single mana** only
- All queries, ingests, searches, and context are scoped to that one mana
- Sidebar shows only that mana's tree
- Status bar shows: `📍 research (focused)`
- Useful for deep research sessions where cross-mana noise is unwanted

#### 2. Unified Mode (`mana unfocus` or default)
- Agent has access to **all registered manas** via the virtual meta-layer
- Queries search across all manas simultaneously
- Cross-mana references work: `agastya://mana-name/path` URI scheme
- Agent reads NAV.md from each relevant mana for context
- Sidebar shows all manas
- Status bar shows: `🌐 unified (3 manas)`
- **No separate "master mana" directory** — the meta-layer is computed, not stored
- This is the **default mode** on startup

#### Connections Are Always Unified
**Regardless of which mode the user is in**, all connections (backlinks, cross-references, `agastya://` links) are created at the **unified level** — never scoped to a single mana. If the agent discovers a relationship between a page in the focused mana and a page in another mana, it creates that link. The connection graph is always global.

This means:
- Working in focused mode on `research` and ingesting a paper that relates to `personal/goals.md` → the cross-mana link is still created
- The backlinks panel in focused mode still shows links **from** other manas pointing **to** the current page
- `lint` in focused mode still detects cross-mana contradictions

#### Switching
```
> mana focus research     # Enter focused mode on 'research' mana
> mana unfocus            # Return to unified mode
```
Or via keyboard: `Ctrl+W` opens mana picker — selecting one enters focused mode, pressing `Esc` goes back to unified.

### Git Auto-Commit

After every mana-modifying operation (ingest, file from inbox, lint fixes, etc.):
1. Agent stages changed files in the mana directory
2. Auto-commits with a descriptive message: `agastya: ingest "Attention Is All You Need" — updated 4 pages`
3. Does NOT auto-push (user controls remote sync)
4. If the mana dir is not a git repo, Agastya offers to initialize one

### External Editor Compatibility (Obsidian / VS Code)

At any point, the user can open a mana directory in **Obsidian** (for markdown previews, graph view, reading) or **VS Code** (for editing) and make changes directly. Agastya must handle this gracefully.

**Design rules to ensure compatibility:**
- **Everything is plain markdown** — no proprietary formats, no databases, no binary state files. Any tool that reads `.md` files will work.
- **No lock files** — Agastya never locks files. Multiple tools can read/write simultaneously.
- **YAML frontmatter** is standard — Obsidian already understands it (tags, aliases, etc.)
- **Wikilinks** use standard `[text](relative/path.md)` markdown links — compatible with both Obsidian and VS Code markdown preview
- **`NAV.md`** is just a markdown file — renders fine in Obsidian as a linked table of contents
- **Cross-mana links** (`agastya://`) degrade gracefully in external editors — they show as plain text links, not broken

**When the user edits externally:**
1. The **file watcher** (already watching `raw/`) also watches the entire mana directory
2. Agastya detects the external change and notifies: *"External edit detected: `pages/scaling-laws.md` was modified outside Agastya"*
3. On next interaction, Agastya **reconciles**:
   - Updates `NAV.md` if new pages were added/removed
   - Refreshes backlinks if links changed
   - Updates `log.md` with the external edit event
4. If a file was edited while Agastya was also about to write to it → Agastya shows a diff and asks the user which version to keep

**Obsidian-specific notes:**
- Mana directories work as Obsidian vaults out of the box (just "Open folder as vault")
- Obsidian's graph view naturally visualizes the backlink structure
- Tags in YAML frontmatter are searchable in Obsidian
- The `blogs/` and `tweets/` directories render as normal markdown in Obsidian

---

## LLM Provider System

Multi-provider support via unified abstraction. Two API client implementations:

| Provider | API Pattern | Base URL | Notes |
|----------|------------|----------|-------|
| OpenAI | OpenAI-compatible | Default | GPT-4o, o1, etc. |
| Gemini | OpenAI-compatible | `generativelanguage.googleapis.com` | Via OpenAI-compat endpoint |
| Claude | Anthropic SDK | Default | Sonnet, Opus, etc. |
| Ollama Local | OpenAI-compatible | `localhost:11434` | Local models |
| Ollama Cloud | OpenAI-compatible | Custom URL | Cloud-hosted Ollama |
| OpenRouter | OpenAI-compatible | `openrouter.ai/api/v1` | Access to every model |

### Session Profiles

```yaml
# ~/.agastya/config.yaml
profiles:
  fast:
    provider: openai
    model: gpt-4o-mini
    description: "Quick queries, low cost"
  deep:
    provider: anthropic
    model: claude-sonnet-4-20250514
    description: "Complex analysis, ingest"
  local:
    provider: ollama
    model: llama3.3
    base_url: http://localhost:11434
    description: "Offline, private"
  open:
    provider: openrouter
    model: meta-llama/llama-3.3-70b
    description: "Via OpenRouter"

default_profile: fast
```

Switch at runtime: `> profile deep` or `Ctrl+1/2/3`

---

## Tool System (Direct Shell Access)

### Core Principle

The model has **direct access to shell commands** — no wrappers, no YAML/Python tool abstractions. The model composes the exact shell command it needs and presents it to the user for confirmation.

**Every command requires user confirmation before execution.**

### Confirmation Flow

```
Model: I need to search for "attention" across your research mana.
       Run: rg --no-heading "attention" ~/research/pages/

       [✓ Run] [✗ Deny] [✎ Edit]
```

- **✓ Run** — Command executes, output returned to model
- **✗ Deny** — Model is notified of denial. It will:
  1. Try an **alternative approach** if one exists (different command, different strategy)
  2. **Stop and explain** if no other way is possible
- **✎ Edit** — User can modify the command before confirming

### Tool Descriptions (Optional Knowledge Files)

`~/.agastya/tools/` contains **description files** — not executable wrappers, but reference documents that help the LLM understand how to use specific tools or workflows.

**`~/.agastya/tools/0.TOOLS_MANIFEST.md`** — index of available descriptions:

```markdown
# Available Tool Descriptions

| Tool | Description |
|------|-------------|
| `ripgrep` | Fast text search with regex support |
| `ffmpeg` | Audio/video processing |
| `pandoc` | Document format conversion |
| `jq` | JSON querying and manipulation |
```

When the LLM needs to use an unfamiliar tool, it reads the relevant description file from `~/.agastya/tools/` for guidance. For well-known tools (grep, cat, ls, git, etc.), the LLM uses its own pre-existing knowledge directly.

**Example description file:** `~/.agastya/tools/pandoc.md`
```markdown
# pandoc — Document Converter

## Common Recipes
- MD → PDF: `pandoc input.md -o output.pdf --pdf-engine=weasyprint`
- EPUB → MD: `pandoc input.epub -t markdown -o output.md`
- MD → HTML: `pandoc input.md -s -o output.html`

## Notes
- Use `--pdf-engine=weasyprint` for PDF (installed globally)
- Use `-s` flag for standalone HTML with proper headers
```

### How It Works

```
Startup:
  1. Read ~/.agastya/tools/0.TOOLS_MANIFEST.md
  2. Inject tool descriptions summary into LLM system prompt
  3. LLM now knows what reference docs are available

At runtime:
  1. LLM decides it needs to perform an action
  2. If unfamiliar tool: reads description file from ~/.agastya/tools/
  3. LLM composes the exact shell command
  4. Command presented to user for confirmation
  5. User confirms → execute → output returned to LLM
  6. User denies → LLM tries alternative or stops
```

### Built-in Operations

These are handled by the agent core directly (no shell, no confirmation needed):

| Operation | Description |
|-----------|-------------|
| `read_file` | Read a mana page, source file, or NAV.md |
| `write_file` | Create or update a mana page |
| `list_directory` | List files in any mana directory |
| `append_inbox` | Add an entry to a mana's inbox.md |
| `read_inbox` | Read inbox contents |

### Chart Generation (render_chart)

Special built-in — generates charts without requiring user confirmation per command:

1. LLM writes matplotlib/seaborn code as a string parameter
2. Agent creates temp Python script, appends `plt.savefig()`
3. Executes in **isolated subprocess** (timeout: 30s, sandboxed to mana's assets dir)
4. Returns image path. LLM references: `![Chart](assets/charts/name.png)`
5. Pre-installed in subprocess env: `matplotlib`, `seaborn`, `numpy`, `pandas`

---

## Source Ingest Formats

### MVP Formats

| Format | Method | Notes |
|--------|--------|-------|
| `.md` (Markdown) | Direct read | Primary format, zero conversion needed |
| `.epub` (Books) | `ebooklib` + extraction | Extract chapters as markdown, images to assets |

### Future Formats (Phase 2+)

| Format | Method | Notes |
|--------|--------|-------|
| `.pdf` | `pymupdf` / `pdfplumber` | Text extraction |
| Images | LLM Vision API | Send to multimodal model for analysis |
| Audio | Whisper (local/API) | Transcribe, then ingest transcript |
| URLs | `httpx` + `markdownify` | Scrape and convert (via web_scrape tool) |

### Epub Ingest Flow

When user ingests an `.epub`:
1. Extract book metadata (title, author, chapters)
2. Convert each chapter to markdown
3. Store originals in `raw/books/`
4. Create per-chapter summary pages in `pages/`
5. Create a master book page with chapter index, themes, characters
6. Update NAV.md with the book entry
7. Auto-commit

---

## Append-and-Review System

Each mana has its own `inbox.md`. Global inbox at `~/.agastya/inbox.md`.

### Commands

- **`append <note>`** — Prepend timestamped entry to inbox. Zero friction.
- **`review`** — Surface sinking items. For each: promote / file / archive / skip.
- **Smart suggestions** during review.

### Gravity Model

New items at top → untouched items sink → promoted items jump back up → archived items move to `archive.md`.

---

## Confirmed Features

### 1. Daily Briefing ✅
On startup, Agastya shows:
- Mana status (page count, source count, last activity per mana)
- Inbox items needing attention (sinking items count)
- Suggested actions ("Paper X ingested 3 days ago but no analysis page exists")

### 2. Source Watcher ✅
File system watcher on each mana's `raw/` directory:
- Drop a file in → Agastya notifies: "New source detected: `paper.md`. Ingest now?"
- Uses macOS `fsevents` (via `watchfiles` Python package)
- Non-blocking notification in status bar

### 3. Session Profiles ✅
Quick switch between LLM models:
- Named profiles in config (fast/deep/local/open)
- One keybinding or command to switch: `> profile deep`
- Status bar shows current profile

### 4. Conversation Persistence ✅
- Conversations saved to `~/.agastya/conversations/`
- Resume previous conversations: `> resume` or `Ctrl+L`
- Each conversation stores: messages, context (which mana, which pages were read)

### 5. Backlinks Panel ✅
- When a page is referenced in chat, show all pages that link TO it
- Visible in the sidebar below the mana tree
- Helps understand knowledge structure and connections

### 6. Conflict Detection ✅
During ingest, if new source contradicts existing mana content:
```
⚠️ Conflict Detected:
  Source: "New Scaling Paper 2026"
  Claims: Chinchilla scaling laws are suboptimal by 2x

  Existing: pages/research/scaling-laws.md (line 34)
  States: Chinchilla provides compute-optimal training ratios

  How should I handle this?
  [1] Update with new findings (mark old as superseded)
  [2] Add both perspectives with discussion
  [3] Flag for manual review
```

### 8. Tagging System ✅
YAML frontmatter tags on mana pages:
```markdown
---
tags: [rlhf, alignment, safety]
sources: [paper-123, paper-456]
created: 2026-04-05
updated: 2026-04-05
confidence: high
---
```
Queryable: `> search tags:rlhf` or `> pages where confidence=low`

### 9. Export System ✅ (PDF & MD only)
- **Single page** → PDF or compiled markdown
- **Entire mana** → compiled markdown (all pages merged with cross-refs resolved)
- **Selection** → PDF export
- Uses `weasyprint` or `md-to-pdf` for PDF generation

### 10. Blog Generation ✅ (Toggleable)

A feature the user can toggle on/off. When enabled:

**How it works:**
- Each mana has a `blogs/` directory containing blog post directories.
- After **every agent action** (ingest, query, lint, summary creation, etc.), the user is prompted: *"Would you like to add this to a blog?"*
- The model does **NOT** keep blog state in memory — it accesses blogs **only through shell commands** (cat, ls, grep, etc.).
- Each blog is a directory: `blogs/<blog-name>/` containing `draft.md` and optionally `published.md`.
- The model **always asks before making any change** to blog content.
- The model **suggests quality improvements** — better structure, clarity, content flow — but only applies changes with user confirmation.

**Blog workflow:**
```
User action (e.g., ingest a paper)
  → Agent processes the source
  → Agent asks: "Add findings to a blog? [y/n/which blog?]"
  → If yes:
    → Agent reads current blog state via shell (cat blogs/ml-research/draft.md)
    → Suggests additions/edits
    → User confirms/rejects each change
    → Agent writes updates via shell
    → Git auto-commit
```

**Blog structure:**
```
blogs/
├── ml-research/
│   ├── draft.md          # Working draft (agent + user edit this)
│   ├── published.md      # Finalized version (user publishes manually)
│   └── assets/           # Images, charts referenced by this blog
├── personal-growth/
│   └── draft.md
└── reading-notes/
    └── draft.md
```

**Key rules:**
- Model never modifies blogs without asking
- Model suggests positive changes (improve quality, add context, better structure)
- User can say "stop asking about blogs" to disable prompts for the session
- Feature toggle in config: `features.blog_generation: true/false`

### 11. Tweet Generation ✅ (Toggleable)

A feature the user can toggle on/off. Driven by a `TWEET_GENERATION.md` config file.

**How it works:**
- A `TWEET_GENERATION.md` file defines the user's tweet style, voice, guidelines, and preferences.
- When the feature is toggled on, the agent can generate tweet drafts based on mana content, discoveries, or user prompts.
- The agent accesses this file to understand the user's tone, structure, and rules.

**TWEET_GENERATION.md lifecycle:**
1. If the feature is toggled on and `TWEET_GENERATION.md` **exists**: agent uses it.
2. If toggled on but the file **doesn't exist**: agent asks the user if they want to provide one.
3. If user doesn't provide one: agent generates a default `TWEET_GENERATION.md` and asks for confirmation.
4. User can ask the agent to update the file as they learn new things about writing tweets.
5. Agent can **suggest edits** to the file but only applies them **with user confirmation**.
6. User can **lock the file** — after locking, the agent cannot suggest or make any changes to `TWEET_GENERATION.md`.

**Config:**
```yaml
# ~/.agastya/config.yaml
features:
  blog_generation: true
  tweet_generation: true
  tweet_generation_locked: false  # When true, TWEET_GENERATION.md cannot be modified
```

**Location:** `~/.agastya/TWEET_GENERATION.md` (global) or `<mana>/TWEET_GENERATION.md` (per-mana override)

---

## Deferred Features (Phase 2+)

| Feature | Reason for deferral |
|---------|-------------------|
| Multi-modal ingest (PDF, images, audio) | Adds complexity; .md and .epub cover most use cases initially |
| HTML site export | PDF + MD covers sharing needs for now |
| Marp slide deck export | Niche use case |
| Mana templates | Can be added once core is stable |
| Vector/semantic search | Grep + NAV.md sufficient at small-medium scale |

---

## TUI Design (Textual)

### Layout

```
┌──────────────────────────────────────────────────────────┐
│  🔱 Agastya                    [profile: deep] [Ctrl+Q] │
├────────────┬─────────────────────────────────────────────┤
│ MANAS      │  Chat                                      │
│            │                                             │
│ 📚 research│  You: What do I know about scaling laws?    │
│  📄 NAV    │                                             │
│  📂 pages/ │  Agastya: Based on your research mana,     │
│   📄 scale │  here's what I found across 3 pages...     │
│   📄 attn  │  [streaming markdown with citations]       │
│  📂 raw/   │                                             │
│            │  📊 [inline chart preview]                  │
│ 📚 personal│                                             │
│  📄 NAV    │  ──────────────────────────────────────     │
│  📂 pages/ │  > type here (or Ctrl+P for commands)      │
│            │                                             │
├────────────┤  BACKLINKS for: scaling-laws.md             │
│ Backlinks  │  ← transformers.md (line 23)               │
│ (context)  │  ← NAV.md (line 12)                        │
│            │  ← analysis/compute.md (line 8)             │
├────────────┴─────────────────────────────────────────────┤
│ 🟢 anthropic/claude-sonnet │ 🌐 unified │ 12 tools │ ✉5│
└──────────────────────────────────────────────────────────┘
```

### Keyboard Shortcuts

| Shortcut | Action |
|----------|--------|
| `Ctrl+P` | Command palette |
| `Ctrl+I` | Ingest source |
| `Ctrl+A` | Quick append to inbox |
| `Ctrl+R` | Review inbox |
| `Ctrl+S` | Search across manas |
| `Ctrl+W` | Switch active mana |
| `Ctrl+1/2/3` | Switch profile (fast/deep/local) |
| `Ctrl+L` | List/resume conversations |
| `Ctrl+Q` | Quit |

---

## Core Commands

| Command | Description |
|---------|-------------|
| `ingest <source>` | Process a source into the active mana |
| `query <question>` | Ask across manas, get synthesized answer |
| `lint` | Health-check: contradictions, orphans, stale pages |
| `append <note>` | Quick capture → inbox |
| `review` | Surface sinking inbox items |
| `search <term>` | Full-text search across all manas |
| `status` | Mana stats + daily briefing |
| `profile <name>` | Switch LLM profile |
| `mana register <path>` | Register a new mana directory |
| `mana list` | List all registered manas |
| `mana init <path>` | Initialize a new mana (creates NAV.md, schema.md, dirs) |
| `mana focus <name>` | Enter focused mode — scope everything to one mana |
| `mana unfocus` | Return to unified mode — access all manas |
| `export <format>` | Export current mana/page (pdf/md) |
| `resume` | Resume a previous conversation |
| (natural chat) | Free-form conversation with the agent |

---

## Context Management

### Phase 1 (MVP)

**Focused Mode:**
- Agent reads `schema.md` of the focused mana at startup (system prompt)
- Agent reads `NAV.md` of that mana for orientation
- Agent uses `read_file` tool to drill into specific pages as needed
- `log.md` provides recent history context
- All operations (ingest, search, query, append) are scoped to the focused mana only

**Unified Mode:**
- Agent reads `schema.md` from the last-used mana (or a configured default)
- On each interaction, agent reads `NAV.md` from all registered manas for orientation
- Agent uses `read_file` tool to drill into specific pages across any mana
- Cross-mana references (`agastya://mana-name/path`) are resolved
- `log.md` from each mana provides per-mana history context

### Phase 2 (Scale)

- Local search tool (BM25/TF-IDF) per mana
- Optional: vector embeddings for semantic search (FAISS, local)

---

## Tech Stack & Dependencies

| Category | Choice | Reason |
|----------|--------|--------|
| Language | Python 3.12+ | Async support, user preference |
| Package Manager | `uv` | Fast, familiar |
| TUI Framework | `textual` | Async TUI, rich rendering |
| LLM (OpenAI-compat) | `openai` SDK | Covers 5/6 providers |
| LLM (Anthropic) | `anthropic` SDK | For Claude |
| YAML Parsing | `pyyaml` | Config files |
| HTTP Client | `httpx` | Async, for tools |
| Charts | `matplotlib`, `seaborn` | Chart generation |
| Data | `numpy`, `pandas` | Available in chart subprocess |
| Epub | `ebooklib` | .epub parsing and extraction |
| Git | `gitpython` | Auto-commit |
| File Watching | `watchfiles` | Source watcher (fsevents on macOS) |
| PDF Export | `weasyprint` or `md-to-pdf` | Export feature |
| CLI Entry | `typer` | Non-TUI entry points |

### Packaging (Future)

```toml
# pyproject.toml
[project]
name = "agastya"
version = "0.1.0"
description = "LLM-powered knowledge agent with persistent, compounding manas"

[project.scripts]
agastya = "agastya.cli:app"
```

- Install: `pip install agastya`
- Setup: `agastya init` → creates first mana
- Run: `agastya` → launches TUI

---

## Project Structure (Agastya Source Code)

```
agastya/
├── pyproject.toml
├── README.md
├── src/
│   └── agastya/
│       ├── __init__.py
│       ├── cli.py              # Typer CLI (init, run, mana register, etc.)
│       ├── core/
│       │   ├── agent.py        # Agent loop: input → LLM → tool calls → respond
│       │   ├── context.py      # Context manager: reads NAVs, manages mana context
│       │   ├── config.py       # Config loading, profiles, mana registry
│       │   └── conversation.py # Conversation persistence (save/resume)
│       ├── llm/
│       │   ├── base.py         # LLMClient protocol
│       │   ├── openai_client.py    # OpenAI-compatible client
│       │   └── anthropic_client.py # Anthropic client
│       ├── shell/
│       │   ├── executor.py     # Shell command execution with confirmation UX
│       │   └── chart.py        # render_chart (matplotlib subprocess)
│       ├── builtins/
│       │   ├── file_ops.py     # read_file, write_file, list_directory
│       │   └── inbox.py        # append_inbox, read_inbox
│       ├── mana/
│       │   ├── manager.py      # Mana registry, discovery, validation
│       │   ├── nav.py          # NAV.md parsing and generation
│       │   ├── git.py          # Git auto-commit logic
│       │   ├── inbox.py        # Inbox management (append, review, gravity)
│       │   ├── ingest.py       # Source ingestion (md, epub)
│       │   ├── export.py       # Export (pdf, md)
│       │   └── watcher.py      # File system watcher for raw/ directories
│       ├── features/
│       │   ├── blog.py         # Blog generation (toggleable)
│       │   └── tweets.py       # Tweet generation (toggleable)
│       ├── tui/
│       │   ├── app.py          # Main Textual App
│       │   ├── screens/
│       │   │   ├── main.py     # Main screen (chat + sidebar)
│       │   │   ├── review.py   # Inbox review screen
│       │   │   └── briefing.py # Daily briefing screen
│       │   ├── widgets/
│       │   │   ├── chat.py     # Chat panel (streaming markdown)
│       │   │   ├── mana_tree.py    # Mana tree sidebar
│       │   │   ├── backlinks.py    # Backlinks panel
│       │   │   ├── status_bar.py   # Status bar
│       │   │   └── command_palette.py # Command palette
│       │   └── styles/
│       │       └── app.tcss    # Textual CSS styles
│       └── utils/
│           ├── markdown.py     # Markdown utilities
│           ├── epub.py         # Epub extraction utilities
│           └── fs.py           # File system helpers
├── tools/                      # Default global tools (shipped with Agastya)
│   ├── web_scrape.py
│   └── search_files.yaml
└── tests/
    ├── test_agent.py
    ├── test_tools.py
    └── test_mana.py
```

---

## All Decisions Summary

| # | Topic | Decision |
|---|-------|----------|
| 1 | LLM Providers | Multi-provider: OpenAI, Gemini, Claude, Ollama (local+cloud), OpenRouter |
| 2 | Tool System | Manifest-based (`TOOLS_MANIFEST.md`) + lazy loading. YAML + Python tools. Global + mana-local. |
| 3 | Knowledge Base Structure | Federated manas. Any dir with `NAV.md` = mana. Registered in `~/.agastya/manas.yaml` |
| 4 | Append-and-Review | Per-mana inbox + global inbox. Gravity model. |
| 5 | Terminal UI | Textual TUI with mana tree, chat, backlinks, command palette |
| 6 | Git Integration | Auto-commit after every mana-modifying operation. No auto-push. |
| 7 | Charts | Built-in `render_chart` tool, matplotlib in isolated subprocess |
| 8 | Project Name | **Agastya** |
| 9 | Distribution | Future `pip install agastya` |
| 10 | Terminology | "wiki" → **mana** throughout |
| 11 | Config Location | `~/.agastya/` |
| 12 | Source Formats (MVP) | `.md` and `.epub` |
| 13 | Export Formats (MVP) | PDF and compiled markdown |
| 14 | Features (MVP) | Daily briefing, source watcher, session profiles, conversation persistence, backlinks, conflict detection, tagging, export (pdf+md) |
| 15 | Blog Generation | Toggleable. `blogs/` dir per mana. Prompt after every action. User confirms all changes. Model accesses via shell only. |
| 16 | Tweet Generation | Toggleable. Driven by `TWEET_GENERATION.md`. User can lock file. Model suggests edits only with confirmation. |

---

## Discussion Complete — Ready for Feature Prioritization

### Full Feature List for MVP vs Phase 2 Decision

**Core Operations:**
1. `ingest` — process source → update mana pages
2. `query` — ask questions → synthesize from mana
3. `lint` — health-check mana (contradictions, orphans, stale)
4. `append` / `review` — inbox system
5. `search` — full-text across manas

**Agent Infrastructure:**
6. Multi-provider LLM client (OpenAI-compat + Anthropic)
7. Tool auto-discovery (YAML + Python)
8. Built-in tools (file ops, search, inbox, chart, git)
9. Context management (NAV.md + schema.md)
10. Git auto-commit

**TUI:**
11. Chat panel with streaming markdown
12. Mana tree sidebar
13. Backlinks panel
14. Command palette
15. Status bar
16. Keyboard shortcuts

**Features:**
17. Daily briefing on startup
18. Source watcher (fsevents on raw/)
19. Session profiles (fast/deep/local)
20. Conversation persistence (save/resume)
21. Conflict detection during ingest
22. Tagging system (YAML frontmatter)
23. Export (PDF + MD)
24. Epub ingest support
25. Blog generation (toggleable — prompt after every action)
26. Tweet generation (toggleable — TWEET_GENERATION.md driven)

**→ User: All of these are confirmed for MVP. Ready for implementation planning when you say go.**
