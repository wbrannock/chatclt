# Setup local LLMs & Embedding models

## Prepare local models

#### NOTE

In the case of using Docker image, please replace `http://localhost` with `http://host.docker.internal` to correctly communicate with service on the host machine. See [more detail](https://stackoverflow.com/questions/31324981/how-to-access-host-port-from-docker-container).

### Ollama OpenAI compatible server (recommended)

Install [ollama](https://github.com/ollama/ollama) and start the application.

Pull your model (e.g):

```
ollama pull qwen3:4b-instruct
ollama pull nomic-embed-text
```

For an M3 Pro MacBook with 18 GB RAM, `qwen3:4b-instruct` is the recommended
first local chat model. It is small enough to run comfortably through Ollama,
while still giving useful RAG answers. Start with a 32K context window:

```
LOCAL_MODEL=qwen3:4b-instruct
LOCAL_MODEL_EMBEDDINGS=nomic-embed-text
LOCAL_MODEL_CONTEXT_LENGTH=32768
```

In Chat settings, select `ollama-qwen3-4b-instruct-32k` for the explicit 32K
context path, or `ollama-qwen3-4b-instruct` for the standard Ollama-compatible
OpenAI endpoint path.

Qwen3 4B advertises very long-context capability, but memory use grows with the
active context window. Treat 64K+ as a stress test on this machine, not the
default.

The `qwen3:4b` thinking tag may stream a visible reasoning trace before the
final answer. That is useful for reasoning experiments but noisy for RAG. If you
want to compare it directly, set:

```
ollama pull qwen3:4b
LOCAL_MODEL=qwen3:4b
```

Setup LLM and Embedding model on Resources tab with type OpenAI. Set these model parameters to connect to Ollama:

```
api_key: ollama
base_url: http://localhost:11434/v1/
model: qwen3:4b-instruct (for llm) | nomic-embed-text (for embedding)
```

![Models](https://raw.githubusercontent.com/Cinnamon/kotaemon/main/docs/images/models.png)

### oobabooga/text-generation-webui OpenAI compatible server

Install [oobabooga/text-generation-webui](https://github.com/oobabooga/text-generation-webui/).

Follow the setup guide to download your models (GGUF, HF).
Also take a look at [OpenAI compatible server](https://github.com/oobabooga/text-generation-webui/wiki/12-%E2%80%90-OpenAI-API) for detail instructions.

Here is a short version

```
# install sentence-transformer for embeddings creation
pip install sentence_transformers
# change to text-generation-webui src dir
python server.py --api
```

Use the `Models` tab to download new model and press Load.

Setup LLM and Embedding model on Resources tab with type OpenAI. Set these model parameters to connect to `text-generation-webui`:

```
api_key: dummy
base_url: http://localhost:5000/v1/
model: any
```

### llama-cpp-python server (LLM only)

See [llama-cpp-python OpenAI server](https://llama-cpp-python.readthedocs.io/en/latest/server/).

Download any GGUF model weight on HuggingFace or other source. Place it somewhere on your local machine.

Run

```
LOCAL_MODEL=<path/to/GGUF> python scripts/serve_local.py
```

Setup LLM model on Resources tab with type OpenAI. Set these model parameters to connect to `llama-cpp-python`:

```
api_key: dummy
base_url: http://localhost:8000/v1/
model: model_name
```

## Use local models for RAG

- Set default LLM and Embedding model to a local variant.

![Models](https://raw.githubusercontent.com/Cinnamon/kotaemon/main/docs/images/llm-default.png)

- Set embedding model for the File Collection to a local model (e.g: `ollama`)

![Index](https://raw.githubusercontent.com/Cinnamon/kotaemon/main/docs/images/index-embedding.png)

- Go to Retrieval settings and choose LLM relevant scoring model as a local model (e.g: `ollama`). Or, you can choose to disable this feature if your machine cannot handle a lot of parallel LLM requests at the same time.

![Settings](https://raw.githubusercontent.com/Cinnamon/kotaemon/main/docs/images/retrieval-setting.png)

You are set! Start a new conversation to test your local RAG pipeline.
