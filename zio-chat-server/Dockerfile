# Use the Python base image
FROM python:3.10.11-bullseye

ARG POETRY_HOME=/opt/poetry
ARG POETRY_VERSION=1.4.2
ARG POETRY_HOME

RUN python3 -m venv ${POETRY_HOME} && \
    $POETRY_HOME/bin/pip install --upgrade pip && \
    $POETRY_HOME/bin/pip install poetry==${POETRY_VERSION}
RUN echo "Poetry version:" && $POETRY_HOME/bin/poetry --version

WORKDIR /app
COPY pyproject.toml poetry.lock /app
RUN $POETRY_HOME/bin/poetry install --no-interaction --no-ansi
COPY . /app

ENTRYPOINT ["/opt/poetry/bin/poetry", "run", "webserver"]
