# ZIO Chat

A Chatbot for ZIO Ecosystem

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