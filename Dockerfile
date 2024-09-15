FROM python:3.12 as builder

WORKDIR /ai-sast-tool

COPY . .

RUN pip install --no-cache-dir -r requirements.txt

FROM python:3.12-slim

WORKDIR /ai-sast-tool

COPY --from=builder /usr/local/lib/python3.12/site-packages/ /usr/local/lib/python3.12/site-packages/

COPY --from=builder /ai-sast-tool /ai-sast-tool




