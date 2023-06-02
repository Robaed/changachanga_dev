#FROM tiangolo/uvicorn-gunicorn-fastapi:python3.10-slim AS builder
FROM python:3.10-slim AS builder

WORKDIR /app

RUN apt-get update && \
    apt-get install -y libpq-dev gcc && \
    pip install poetry && \
    poetry config virtualenvs.create false

# Copy poetry.lock* in case it doesn't exist in the repo
COPY ./app/pyproject.toml /app/poetry.lock* /app/

RUN --mount=type=cache,target=/root/.cache/pip \
    poetry install --only main --no-root --compile

COPY ./app /app

COPY ./app/app-start.sh /app-start.sh
RUN chmod +x ./app-start.sh
ENV PYTHONPATH=/app

CMD ["/bin/sh", "app-start.sh"]
