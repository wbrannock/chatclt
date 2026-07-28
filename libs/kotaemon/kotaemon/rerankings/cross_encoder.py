from __future__ import annotations

import threading
from typing import Optional

from kotaemon.base import Document, Param

from .base import BaseReranking


def _auto_device() -> str:
    """Best available torch device: Apple Metal, then CUDA, then CPU."""
    try:
        import torch
    except ImportError:
        return "cpu"

    if torch.backends.mps.is_available():
        return "mps"
    if torch.cuda.is_available():
        return "cuda"
    return "cpu"


class CrossEncoderReranking(BaseReranking):
    """Local cross-encoder reranker on torch, GPU-accelerated where available.

    A cross-encoder reads the query and passage together, so unlike the bi-encoder used
    for retrieval it can separate passages whose embeddings are near-identical -- which
    is the whole difficulty of a corpus of thousands of similarly-worded lab SOPs.

    Runs entirely locally: no API key, no network. On Apple Metal, bge-reranker-base
    scores ~30ms/document, which is both faster and more accurate than running the much
    smaller MiniLM through fastembed's CPU ONNX runtime (~37ms/document), so there's no
    quality/latency tradeoff to make here -- the good model is also the fast one.
    """

    model_name: str = Param(
        "BAAI/bge-reranker-base",
        help="A sentence-transformers CrossEncoder model id.",
        required=True,
    )
    device: Optional[str] = Param(
        None,
        help="torch device ('mps', 'cuda', 'cpu'). Auto-detected when unset.",
    )
    max_length: int = Param(512, help="Token limit per (query, passage) pair.")
    batch_size: int = Param(32, help="Pairs scored per forward pass.")

    _model = None
    _lock = threading.Lock()

    def _get_model(self):
        # Loading weights costs a couple of seconds; hold one instance rather than
        # paying that on every query.
        if self._model is None:
            with self._lock:
                if self._model is None:
                    try:
                        from sentence_transformers import CrossEncoder
                    except ImportError:
                        raise ImportError(
                            "Please install sentence-transformers "
                            "(`pip install sentence-transformers`) to use "
                            "CrossEncoderReranking"
                        )
                    device = self.device or _auto_device()
                    print(
                        f"[CrossEncoderReranking] loading {self.model_name} on {device}"
                    )
                    self._model = CrossEncoder(
                        self.model_name, device=device, max_length=self.max_length
                    )
        return self._model

    def run(self, documents: list[Document], query: str) -> list[Document]:
        """Reorder `documents` by cross-encoder relevance to `query`, best first."""
        if not documents or not query:
            return documents

        model = self._get_model()
        scores = model.predict(
            [(query, doc.content) for doc in documents],
            batch_size=self.batch_size,
            show_progress_bar=False,
        )

        for doc, score in zip(documents, scores):
            doc.metadata["reranking_score"] = float(score)

        return [
            doc
            for doc, _ in sorted(
                zip(documents, scores), key=lambda pair: pair[1], reverse=True
            )
        ]
