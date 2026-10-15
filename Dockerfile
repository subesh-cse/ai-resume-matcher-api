FROM python:3.12-slim-bookworm

COPY --from=ghcr.io/astral-sh/uv:latest /uv /bin/uv

ENV PYTHONUNBUFFERED=1 \
    UV_COMPILE_BYTECODE=1 \
    UV_SYSTEM_PYTHON=1 \
    PORT=10000

WORKDIR /app

COPY pyproject.toml uv.lock ./
RUN uv pip install --system -r pyproject.toml

COPY app/ ./app

EXPOSE 10000

RUN python -c "from sentence_transformers import SentenceTransformer; SentenceTransformer('all-MiniLM-L6-v2')"

CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "10000"]