# syntax=docker/dockerfile:1
FROM python:3.12-slim AS base

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PIP_NO_CACHE_DIR=1

WORKDIR /app

# System deps: gcc for pdfminer/lxml; texlive for PDF compilation
RUN apt-get update && apt-get install -y --no-install-recommends \
    gcc \
    texlive-latex-base \
    texlive-latex-extra \
    texlive-fonts-recommended \
    && rm -rf /var/lib/apt/lists/*

COPY requirements.txt .
RUN pip install --upgrade pip && pip install -r requirements.txt

# Copy backend source
COPY app/ ./app/

# Copy tailor-resume scripts (pipeline, parsers, stores, etc.)
COPY ../../.claude/skills/tailor-resume/scripts/ ./scripts/

ENV PYTHONPATH=/app/scripts

CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
