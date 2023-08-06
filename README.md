# ZIO Chat

A Chatbot for ZIO Ecosystem

## Install Development Environment

### ZIO Chat Server

Run the following steps:

```shell
nix-shell shell.nix
cd bytebrain-server
python -m venv .venv
source .venv/bin/activate
pip install poetry
poetry install
```

After running these steps, we can run any task defined inside `pyproject.toml`, e.g.:

```shell
poetry run webserver
```

## Installation

1. Define following env variables

```shell
export OPENAI_API_KEY=<openai_api_key>
export ZIOCHAT_DOCS_DIR=<docs_dir>
export ZIOCHAT_CHROMA_DB_DIR=<chroma_db_dir>
```

3. Index docs:

```shell
poetry run index
```

2. Run chart service:

```shell
poetry run webserver
```

Then open the chatbot on http://localhost:8081