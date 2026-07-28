FROM python:3.11-slim AS base
WORKDIR /app

RUN apt-get update && apt-get install -y --no-install-recommends     build-essential && rm -rf /var/lib/apt/lists/*

COPY pyproject.toml README.md ./
COPY codeslim/ ./codeslim/
COPY data/ ./data/

RUN pip install --no-cache-dir -e .

ENTRYPOINT ["codeslim"]
CMD ["--help"]
