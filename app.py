"""Knowledge-base service — FastAPI server.

Endpoints:
  GET  /            web UI
  POST /api/chat    SSE stream: retrieved sources first, then answer tokens
  GET  /api/health  index stats + whether generation is configured

Run:  uvicorn app:app --reload
Env:
  OPENAI_API_KEY       required for answer generation (without it, the server
                       still runs and returns retrieval results only)
  OPENAI_BASE_URL      optional: point at any OpenAI-compatible gateway
  MODEL                default: gpt-5.4
  TOP_K                retrieved chunks per question, default 4
  RATE_LIMIT_PER_MIN   per-IP chat requests per minute, default 30
"""

from __future__ import annotations

import json
import os
import time
from collections import defaultdict, deque
from pathlib import Path
from threading import Lock

import openai
from fastapi import FastAPI, HTTPException, Request
from fastapi.responses import FileResponse, PlainTextResponse, StreamingResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel, Field

from rag.index import DocumentIndex

BASE_DIR = Path(__file__).parent
MODEL = os.environ.get("MODEL", "gpt-5.4")
TOP_K = int(os.environ.get("TOP_K", "4"))
RATE_LIMIT_PER_MIN = int(os.environ.get("RATE_LIMIT_PER_MIN", "30"))
MAX_MESSAGE_CHARS = 2000
MAX_HISTORY_TURNS = 10
SOURCE_PREVIEW_CHARS = 700

# --- Deployment branding (all optional) ----------------------------------
BOT_NAME = os.environ.get("BOT_NAME", "Knowledge Base")
BOT_TAGLINE = os.environ.get(
    "BOT_TAGLINE", "Answers grounded in the product knowledge base"
)
BOT_PLACEHOLDER = os.environ.get(
    "BOT_PLACEHOLDER", "Ask about billing, deployments, API…"
)
BOT_LANG = os.environ.get("BOT_LANG", "en")
DOCS_DIR = Path(os.environ.get("DOCS_DIR", BASE_DIR / "docs"))
# Testing aid: expose the loaded knowledge base in a side panel.
# Turn off for production deployments.
SHOW_KB_PANEL = os.environ.get("SHOW_KB_PANEL", "false").lower() in {"1", "true", "yes"}
SHOW_SOURCES = os.environ.get("SHOW_SOURCES", "true").lower() in {"1", "true", "yes"}
# Comma-separated origins allowed to call the API cross-origin (for embedding
# the widget into other sites/apps). Empty = same-origin only.
ALLOWED_ORIGINS = [o.strip() for o in os.environ.get("ALLOWED_ORIGINS", "").split(",") if o.strip()]

DEFAULT_SYSTEM_PROMPT = f"""\
You answer questions for {BOT_NAME}.

Answer using ONLY the knowledge-base excerpts provided in each message.
Rules:
- If the excerpts do not contain the answer, say you don't know — never \
invent facts.
{"- Cite the section you used, e.g. (see: billing — Refund policy)." if SHOW_SOURCES else "- Do not expose document names, section names, citations, source labels, or retrieval scores."}
- Be concise and friendly. Answer in the same language the user writes in.
"""

_prompt_file = os.environ.get("SYSTEM_PROMPT_FILE")
SYSTEM_PROMPT = (
    Path(_prompt_file).read_text(encoding="utf-8")
    if _prompt_file
    else DEFAULT_SYSTEM_PROMPT
)

app = FastAPI(title=BOT_NAME, docs_url=None, redoc_url=None)
if ALLOWED_ORIGINS:
    from fastapi.middleware.cors import CORSMiddleware

    app.add_middleware(
        CORSMiddleware,
        allow_origins=ALLOWED_ORIGINS,
        allow_methods=["GET", "POST"],
        allow_headers=["Content-Type"],
    )
app.mount("/static", StaticFiles(directory=BASE_DIR / "static"), name="static")
index_manager = DocumentIndex(DOCS_DIR)

_rate_lock = Lock()
_rate_buckets: dict[str, deque] = defaultdict(deque)


def _completion_client() -> openai.OpenAI:
    # Reads OPENAI_API_KEY / OPENAI_BASE_URL from the environment.
    return openai.OpenAI()


def _check_rate_limit(request: Request) -> None:
    # Caddy sets X-Real-IP; fall back to the socket peer for local runs.
    ip = request.headers.get("x-real-ip") or (request.client.host if request.client else "?")
    now = time.monotonic()
    with _rate_lock:
        bucket = _rate_buckets[ip]
        while bucket and now - bucket[0] > 60:
            bucket.popleft()
        if len(bucket) >= RATE_LIMIT_PER_MIN:
            raise HTTPException(429, "Too many requests — please wait a minute.")
        bucket.append(now)


class ChatTurn(BaseModel):
    role: str = Field(pattern="^(user|assistant)$")
    content: str = Field(max_length=8000)


class ChatRequest(BaseModel):
    message: str = Field(min_length=1, max_length=MAX_MESSAGE_CHARS)
    history: list[ChatTurn] = Field(default=[], max_length=2 * MAX_HISTORY_TURNS)


def _sse(event: str, data: dict) -> str:
    return f"event: {event}\ndata: {json.dumps(data, ensure_ascii=False)}\n\n"


def _stream_delta_content(event) -> str | None:
    """Read text from OpenAI-compatible stream events, including providers
    that emit usage/final chunks with a null delta."""
    choices = getattr(event, "choices", None)
    if not choices:
        return None
    delta = getattr(choices[0], "delta", None)
    content = getattr(delta, "content", None) if delta is not None else None
    return content if isinstance(content, str) and content else None


def _source_only_answer(hits, show_sources: bool = True) -> str:
    """Return useful results when no completion API key is configured."""
    if not hits:
        return (
            "未找到相关文档片段。\n\n"
            "No matching source excerpts were found in the knowledge base."
        )

    lines = [
        "当前未配置生成接口,以下是知识库中检索到的相关片段:",
        "",
    ]
    for idx, (chunk, score) in enumerate(hits, start=1):
        text = " ".join(chunk.text.split())
        if len(text) > SOURCE_PREVIEW_CHARS:
            text = text[:SOURCE_PREVIEW_CHARS].rstrip() + "..."
        if show_sources:
            lines.extend([
                f"## {idx}. {chunk.source_label}",
                "",
                text,
                "",
                f"相关度: {score:.2f}",
                "",
            ])
        else:
            lines.extend([text, ""])
    return "\n".join(lines).strip()


@app.get("/api/config")
def config():
    """Branding for the web UI."""
    return {
        "name": BOT_NAME,
        "tagline": BOT_TAGLINE,
        "placeholder": BOT_PLACEHOLDER,
        "lang": BOT_LANG,
        "show_kb": SHOW_KB_PANEL,
        "show_sources": SHOW_SOURCES,
    }


@app.get("/api/kb")
def kb_overview():
    """Loaded knowledge-base summary — only exposed when SHOW_KB_PANEL is on."""
    if not SHOW_KB_PANEL:
        raise HTTPException(404, "Not found")
    docs: dict[str, dict] = {}
    for c in index_manager.retriever.chunks:
        entry = docs.setdefault(c.doc_name, {"chunks": 0, "sections": set()})
        entry["chunks"] += 1
        if c.section:
            entry["sections"].add(c.section)
    return {
        "documents": [
            {"name": name, "chunks": e["chunks"], "sections": len(e["sections"])}
            for name, e in sorted(docs.items())
        ],
        "total_chunks": len(index_manager.retriever.chunks),
    }


@app.get("/api/health")
def health():
    return {
        "status": "ok",
        "chunks_indexed": len(index_manager.retriever.chunks),
        # Backward-compatible key for older health checks.
        "generation_configured": bool(os.environ.get("OPENAI_API_KEY")),
        "llm_configured": bool(os.environ.get("OPENAI_API_KEY")),
        "model": MODEL,
    }


def _rewrite_query(question: str) -> str | None:
    """Rewrite a question into English search keywords (cross-language fallback).

    BM25 is lexical: a Chinese question can't match English docs by surface
    form. When retrieval comes back empty, one short rewrite call bridges the gap.
    The instruction lives in the user message so it survives gateways that
    inject their own system prompts.
    """
    try:
        resp = _completion_client().chat.completions.create(
            model=MODEL,
            max_tokens=60,
            messages=[{
                "role": "user",
                "content": (
                    "Translate the following text into a short English keyword "
                    "search query (max 8 words). Reply with ONLY the query on a "
                    f"single line, no explanation:\n\n{question}"
                ),
            }],
        )
        text = (resp.choices[0].message.content or "").strip()
        query = text.splitlines()[0].strip().strip('"') if text else ""
        # Guard against the service answering instead of rewriting.
        return query if 0 < len(query) <= 80 else None
    except openai.OpenAIError:
        return None


@app.post("/api/chat")
def chat(req: ChatRequest, request: Request):
    _check_rate_limit(request)
    retriever = index_manager.retriever
    hits = retriever.search(req.message, top_k=TOP_K)
    if not hits and os.environ.get("OPENAI_API_KEY"):
        rewritten = _rewrite_query(req.message)
        if rewritten:
            hits = retriever.search(rewritten, top_k=TOP_K)

    def generate():
        if SHOW_SOURCES:
            yield _sse("sources", {"sources": [c.source_label for c, _ in hits]})

        if not os.environ.get("OPENAI_API_KEY"):
            yield _sse("token", {"text": _source_only_answer(hits, SHOW_SOURCES)})
            yield _sse("done", {})
            return

        context = "\n\n---\n\n".join(
            f"[{c.source_label}]\n{c.text}" for c, _ in hits
        ) or "(no relevant excerpts found)"

        messages = [{"role": "system", "content": SYSTEM_PROMPT}]
        messages += [
            {"role": t.role, "content": t.content}
            for t in req.history[-2 * MAX_HISTORY_TURNS:]
        ]
        messages.append({
            "role": "user",
            "content": (
                f"Knowledge-base excerpts:\n\n{context}\n\n"
                f"Customer question: {req.message}"
            ),
        })

        try:
            stream = _completion_client().chat.completions.create(
                model=MODEL,
                max_tokens=1024,
                messages=messages,
                stream=True,
            )
            for event in stream:
                if delta := _stream_delta_content(event):
                    yield _sse("token", {"text": delta})
        except openai.OpenAIError as e:
            yield _sse("error", {"message": f"Completion API error: {e}"})
        yield _sse("done", {})

    return StreamingResponse(
        generate(),
        media_type="text/event-stream",
        headers={"Cache-Control": "no-cache", "X-Accel-Buffering": "no"},
    )


@app.get("/favicon.ico", include_in_schema=False)
def favicon():
    return FileResponse(BASE_DIR / "static" / "favicon.ico")


@app.get("/robots.txt", include_in_schema=False)
def robots():
    return PlainTextResponse("User-agent: *\nDisallow: /api/\n")


@app.get("/")
def index():
    return FileResponse(BASE_DIR / "static" / "index.html")
