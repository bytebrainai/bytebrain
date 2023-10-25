import asyncio
import json
import time
from datetime import datetime
from typing import Any, List

import uvicorn
import weaviate
from fastapi import FastAPI, WebSocket
from fastapi.middleware.cors import CORSMiddleware
from langchain.embeddings import OpenAIEmbeddings, CacheBackedEmbeddings
from langchain.storage import LocalFileStore
from langchain.vectorstores.weaviate import Weaviate
from prometheus_client import Counter, Histogram, CollectorRegistry, generate_latest
from pydantic.main import BaseModel
from starlette.responses import Response, JSONResponse
from structlog import getLogger

from config import load_config
from core.chatbot_v2 import make_question_answering_chatbot

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

log = getLogger()
config = load_config()

registry = CollectorRegistry()

request_counter = Counter("requests_total", "Total requests", registry=registry)
response_counter = Counter("responses_total", "Total responses", registry=registry)
response_time_histogram = Histogram("response_latency", "Response latency (seconds)",
                                    labelnames=["path"], registry=registry)

underlying_embeddings: OpenAIEmbeddings = OpenAIEmbeddings()

fs = LocalFileStore(config.embeddings_dir)
cached_embedder = CacheBackedEmbeddings.from_bytes_store(
    underlying_embeddings, fs, namespace=underlying_embeddings.model
)

client = weaviate.Client(url=config.weaviate_url)
vector_store = Weaviate(client,
                        index_name='Zio',
                        text_key="text",
                        attributes=['source', 'doc_source_id', 'doc_title', 'doc_url'],
                        embedding=cached_embedder,
                        by_text=False)


@app.websocket("/chat")
async def websocket_endpoint(websocket: WebSocket):
    await websocket.accept()
    start_time = time.time()
    request_counter.inc()
    qa = make_question_answering_chatbot(
        websocket=websocket,
        vector_store=vector_store,
        prompt_template=config.webservice.prompt
    )
    while True:
        raw_data = await websocket.receive_text()
        obj = json.loads(raw_data)
        log.info("Received a new query!", query=obj)
        result: dict[str, Any] = await qa.acall(
            {
                "question": obj["question"],
                "project_name": config.project_name,
                "chat_history": obj["history"]
            },
            return_only_outputs=True
        )

        source_documents: list[dict[str, Any]] = []
        for src_doc in result["source_documents"]:
            metadata = src_doc.metadata
            if "doc_source_id" in metadata:
                doc_source_id = metadata["doc_source_id"]
                if doc_source_id == "zio.dev":
                    entry = {
                        "page_title": metadata["doc_title"],
                        "page_url": metadata["doc_url"],
                        "page_content": src_doc.page_content
                    }
                    log.info(entry)
                    source_documents.append(entry)
                else:
                    # TODO: Add support for other source types
                    log.warning(f"doc_source {doc_source_id} was not supported")
            else:
                log.warning("The doc_source is not exists in metadata")

        references = [{k: v for k, v in d.items() if k != "page_content"} for d in source_documents]
        unique_refs = [dict(t) for t in {tuple(d.items()) for d in references}]

        await websocket.send_json({"token": "", "completed": True, "references": unique_refs[:3]})
        duration = time.time() - start_time
        response_time_histogram.labels(path="/chat").observe(duration)
        response_counter.inc()


@app.websocket("/dummy_chat")
async def websocket_endpoint(websocket: WebSocket):
    await websocket.accept()
    while True:
        await websocket.receive_text()

        with open('core/dummy/chat.md', 'r') as file:
            response = file.read()

        tokens = [{"token": token + " ", "completed": False} for token in response.split(" ")]
        tokens.append(
            {"completed": True,
             "references":
                 [{'title': 'Ref', 'url': 'https://zio.dev/reference/concurrency/ref'},
                  {'title': 'Global Shared State Using Ref',
                   'url': 'https://zio.dev/reference/state-management/global-shared-state'},
                  {'title': 'TRef', 'url': 'https://zio.dev/reference/stm/tref'}]}
        )
        for item in tokens:
            await asyncio.sleep(0.02)
            await websocket.send_json(item)


@app.get("/metrics")
async def metrics():
    return Response(generate_latest(registry), media_type="text/plain")


def create_feedback_db():
    import sqlite3
    conn = sqlite3.connect('./db/feedbacks.db')
    cursor = conn.cursor()

    cursor.execute('''
        CREATE TABLE IF NOT EXISTS feedbacks (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            chat_history JSON,
            is_useful BOOLEAN,
            created_at DATETIME
        )
    ''')

    conn.commit()
    conn.close()


class FeedbackCreate(BaseModel):
    chat_history: List[Any]
    is_useful: bool


@app.post("/feedback/", response_model=FeedbackCreate)
def create_feedback(feedback: FeedbackCreate):
    import sqlite3
    conn = sqlite3.connect('feedbacks.db')
    cursor = conn.cursor()
    created_at = datetime.utcnow()

    cursor.execute('''
        INSERT INTO feedbacks (chat_history, is_useful, created_at) 
        VALUES (?, ?, ?)
    ''', (json.dumps(feedback.chat_history), feedback.is_useful, created_at))

    conn.commit()
    conn.close()

    return JSONResponse(content={"message": "Feedback received"}, status_code=200)


def main():
    create_feedback_db()
    uvicorn.run("core.webservice:app", host=config.webservice.host, port=config.webservice.port, reload=False)


if __name__ == "__main__":
    main()
