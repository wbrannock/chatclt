#!/usr/bin/env python3
"""
Check which project dependencies are available on conda-forge vs pip-only.
Outputs a compatibility report with suggested alternatives.

Usage: python scripts/check_conda_compat.py
"""

import subprocess
import sys
from concurrent.futures import ThreadPoolExecutor, as_completed

# All deps extracted from libs/kotaemon/pyproject.toml, libs/ktem/pyproject.toml,
# and the root pyproject.toml dev group.
DEPS = {
    # kotaemon core
    "azure-ai-documentintelligence": {"conda_name": "azure-ai-documentintelligence"},
    "beautifulsoup4": {"conda_name": "beautifulsoup4"},
    "click": {"conda_name": "click"},
    "cohere": {"conda_name": "cohere"},
    "cookiecutter": {"conda_name": "cookiecutter"},
    "fast_langdetect": {"conda_name": "fast_langdetect"},
    "fastapi": {"conda_name": "fastapi"},
    "gradio": {"conda_name": "gradio"},
    "html2text": {"conda_name": "html2text"},
    "langchain": {"conda_name": "langchain"},
    "langchain-community": {"conda_name": "langchain-community"},
    "langchain-openai": {"conda_name": "langchain-openai"},
    "langchain-google-genai": {"conda_name": "langchain-google-genai"},
    "langchain-anthropic": {"conda_name": "langchain-anthropic"},
    "langchain-ollama": {"conda_name": "langchain-ollama"},
    "langchain-mistralai": {"conda_name": "langchain-mistralai"},
    "langchain-cohere": {"conda_name": "langchain-cohere"},
    "llama-hub": {"conda_name": "llama-hub"},
    "llama-index": {"conda_name": "llama-index"},
    "chromadb": {"conda_name": "chromadb"},
    "llama-index-vector-stores-chroma": {"conda_name": "llama-index-vector-stores-chroma"},
    "llama-index-vector-stores-lancedb": {"conda_name": "llama-index-vector-stores-lancedb"},
    "openai": {"conda_name": "openai"},
    "matplotlib": {"conda_name": "matplotlib"},
    "matplotlib-inline": {"conda_name": "matplotlib-inline"},
    "openpyxl": {"conda_name": "openpyxl"},
    "opentelemetry-exporter-otlp-proto-grpc": {"conda_name": "opentelemetry-exporter-otlp-proto-grpc"},
    "pandas": {"conda_name": "pandas"},
    "plotly": {"conda_name": "plotly"},
    "PyMuPDF": {"conda_name": "pymupdf"},
    "pypdf": {"conda_name": "pypdf"},
    "pylance": {"conda_name": "pylance"},
    "python-decouple": {"conda_name": "python-decouple"},
    "python-docx": {"conda_name": "python-docx"},
    "python-dotenv": {"conda_name": "python-dotenv"},
    "tenacity": {"conda_name": "tenacity"},
    "theflow": {"conda_name": "theflow"},
    "trogon": {"conda_name": "trogon"},
    "umap-learn": {"conda_name": "umap-learn"},
    "tavily-python": {"conda_name": "tavily-python"},
    "pydantic": {"conda_name": "pydantic"},
    # kotaemon adv extras
    "duckduckgo-search": {"conda_name": "duckduckgo-search"},
    "elasticsearch": {"conda_name": "elasticsearch"},
    "fastembed": {"conda_name": "fastembed"},
    "onnxruntime": {"conda_name": "onnxruntime"},
    "googlesearch-python": {"conda_name": "googlesearch-python"},
    "llama-cpp-python": {"conda_name": "llama-cpp-python"},
    "llama-index-vector-stores-milvus": {"conda_name": "llama-index-vector-stores-milvus"},
    "llama-index-vector-stores-qdrant": {"conda_name": "llama-index-vector-stores-qdrant"},
    "mcp": {"conda_name": "mcp"},
    "sentence-transformers": {"conda_name": "sentence-transformers"},
    "tabulate": {"conda_name": "tabulate"},
    "unstructured": {"conda_name": "unstructured"},
    "wikipedia": {"conda_name": "wikipedia"},
    "voyageai": {"conda_name": "voyageai"},
    # ktem
    "platformdirs": {"conda_name": "platformdirs"},
    "pluggy": {"conda_name": "pluggy"},
    "SQLAlchemy": {"conda_name": "sqlalchemy"},
    "sqlmodel": {"conda_name": "sqlmodel"},
    "tiktoken": {"conda_name": "tiktoken"},
    "gradiologin": {"conda_name": "gradiologin"},
    "python-multipart": {"conda_name": "python-multipart"},
    "markdown": {"conda_name": "markdown"},
    "tzlocal": {"conda_name": "tzlocal"},
}

# Known conda-forge availability (pre-verified to avoid slow network calls for obvious ones)
KNOWN_CONDA = {
    "beautifulsoup4", "click", "cookiecutter", "fastapi", "langchain",
    "openai", "matplotlib", "matplotlib-inline", "openpyxl",
    "opentelemetry-exporter-otlp-proto-grpc", "pandas", "plotly",
    "pymupdf", "pypdf", "python-decouple", "python-docx", "python-dotenv",
    "tenacity", "umap-learn", "pydantic", "elasticsearch", "onnxruntime",
    "sentence-transformers", "tabulate", "platformdirs", "pluggy",
    "sqlalchemy", "tiktoken", "python-multipart", "markdown", "tzlocal",
    "gradio", "trogon", "chromadb",
}

# Known pip-only (not on conda-forge or version constraints make conda impractical)
KNOWN_PIP_ONLY = {
    "azure-ai-documentintelligence": "No conda-forge package. Pip only.",
    "cohere": "No conda-forge package. Pip only.",
    "fast_langdetect": "Not on conda-forge. Alt: `langdetect` (conda-forge) for basic language detection.",
    "html2text": "Not on conda-forge. Alt: `markdownify` (pip) or `bleach` (conda-forge) for HTML stripping.",
    "langchain-community": "Not on conda-forge. Pip only.",
    "langchain-openai": "Not on conda-forge. Pip only.",
    "langchain-google-genai": "Not on conda-forge. Pip only.",
    "langchain-anthropic": "Not on conda-forge. Pip only.",
    "langchain-ollama": "Not on conda-forge. Pip only.",
    "langchain-mistralai": "Not on conda-forge. Pip only.",
    "langchain-cohere": "Not on conda-forge. Pip only.",
    "llama-hub": "Not on conda-forge. Pip only.",
    "llama-index": "Not on conda-forge. Pip only.",
    "llama-index-vector-stores-chroma": "Not on conda-forge. Pip only.",
    "llama-index-vector-stores-lancedb": "Not on conda-forge. Pip only.",
    "llama-index-vector-stores-milvus": "Not on conda-forge. Pip only.",
    "llama-index-vector-stores-qdrant": "Not on conda-forge. Pip only.",
    "pylance": "⚠️  This is a VS Code extension — NOT a Python package. Should be removed from pyproject.toml.",
    "theflow": "Not on conda-forge. Core framework — no replacement possible.",
    "tavily-python": "Not on conda-forge. Pip only.",
    "duckduckgo-search": "Not on conda-forge. Pip only.",
    "fastembed": "Not on conda-forge. Pip only.",
    "googlesearch-python": "Not on conda-forge. Pip only.",
    "llama-cpp-python": "Not on conda-forge (build is complex). Pip only.",
    "mcp": "Not on conda-forge. Pip only.",
    "unstructured": "Not on conda-forge. Pip only.",
    "wikipedia": "Not on conda-forge. Pip only.",
    "voyageai": "Not on conda-forge. Pip only.",
    "sqlmodel": "Not on conda-forge. Pip only.",
    "gradiologin": "Not on conda-forge. Pip only.",
}


def check_conda_forge(pkg_name: str) -> tuple[str, bool]:
    conda_name = DEPS[pkg_name]["conda_name"]
    if conda_name in KNOWN_CONDA:
        return pkg_name, True
    if pkg_name in KNOWN_PIP_ONLY:
        return pkg_name, False
    try:
        result = subprocess.run(
            ["conda", "search", "-c", "conda-forge", "--json", conda_name],
            capture_output=True, text=True, timeout=15
        )
        data = result.stdout
        found = f'"{conda_name}"' in data or f'"name": "{conda_name}"' in data
        return pkg_name, found
    except Exception:
        return pkg_name, False


def main():
    print("Checking conda-forge availability for all dependencies...\n")
    results = {}

    with ThreadPoolExecutor(max_workers=8) as executor:
        futures = {executor.submit(check_conda_forge, pkg): pkg for pkg in DEPS}
        for future in as_completed(futures):
            pkg, available = future.result()
            results[pkg] = available

    conda_ok = sorted([p for p, ok in results.items() if ok])
    pip_only = sorted([p for p, ok in results.items() if not ok])

    print("=" * 70)
    print(f"CONDA-FORGE AVAILABLE ({len(conda_ok)} packages)")
    print("=" * 70)
    for pkg in conda_ok:
        conda_name = DEPS[pkg]["conda_name"]
        note = f"  (conda name: {conda_name})" if conda_name != pkg.lower() else ""
        print(f"  ✓  {pkg}{note}")

    print()
    print("=" * 70)
    print(f"PIP-ONLY ({len(pip_only)} packages)")
    print("=" * 70)
    for pkg in pip_only:
        note = KNOWN_PIP_ONLY.get(pkg, "Not found on conda-forge.")
        print(f"  ✗  {pkg}")
        print(f"       {note}")

    print()
    print("=" * 70)
    print("RECOMMENDED CHANGES FOR CONDA COMPATIBILITY")
    print("=" * 70)
    print("""
1. USE A CONDA + PIP HYBRID ENVIRONMENT (standard for ML projects)
   Most of the pip-only packages (langchain-*, llama-index-*, theflow,
   fastembed, mcp) have no conda-forge equivalent and cannot be replaced
   without significant architectural changes. A hybrid approach is the
   only practical path.

   Recommended environment.yml structure:
     channels:
       - conda-forge
       - defaults
     dependencies:
       - python=3.11
       - <all conda-forge packages listed above>
       - pip:
           - <all pip-only packages>

2. REMOVE `pylance` FROM pyproject.toml
   `pylance` is a VS Code language server extension, not a Python package.
   It should not be in pyproject.toml at all — it will cause pip install
   failures in clean environments. Remove it from libs/kotaemon/pyproject.toml.

3. REPLACE `fast_langdetect` (pip-only) → `langdetect` (conda-forge)
   If language detection is the only use, `langdetect` is on conda-forge
   and covers the same basic functionality. Requires code change in the
   callers.

4. NO SWAP POSSIBLE FOR THESE (too deeply integrated):
   - theflow, gradio, langchain-*, llama-index-*, chromadb, fastembed,
     sqlmodel, mcp, theflow — all pip-only with no conda equivalent.
     Must be installed via pip inside conda.
""")

    print(f"\nSummary: {len(conda_ok)} conda-forge, {len(pip_only)} pip-only "
          f"out of {len(DEPS)} total packages.")


if __name__ == "__main__":
    main()
