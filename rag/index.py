"""Self-refreshing document index.

Watches the docs directory by signature (path, mtime, size). When a change is
detected — checked at most once per `check_interval` seconds, on access — the
index is rebuilt and swapped in atomically. Readers never block on a rebuild;
they keep using the previous index until the new one is ready.
"""

from __future__ import annotations

import logging
import time
from pathlib import Path
from threading import Lock, Thread

from .ingest import SUPPORTED_SUFFIXES, load_documents
from .retriever import Retriever

logger = logging.getLogger(__name__)


class DocumentIndex:
    def __init__(self, docs_dir: str | Path, check_interval: float = 5.0,
                 background: bool = True):
        self.docs_dir = Path(docs_dir)
        self.check_interval = check_interval
        self.background = background
        self._lock = Lock()
        self._rebuilding = False
        self._last_check = time.monotonic()
        self._signature = self._scan()
        self._retriever = Retriever(load_documents(self.docs_dir))

    @property
    def retriever(self) -> Retriever:
        self._maybe_reload()
        return self._retriever

    def _scan(self) -> tuple:
        entries = []
        for p in self.docs_dir.rglob("*"):
            if p.suffix.lower() in SUPPORTED_SUFFIXES and p.is_file():
                st = p.stat()
                entries.append((str(p), st.st_mtime_ns, st.st_size))
        return tuple(sorted(entries))

    def _maybe_reload(self) -> None:
        now = time.monotonic()
        with self._lock:
            if self._rebuilding or now - self._last_check < self.check_interval:
                return
            self._last_check = now
            signature = self._scan()
            if signature == self._signature:
                return
            self._rebuilding = True
        if self.background:
            Thread(target=self._rebuild, args=(signature,), daemon=True).start()
        else:
            self._rebuild(signature)

    def _rebuild(self, signature: tuple) -> None:
        try:
            new_retriever = Retriever(load_documents(self.docs_dir))
        except Exception:
            # e.g. docs dir temporarily empty or an unparsable file mid-upload;
            # keep serving the previous index and retry on the next change.
            logger.exception("Index rebuild failed; keeping previous index")
            with self._lock:
                self._rebuilding = False
            return
        with self._lock:
            self._retriever = new_retriever
            self._signature = signature
            self._rebuilding = False
        logger.info("Knowledge base reloaded: %d chunks", len(new_retriever.chunks))
