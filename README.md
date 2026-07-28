# chatclt — A RAG System for the UVA Pathology Department
## UVA MSDS Capstone Project 2026
### Team: Edward Anderson, William Brannock, Samuel Kunitz-Levy, Nathan Todd and Will Novak

ChatCLT: a PDF-grounded chat app for querying a medical / laboratory literature corpus (pathology, immunology, hematology, clinical chemistry, molecular genetics, synthetic procedures). Built on a fork of [Cinnamon/kotaemon](https://github.com/Cinnamon/kotaemon) with our own UI theming, local chat flow tweaks, and model defaults.

- **Chat models**: Gemma 4 26B A4B, Qwen3 14B, and Mistral Small 3.2 24B — runnable locally via [Ollama](https://ollama.com) (see [Local models via Ollama](#local-models-via-ollama-fully-offline)) or remotely via [OpenRouter](https://openrouter.ai) (one key, any model; `anthropic/claude-sonnet-4-6` available as a strong-baseline reference). Our model evaluation used the OpenRouter API because we didn't have access to a machine with enough unified memory to serve them locally. The target deployment is fully local on a Mac mini that the pathology department has. 

- **Embeddings**: FastEmbed `BAAI/bge-small-en-v1.5` — runs locally on CPU, no key needed
- **Reranking**: local cross-encoder `BAAI/bge-reranker-base` (Apple Metal/CUDA/CPU, no key needed), on by default; optional Cohere rerank with a `COHERE_API_KEY`
- **Relevance scoring**: optional per-chunk LLM scoring using the selected chat model (shown in the info panel; turn off for local models — see performance tip below)
- **Vector store / index**: local, persisted in `ktem_app_data/` — survives restarts
- **Auth**: local login, default username is `admin` / default password is `admin`

---

## Prerequisites

- macOS or Linux (Apple Silicon recommended for LLM inference)
- [uv](https://docs.astral.sh/uv/) — install with `curl -LsSf https://astral.sh/uv/install.sh | sh`
- Github access
- OpenRouter API key (credit needed for remote model usage)
- [Ollama](https://ollama.com) for running chat models fully locally (no API key) — see [Local models via Ollama](#local-models-via-ollama-fully-offline)

uv manages Python installation and dependencies 

Disk: the venv is  roughly 4 GB. Indexed PDFs add ~100 MB per few dozen files.

---

## 1. Clone the repo

```bash
git clone https://github.com/wbrannock/chatclt.git
cd chatclt
```

## 2. Install dependencies with uv

```bash
uv sync
```

That one command:
- Installs Python 3.11 (pinned in `.python-version`) if you don't have it
- Creates `.venv/` in the repo root
- Installs every dep from `uv.lock` 
- Installs the `libs/kotaemon` and `libs/ktem` workspaces in editable mode

First run takes ~1–3 minutes (fast — uv uses a global cache and parallel downloads). Subsequent `uv sync` calls are near-instant because of caching.

Activation:

- **Prefix with `uv run`** (recommended, no activation needed):
  ```bash
  uv run python app.py
  ```


To wipe and rebuild the virtual environment if something breaks:

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

We're pointing the "OpenAI" variables at OpenRouter because OpenRouter is API-compatible. This lets us swap models (Claude, GPT, Llama, etc.) by changing one line. Embeddings still run locally via FastEmbed, so `OPENAI_EMBEDDINGS_MODEL` is just a placeholder.

**`.env` is gitignored. Never commit it. Make sure to never share**

Optional:
- Reranking: add `COHERE_API_KEY=...` to `.env`
- Different chat model: change `OPENAI_CHAT_MODEL` to any OpenRouter model id (e.g. `openai/gpt-4o-mini`, `meta-llama/llama-3.1-70b-instruct`)

### Local models via Ollama (fully offline)

For running against local models (e.g. on the Mac mini deployment), install [Ollama](https://ollama.com), pull the models you want, and list them in `.env`. The default set mirrors our eval models (as Ollama builds) plus the small on-device Gemma:

```bash
ollama pull gemma4:e4b             # Gemma 4 E4B (~10 GB) — small, fits modest hardware
ollama pull gemma4:26b             # Gemma 4 26B A4B (~16 GB) — eval model
ollama pull qwen3:14b              # Qwen3 14B (~9 GB) — eval model
ollama pull mistral-small3.2:24b   # Mistral Small 3.2 24B (~14 GB) — eval model
```

```env
LOCAL_MODELS=gemma4:e4b,gemma4:26b,qwen3:14b,mistral-small3.2:24b
LOCAL_MODELS_DEFAULT=true          # make the first one the app's default LLM
# LOCAL_MODEL_CTX=32768            # context window for the "-32k" variants
```

Only pull what your machine can hold — every listed model appears in the app's model dropdown, but a model errors at question time if its tag hasn't been pulled. Trim `LOCAL_MODELS` to match what you actually pulled.

Each model shows up twice in Chat settings: `ollama-gemma4-e4b` (OpenAI-compatible endpoint — streaming and tool-call citations, but the context window is whatever the Ollama server runs with) and `ollama-gemma4-e4b-32k` (pins the context window client-side so long retrieved evidence isn't truncated). For the first variant, start Ollama with a larger window:

```bash
OLLAMA_CONTEXT_LENGTH=32768 ollama serve
```

Everything else already runs locally by default: embeddings (FastEmbed), reranking (a local cross-encoder on Apple Metal/CUDA/CPU), and the LLM-based relevance scoring, which uses whatever chat model you selected. No API keys are needed in this mode.

**Performance tip:** "LLM relevant scoring" (Settings → Retrieval settings) makes one extra LLM call *per retrieved chunk* per question — 10 chunks means 10 extra calls. Remote APIs absorb those in parallel, but a local model runs them on the same GPU as the answer, so responses get dramatically slower. Untick it when using local models; the info panel then shows the cross-encoder's relevance scores instead. The first local question also pays some one-time model-download/load costs (fastembed, cross-encoder, fastText); later questions are faster.

## 4. Run the app

From the repo root:

```bash
PDFJS_PREBUILT_DIR="$(pwd)/libs/ktem/ktem/assets/prebuilt/pdfjs-4.0.379-dist" uv run python app.py
```

Open **http://localhost:7860** and log in as `admin` / `admin`.

Stop the app with `Ctrl+C` in the terminal.

---

## App Workflow

1. **Files** tab → upload PDFs (drag-and-drop works), paste web links, or use **Use Local Folder** to import a server-local folder. Indexing runs once per file; progress shows in the UI.
2. **Chat** tab → ask questions. Answers cite the source PDF and page.
3. **File Collection** panel on the left of Chat → check the files you want in scope for the current question. Leave all unchecked to search everything.
4. **Chat settings** (bottom of the Chat tab) → change reasoning method (`simple`, `complex`, `ReAct`, etc.), model, and response language.

### Our PDF corpus

The UVA medical laboratories PDF corpus lives outside the repo on a folder that can be imported into the system.


For the organized corpus, go to **Files** → **Use Local Folder**, enter `../datarepo/dc_1224400_uvahealthsystemmedicallaboratories_summary`, keep **Include subfolders** on, and keep **Create/update groups from folders** on if you want each folder to appear as a selectable group in Chat. Duplicate filenames are imported automatically by storing duplicate-name files under their relative folder path.

---

## Project File Layout 

```
chatclt/
├── app.py                    # entrypoint 
├── flowsettings.py           # defaults (OpenRouter, FastEmbed, etc.)
├── pyproject.toml            # uv workspace root
├── uv.lock                   # locked dep versions 
├── .python-version           # pins Python 3.11
├── README.md                 # you are here
├── .env.example              # template for .env
├── libs/
│   ├── kotaemon/             # RAG engine (upstream, editable workspace member)
│   └── ktem/                 # web UI (upstream, editable workspace member)
│       └── ktem/
│           ├── assets/       # Theme Files
│           ├── pages/chat/   # Chat panel tweaks
│           └── reasoning/    # Reasoning flow tweaks
└── ktem_app_data/            # local index + uploads (gitignored) (data storage)
```


### Managing dependencies

- Add a dep: `uv add <package>` (adds to `pyproject.toml` + `uv.lock`)
- Add to a workspace member: `uv add --package kotaemon <package>`
- Update everything: `uv lock --upgrade && uv sync`
- **Commit `uv.lock`** whenever it changes — that's what keeps the team in sync.

---


## Troubleshooting

Here are some bugs and quirks we ran into that may be useful for someone trying to deploy or extend this project.

- **`uv: command not found`** — install it: `brew install uv` or `curl -LsSf https://astral.sh/uv/install.sh | sh`, then restart your shell.
- **`uv sync` fails on a single package** — run `uv sync --reinstall` to wipe and retry.
- **`ModuleNotFoundError` after running** — you ran `python app.py` instead of `uv run python app.py`, or didn't activate `.venv`.
- **`PDFJS_PREBUILT_DIR` path issue** — launch from the repo root; the `$(pwd)` in the run command assumes it.
- **Port 7860 in use** — `GRADIO_SERVER_PORT=7861 uv run python app.py`
- **401 from OpenRouter** — your key is wrong, or you left `OPENAI_API_BASE` pointed at `api.openai.com`. Both need to match step 3.
- **Slow / repeated indexing** — make sure `ktem_app_data/` exists and is writable; deleting it forces a full reindex.
- **Lockfile conflicts on merge** — don't hand-edit `uv.lock`. Accept one side of the merge, then run `uv lock` to regenerate cleanly.
- **Chat hangs with no answer / uploads never finish indexing** — if the terminal prints up to `Retrievers [...]` (or stalls during indexing right after `Got N page thumbnails`) and nothing else comes back, suspect a **stale `theflow` cache lock**. Every pipeline call (query *and* indexing) acquires a cross-process `diskcache` RLock under the key `__lock__` in `<tempdir>/theflow_<user>/cache`. If the app (or a worker) is force-killed mid-request, that lock is left held by a dead PID and every later call spins forever. Fix it by clearing the lock:

  ```bash
  uv run python -c "import diskcache; from theflow.utils.paths import temp_path; from pathlib import Path; diskcache.Cache(str(Path(temp_path(), 'cache'))).delete('__lock__'); print('cleared')"
  ```

  Or, with the app stopped, delete the whole cache dir (it's only a cache and is rebuilt automatically): `rm -rf "$(uv run python -c "from theflow.utils.paths import temp_path; from pathlib import Path; print(Path(temp_path(), 'cache'))")"`. To check whether the lock is actually stale, read it — a dead PID with count ≥ 1 confirms it: `uv run python -c "import diskcache; from theflow.utils.paths import temp_path; from pathlib import Path; print(diskcache.Cache(str(Path(temp_path(), 'cache'))).get('__lock__'))"`. After clearing, re-upload any file whose indexing was interrupted (a source can show in the UI with 0 chunks). Avoid hard-killing the app mid-request to prevent recurrence.

