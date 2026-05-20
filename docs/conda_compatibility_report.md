# Conda Compatibility Report
**Project:** ChatCLT — Medical Procedure Query App
**Date:** May 5, 2026

---

## Executive Summary

The team evaluated whether the ChatCLT codebase can be migrated to use only conda packages, motivated by a healthcare IT security requirement. The short answer is: **a full conda-only migration is not feasible without a 3–6 month ground-up rewrite**, but the underlying security concern can be addressed through easier alternatives that take days, not months.

The advisor's recommendation to use conda stems from a legitimate concern: **supply chain security**. Conda-forge packages go through a peer-review process before publishing; PyPI does not. However, conda is a mechanism for achieving supply chain integrity — not the only one. The project already has a `uv.lock` file that pins every dependency to an exact SHA256 hash, which provides equivalent guarantees.

---

## Why a Full Conda Rewrite Is Not Feasible

The app is built on three pip-only ecosystems that are load-bearing across the entire codebase:

| Library | Files affected (out of 253) | Role |
|---|---|---|
| `theflow` | 83 | Core pipeline and component framework — every class inherits from it |
| `llama-index` | 25 | All vector indexing and retrieval logic |
| `langchain-*` | 16 | All LLM and embedding provider integrations |
| `sqlmodel` | 14 | All database models |

None of these have conda-forge equivalents, and none can be swapped out without replacing the architecture they underpin. `theflow` alone would require writing a custom pipeline framework from scratch before any other work could begin. **The result would not be a rewrite of ChatCLT — it would be an entirely new application.**

---

## The Real Security Concern

The advisor's recommendation is about **supply chain integrity** — preventing a malicious or tampered package from being installed. Conda-forge solves this through a package review process. But the same protection can be achieved other ways:

- **Pinned lockfiles:** Every pip package pinned to an exact SHA256 hash means nothing can be swapped or updated without a deliberate change to the lockfile. The project already has `uv.lock`.
- **Docker containers:** The entire runtime environment is frozen at build time, scanned once, and approved. Nothing changes after approval. This is arguably more secure than conda.
- **Private conda channels:** Tools exist to convert pip packages into conda packages and host them internally, giving IT an all-conda install without any code changes.

---

## Recommended Options (Ranked by Effort)

### Option 1 — Present the existing lockfile to IT *(days)*
The `uv.lock` file already pins every dependency to a specific hash. No package can be silently updated or swapped. Present this alongside the list of pip packages and their publishers (all reputable: LangChain, LlamaIndex, OpenAI, Anthropic) and ask if this satisfies the supply chain requirement.

### Option 2 — Docker container *(1–2 weeks)*
Package the app as a Docker image. Build it, scan it with a tool like Trivy or Grype, get the image approved, and deploy it. The environment is immutable after approval — nothing can change without rebuilding and re-approving the image. Many hospital IT departments accept this model.

### Option 3 — Private conda channel via `grayskull` *(2–4 weeks)*
Use [`grayskull`](https://github.com/conda/grayskull) or [`rattler-build`](https://github.com/prefix-dev/rattler-build) to convert the pip-only packages into conda packages and host them on an internal channel. IT gets an all-conda install. No code changes required.

### Option 4 — Conda + pip hybrid environment *(1 week)*
Use conda for the 34 packages available on conda-forge, and pip (with pinned versions) for the 30 pip-only packages. This is the standard pattern for ML projects and is well understood by most IT security teams.

### Option 5 — Full rewrite *(3–6 months)*
Replace `theflow`, `llama-index`, `langchain-*`, and `sqlmodel` with conda-compatible alternatives or custom implementations. Not recommended — disproportionate effort for a capstone project, and the security outcome is the same as Options 1–3.

---

## Suggested Next Step

Go back to your advisor with this framing:

> "The security concern is supply chain integrity. We already have a hash-pinned lockfile covering every dependency. Would a Docker container with a scanned image, or a pip+conda hybrid with pinned hashes, satisfy the requirement? A full conda migration would require 3–6 months of architectural rewriting and is out of scope."

---

## Package Breakdown

### Available on conda-forge (34 packages)

These can be installed via `conda install -c conda-forge`:

| Package | Notes |
|---|---|
| `beautifulsoup4` | HTML parsing |
| `click` | CLI framework |
| `chromadb` | Vector store |
| `cookiecutter` | Project templating |
| `elasticsearch` | Document search |
| `fastapi` | Web API framework |
| `gradio` | UI framework |
| `langchain` | Base LangChain (provider integrations are pip-only) |
| `markdown` | Markdown rendering |
| `matplotlib` + `matplotlib-inline` | Plotting |
| `onnxruntime` | ML model runtime |
| `openai` | OpenAI SDK |
| `openpyxl` | Excel file support |
| `opentelemetry-exporter-otlp-proto-grpc` | Telemetry |
| `pandas` | Data processing |
| `platformdirs` | OS path utilities |
| `plotly` | Interactive charts |
| `pluggy` | Plugin system |
| `pydantic` | Data validation |
| `pymupdf` | PDF parsing |
| `pypdf` | PDF parsing (secondary) |
| `python-decouple` | Environment config |
| `python-docx` | Word document support |
| `python-dotenv` | .env file loading |
| `python-multipart` | File upload support |
| `sentence-transformers` | Local embeddings (conda alternative to fastembed) |
| `sqlalchemy` | Database ORM (base layer) |
| `tabulate` | Table formatting |
| `tenacity` | Retry logic |
| `tiktoken` | OpenAI tokenizer |
| `trogon` | TUI for CLI apps |
| `tzlocal` | Timezone utilities |
| `umap-learn` | Dimensionality reduction |

---

### Pip-only — No conda equivalent (30 packages)

#### Cannot be replaced (architectural)

| Package | Why it cannot be replaced |
|---|---|
| `theflow` | The pipeline/component framework the entire `kotaemon` library is written in. 83 files inherit from it. No conda equivalent exists anywhere. |
| `llama-index` + `llama-index-vector-stores-*` + `llama-hub` | The entire vector indexing and retrieval system. Powers document ingestion, chunking, embedding storage, and semantic search. Not on conda-forge. |
| `langchain-community`, `langchain-openai`, `langchain-anthropic`, `langchain-ollama`, `langchain-google-genai`, `langchain-mistralai`, `langchain-cohere` | All LLM provider integrations. The base `langchain` package is on conda-forge but is useless without these. All pip-only. |
| `sqlmodel` | Bridges SQLAlchemy + Pydantic for all database models. No conda equivalent. Could be replaced with raw SQLAlchemy (significant refactor). |
| `mcp` | Anthropic's Model Context Protocol for tool use. Brand new — no conda package yet. |

#### No conda equivalent, no practical alternative

| Package | Notes |
|---|---|
| `fastembed` | Default local embedding model. `sentence-transformers` (conda-forge) could replace it with config changes. |
| `gradiologin` | Gradio authentication extension. Required for the SSO login flow. |
| `cohere` | Cohere SDK. Required for the default reranking model (`rerank-v3.5`). |
| `voyageai` | Voyage AI SDK. Optional — only needed if using Voyage embeddings/reranking. |
| `azure-ai-documentintelligence` | Azure document parsing SDK. Optional — only needed for Azure DI integration. |
| `tavily-python` | Web search SDK. Required for the default web search backend. |
| `unstructured` | Document parsing for complex formats. Notoriously difficult to install even via pip. |
| `html2text` | HTML to text conversion. No conda package. |
| `fast_langdetect` | Language detection. Could be replaced with `langdetect` (conda-forge) with minor code changes. |
| `duckduckgo-search` | Optional web search backend. |
| `googlesearch-python` | Optional web search backend. |
| `llama-cpp-python` | Local LLM inference. Optional — only needed for local model support. |
| `wikipedia` | Wikipedia search tool. Optional. |
| `sqlmodel` | See architectural section above. |

#### Should be removed entirely

| Package | Why |
|---|---|
| `pylance` | This is a VS Code language server extension, **not a Python package**. Its presence in `libs/kotaemon/pyproject.toml` will cause install failures in clean environments. Should be deleted from the dependencies list. |

---

## Summary

| Category | Count |
|---|---|
| Available on conda-forge | 34 |
| Pip-only, no replacement | 20 |
| Pip-only, minor replacement possible | 2 (`fast_langdetect` → `langdetect`, `fastembed` → `sentence-transformers`) |
| Should be removed | 1 (`pylance`) |
| **Total** | **64** |
