# python:3.11-slim, pinned to the digest validated for this release.
FROM python@sha256:db3ff2e1800a8581e2c48a27c3995339d47bdf046da21c7627accd3d51053a93

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
