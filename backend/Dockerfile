FROM python:3.11-slim

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PIP_NO_CACHE_DIR=1 \
    PIP_DISABLE_PIP_VERSION_CHECK=1 \
    EMBEDDING_CACHE_DIR=/opt/models

# The ONNX runtime used for embeddings needs the OpenMP library, which the slim image lacks.
RUN apt-get update \
    && apt-get install -y --no-install-recommends libgomp1 \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

# Install dependencies first, so this slow layer is reused when only the code changes.
COPY requirements.txt .
RUN pip install -r requirements.txt

# Download the embedding model now, so the container never has to download it at start-up.
RUN python -c "from fastembed import TextEmbedding; TextEmbedding('sentence-transformers/all-MiniLM-L6-v2', cache_dir='/opt/models')"

COPY . .

# Run as an ordinary user instead of root.
RUN useradd --create-home --uid 10001 app \
    && chown -R app:app /app /opt/models
USER app

EXPOSE 8000

# Apply database migrations, then start the API. Some hosts (such as Render) set PORT.
CMD ["sh", "-c", "alembic upgrade head && exec uvicorn app.main:app --host 0.0.0.0 --port ${PORT:-8000}"]