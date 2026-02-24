FROM python:3.11-slim

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PIP_NO_CACHE_DIR=1

WORKDIR /app

COPY pyproject.toml README.md ./
COPY src ./src
COPY tests ./tests

RUN python -m pip install --upgrade pip \
    && python -m pip install -e . pytest

# Runtime workspace is mounted here so `.lame/` persists on the host.
WORKDIR /workspace

EXPOSE 8080

CMD ["lamecoder", "ui", "--host", "0.0.0.0", "--port", "8080"]
