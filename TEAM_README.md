# Capstone Kotaemon — Team Setup

Our capstone fork of [Cinnamon/kotaemon](https://github.com/Cinnamon/kotaemon) for a PDF-grounded RAG chat app. Upstream docs live in [`README.md`](./README.md); this file is the short path to a running app.

## Prerequisites

- macOS or Linux
- [Miniconda / Anaconda](https://docs.conda.io/en/latest/miniconda.html)
- Git
- An OpenRouter API key (https://openrouter.ai/keys)

## 1. Clone

```bash
git clone <this-repo-url> kotaemon
cd kotaemon
```

## 2. Create the conda environment

```bash
conda env create -f environment.yml
conda activate kotaemon
```

This creates a Python 3.10 env named `kotaemon` and installs the local `libs/kotaemon[adv]` and `libs/ktem` packages in editable mode, so your code changes apply without reinstalling.

To rebuild from scratch later:

```bash
conda env remove -n kotaemon
conda env create -f environment.yml
```

## 3. Configure secrets

```bash
cp .env.example .env
```

Then edit `.env` and set at minimum:

```
OPENAI_API_KEY=sk-or-v1-...      # your OpenRouter key
OPENAI_API_BASE=https://openrouter.ai/api/v1
OPENAI_CHAT_MODEL=anthropic/claude-sonnet-4-6
```

`.env` is gitignored — never commit it.

## 4. Run

```bash
PDFJS_PREBUILT_DIR="$(pwd)/libs/ktem/ktem/assets/prebuilt/pdfjs-4.0.379-dist" python app.py
```

Open http://localhost:7860 — default login is `admin` / `admin`.

Stop with `Ctrl+C`.

## Using the app

1. **Files** tab → upload PDFs.
2. **Chat** tab → ask questions. Select files under **File Collection** on the left to scope the search.
3. **Chat settings** (bottom of Chat) → switch reasoning method, model, or language.

Indexed data is persisted in `ktem_app_data/` (gitignored), so re-running does not require re-uploading.

## Defaults

- **Chat model**: `anthropic/claude-sonnet-4-6` via OpenRouter
- **Embeddings**: FastEmbed `BAAI/bge-small-en-v1.5` (local, no key)
- **Reranking**: off. Add `COHERE_API_KEY=...` to `.env` to enable.

## Contributing

```bash
git checkout -b your-feature
# edit, test locally
git commit -am "short message"
git push -u origin your-feature
```

Open a PR against `main`. Do not commit `.env`, `ktem_app_data/`, or anything under `__pycache__/`.

## Troubleshooting

- **`conda env create` fails on a dep**: update conda (`conda update -n base conda`), then retry. If one pip package fails, you can finish the install manually: `conda activate kotaemon && pip install -e "libs/kotaemon[adv]" && pip install -e libs/ktem`.
- **`PDFJS_PREBUILT_DIR` missing**: make sure you launched from the repo root.
- **Port 7860 in use**: `GRADIO_SERVER_PORT=7861 python app.py`.
