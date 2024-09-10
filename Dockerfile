FROM python:3.12-slim as builder

RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    libpq-dev \
    gcc \
    && rm -rf /var/lib/apt/lists/*

RUN pip install --upgrade pip

WORKDIR /ai-sast-tool

COPY requirements.txt .

RUN pip install --no-cache-dir -r requirements.txt

COPY . .

ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1

# Add this line to debug and confirm the path
RUN ls -la /usr/local/lib

FROM gcr.io/distroless/python3

# Adjust this line if the path is confirmed to be different
COPY --from=builder /usr/local/lib/python3.12/site-packages /usr/local/lib/python3.12/site-packages
COPY --from=builder /ai-sast-tool /ai-sast-tool

WORKDIR /ai-sast-tool
