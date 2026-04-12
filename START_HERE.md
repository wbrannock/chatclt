# Kotaemon RAG - Start/Stop Instructions

## Start the App

```bash
conda activate kotaemon
cd /Users/williambrannock/Documents/gradschool/capstone/v1/kotaemon
PDFJS_PREBUILT_DIR="$(pwd)/libs/ktem/ktem/assets/prebuilt/pdfjs-4.0.379-dist" python app.py
```

Open **http://localhost:7860** in your browser.
Login: **admin / admin**

## Stop the App

Press **Ctrl+C** in the terminal where it's running.

## Usage

1. Go to **Files** tab to upload PDFs
2. Go to **Chat** tab to ask questions about your documents
3. Select files in the left sidebar under **File Collection** to scope your search
4. Use **Chat settings** at the bottom to change reasoning method, model, and language

## Configuration

- **API Key**: `kotaemon/.env` — your OpenRouter key lives here
- **Chat Model**: `anthropic/claude-sonnet-4-6` via OpenRouter (change `OPENAI_CHAT_MODEL` in `.env`)
- **Embeddings**: FastEmbed (`BAAI/bge-small-en-v1.5`) — runs locally, no API key needed
- **Reranking**: Disabled by default (no Cohere key). To enable, add `COHERE_API_KEY=your-key` to `.env`

## Your PDF Files

Located at `../sample_rag_pdfs/` organized by category:
- pathology (33 files)
- synthetic_procedures (16 files)
- immunology (5 files)
- hematology (4 files)
- clinical_chemistry (4 files)
- molecular_genetics (2 files)

## Data Persistence

All indexed data is stored in `kotaemon/ktem_app_data/`. This persists between restarts — you don't need to re-upload files.
