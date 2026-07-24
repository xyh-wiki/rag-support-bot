# python:3.11-slim, pinned to the digest validated for this release.
FROM python@sha256:9643927a6fc74bd81b0f1bbb5cce3cb4a491f46b4c5dbee770f28e575f180015

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PIP_DISABLE_PIP_VERSION_CHECK=1

RUN groupadd --system --gid 993 rag-support-bot \
    && useradd --system --uid 993 --gid 993 --no-create-home --shell /usr/sbin/nologin rag-support-bot

WORKDIR /app

COPY requirements.lock /tmp/requirements.lock
RUN pip install --no-cache-dir -r /tmp/requirements.lock \
    && rm /tmp/requirements.lock

COPY --chown=993:993 . .

USER 993:993
EXPOSE 8000
HEALTHCHECK --interval=15s --timeout=5s --start-period=15s --retries=8 \
    CMD ["python", "-c", "import urllib.request; urllib.request.urlopen('http://127.0.0.1:8000/api/health', timeout=3).read()"]
CMD ["python", "-m", "uvicorn", "app:app", "--host", "0.0.0.0", "--port", "8000"]
