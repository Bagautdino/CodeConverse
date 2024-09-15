FROM python:3.12 as builder

WORKDIR /code_converse

COPY . .

RUN pip install --no-cache-dir -r requirements.txt

FROM python:3.12-slim

WORKDIR /code_converse

COPY --from=builder /usr/local/lib/python3.12/site-packages/ /usr/local/lib/python3.12/site-packages/

COPY --from=builder /code_converse /code_converse




