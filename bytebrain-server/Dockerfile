# Use the Python base image
FROM python:3.10.12-bullseye

ARG POETRY_VERSION=1.5.1

WORKDIR /app
RUN python3 -m venv .venv && \
    . .venv/bin/activate && \
    pip install --upgrade pip && \
    pip install poetry==${POETRY_VERSION} && \
    echo "Poetry version:" && poetry --version

COPY pyproject.toml poetry.lock /app
RUN . .venv/bin/activate && poetry install --no-interaction --no-ansi
COPY . /app

ENTRYPOINT ["/app/.venv/bin/poetry", "run", "main"]

