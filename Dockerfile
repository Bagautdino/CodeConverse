FROM python:3.12-slim as builder

RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    libpq-dev \
    gcc \
    && rm -rf /var/lib/apt/lists/*

RUN pip install --upgrade pip

WORKDIR /ai-sast-tool

COPY . .

RUN pip install --no-cache-dir -r requirements.txt




