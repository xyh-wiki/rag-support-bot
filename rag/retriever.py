"""BM25 retrieval over document chunks.

BM25 keeps the service dependency-light and fully offline. Replacing this class
is enough to switch the retrieval layer to another ranking backend later; the
ingest and app layers do not need to change.
"""

from __future__ import annotations

import re

from rank_bm25 import BM25Okapi

from .ingest import Chunk

_LATIN_RE = re.compile(r"[a-z0-9]+")
_CJK_RE = re.compile(r"[一-鿿぀-ヿ가-힯]+")


def _tokenize(text: str) -> list[str]:
    """Latin words plus CJK character bigrams, so mixed-language corpora work."""
    text = text.lower()
    tokens = _LATIN_RE.findall(text)
    for run in _CJK_RE.findall(text):
        if len(run) == 1:
            tokens.append(run)
        else:
            tokens.extend(run[i : i + 2] for i in range(len(run) - 1))
    return tokens


class Retriever:
    def __init__(self, chunks: list[Chunk]):
        if not chunks:
            raise ValueError("No document chunks to index — is the docs/ folder empty?")
        self.chunks = chunks
        self._corpus = [_tokenize(f"{c.doc_name} {c.section} {c.text}") for c in chunks]
        self.bm25 = BM25Okapi(self._corpus)

    def search(self, query: str, top_k: int = 4) -> list[tuple[Chunk, float]]:
        """Return the top_k most relevant chunks with their scores."""
        q_tokens = _tokenize(query)
        scores = self.bm25.get_scores(q_tokens)
        if max(scores, default=0) <= 0:
            # BM25 IDF degenerates on tiny corpora (a term present in every
            # document gets non-positive weight). Fall back to token overlap.
            q_set = set(q_tokens)
            scores = [len(q_set & set(doc)) for doc in self._corpus]
        ranked = sorted(range(len(scores)), key=lambda i: scores[i], reverse=True)
        return [(self.chunks[i], float(scores[i])) for i in ranked[:top_k] if scores[i] > 0]
