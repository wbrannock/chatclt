# chatclt — Capstone RAG Chat

Our capstone project: a PDF-grounded chat app for querying a medical / laboratory literature corpus (pathology, immunology, hematology, clinical chemistry, molecular genetics, synthetic procedures). Built on a fork of [Cinnamon/kotaemon](https://github.com/Cinnamon/kotaemon) with our own UI theming, chat flow tweaks, and model defaults.

- **Chat model**: `anthropic/claude-sonnet-4-6` via [OpenRouter](https://openrouter.ai) (one key, any model)
- **Embeddings**: FastEmbed `BAAI/bge-small-en-v1.5` — runs locally on CPU, no key needed
- **Reranking**: off by default (optional Cohere key)
- **Vector store / index**: local, persisted in `ktem_app_data/` — survives restarts
- **Auth**: local login, default `admin` / `admin`

For upstream kotaemon documentation, see https://github.com/Cinnamon/kotaemon.

---

## Prerequisites

- macOS or Linux (Apple Silicon works)
- [uv](https://docs.astral.sh/uv/) — install with `curl -LsSf https://astral.sh/uv/install.sh | sh` or `brew install uv`
- Git
- An **OpenRouter** API key — sign up at https://openrouter.ai/keys (free tier works to start; add credit for Claude Sonnet)

uv manages Python itself — you do **not** need conda or a pre-installed Python. Disk: the venv is ~4 GB. Indexed PDFs add ~100 MB per few dozen files.

---

## 1. Clone the repo

```bash
git clone https://github.com/wbrannock/chatclt.git
cd chatclt
```

Optional — track the upstream kotaemon project so we can pull fixes:

```bash
git remote add upstream https://github.com/Cinnamon/kotaemon.git
```

## 2. Install dependencies with uv

```bash
uv sync
```

That one command:
- Installs Python 3.10 (pinned in `.python-version`) if you don't have it
- Creates `.venv/` in the repo root
- Installs every dep from `uv.lock` — **exact versions everyone on the team gets**
- Installs the `libs/kotaemon` and `libs/ktem` workspaces in editable mode, so your code edits apply immediately

First run takes ~1–3 minutes (fast — uv uses a global cache and parallel downloads). Subsequent `uv sync` calls are near-instant.

You have two options for activation:

- **Prefix with `uv run`** (recommended, no activation needed):
  ```bash
  uv run python app.py
  ```
- **Activate the venv** the old-school way:
  ```bash
  source .venv/bin/activate
  python app.py
  ```

To wipe and rebuild:

```bash
rm -rf .venv
uv sync
```

## 3. Configure your API key

```bash
cp .env.example .env
```

Open `.env` and set these four lines (delete or ignore the rest):

```env
OPENAI_API_BASE=https://openrouter.ai/api/v1
OPENAI_API_KEY=sk-or-v1-...your-openrouter-key...
OPENAI_CHAT_MODEL=anthropic/claude-sonnet-4-6
OPENAI_EMBEDDINGS_MODEL=text-embedding-3-large
```

We're pointing the "OpenAI" variables at OpenRouter because OpenRouter is API-compatible — this lets us swap models (Claude, GPT, Llama, etc.) by changing one line. Embeddings still run locally via FastEmbed, so `OPENAI_EMBEDDINGS_MODEL` is just a placeholder.

**`.env` is gitignored. Never commit it. Never share your key in Slack / commits / screenshots.**

Optional:
- Reranking: add `COHERE_API_KEY=...` to `.env`
- Different chat model: change `OPENAI_CHAT_MODEL` to any OpenRouter model id (e.g. `openai/gpt-4o-mini`, `meta-llama/llama-3.1-70b-instruct`)

## 4. Run the app

From the repo root:

```bash
PDFJS_PREBUILT_DIR="$(pwd)/libs/ktem/ktem/assets/prebuilt/pdfjs-4.0.379-dist" uv run python app.py
```

Open **http://localhost:7860** and log in as `admin` / `admin`.

Stop the app with `Ctrl+C` in the terminal.

---

## Using the app

1. **Files** tab → upload PDFs (drag-and-drop works). Indexing runs once per file; progress shows in the UI.
2. **Chat** tab → ask questions. Answers cite the source PDF and page.
3. **File Collection** panel on the left of Chat → check the files you want in scope for the current question. Leave all unchecked to search everything.
4. **Chat settings** (bottom of the Chat tab) → change reasoning method (`simple`, `complex`, `ReAct`, etc.), model, and response language.

### Our PDF corpus

Sample PDFs live **outside the repo** at `../sample_rag_pdfs/`, grouped by subject:

| Folder | Files |
| --- | --- |
| pathology | 33 |
| synthetic_procedures | 16 |
| immunology | 5 |
| hematology | 4 |
| clinical_chemistry | 4 |
| molecular_genetics | 2 |

Upload whichever subset you're working with. Indexed content is stored in `ktem_app_data/` (gitignored) and survives restarts — you don't need to re-upload every time.

---

## Project layout (what's ours vs upstream)

```
chatclt/
├── app.py                    # entrypoint (upstream)
├── flowsettings.py           # ← OUR defaults (OpenRouter, FastEmbed, etc.)
├── pyproject.toml            # uv workspace root
├── uv.lock                   # locked dep versions — commit changes
├── .python-version           # pins Python 3.10
├── README.md                 # ← this file
├── START_HERE.md             # quick start cheatsheet
├── .env.example              # template for .env
├── libs/
│   ├── kotaemon/             # RAG engine (upstream, editable workspace member)
│   └── ktem/                 # web UI (upstream, editable workspace member)
│       └── ktem/
│           ├── assets/       # ← OUR theme, CSS, JS, favicon tweaks
│           ├── pages/chat/   # ← OUR chat panel tweaks
│           └── reasoning/    # ← OUR reasoning flow tweaks
└── ktem_app_data/            # local index + uploads (gitignored)
```

If you're changing behavior: `flowsettings.py` for model/embedding config, `libs/ktem/ktem/assets/theme.py` + `main.css` for look and feel, `libs/ktem/ktem/reasoning/simple.py` for how answers are generated.

### Managing dependencies

- Add a dep: `uv add <package>` (adds to `pyproject.toml` + `uv.lock`)
- Add to a workspace member: `uv add --package kotaemon <package>`
- Update everything: `uv lock --upgrade && uv sync`
- **Commit `uv.lock`** whenever it changes — that's what keeps the team in sync.

---

## Git workflow for teammates

```bash
git checkout -b your-name/short-feature-description
# ...edit, test locally...
git add <specific files>
git commit -m "feat: what you changed"
git push -u origin your-name/short-feature-description
```

Open a PR on GitHub targeting `main`. Get one review before merging.

**Never commit**: `.env`, `ktem_app_data/`, `.venv/`, `__pycache__/`, `*.pyc`, anything under `libs/*/cache/`.

Pull upstream kotaemon changes (optional, occasional):

```bash
git fetch upstream
git merge upstream/main        # or rebase — talk to the team first
uv sync                        # resync after a merge that touches deps
```

---

## Troubleshooting

- **`uv: command not found`** — install it: `brew install uv` or `curl -LsSf https://astral.sh/uv/install.sh | sh`, then restart your shell.
- **`uv sync` fails on a single package** — run `uv sync --reinstall` to wipe and retry.
- **`ModuleNotFoundError` after running** — you ran `python app.py` instead of `uv run python app.py`, or didn't activate `.venv`.
- **`PDFJS_PREBUILT_DIR` path issue** — launch from the repo root; the `$(pwd)` in the run command assumes it.
- **Port 7860 in use** — `GRADIO_SERVER_PORT=7861 uv run python app.py`
- **401 from OpenRouter** — your key is wrong, or you left `OPENAI_API_BASE` pointed at `api.openai.com`. Both need to match step 3.
- **Slow / repeated indexing** — make sure `ktem_app_data/` exists and is writable; deleting it forces a full reindex.
- **Lockfile conflicts on merge** — don't hand-edit `uv.lock`. Accept one side of the merge, then run `uv lock` to regenerate cleanly.

Questions → ping the team chat. Bugs in our customizations → open an issue on this repo.
