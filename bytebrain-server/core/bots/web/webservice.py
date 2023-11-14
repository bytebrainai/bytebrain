import asyncio
import json
import time
from typing import Any, List, Dict

import uvicorn
import weaviate
from fastapi import FastAPI, WebSocket
from fastapi.middleware.cors import CORSMiddleware
from langchain.embeddings import OpenAIEmbeddings, CacheBackedEmbeddings
from langchain.storage import LocalFileStore
from langchain.vectorstores.weaviate import Weaviate
from prometheus_client import Counter, Histogram, CollectorRegistry, generate_latest
from starlette.responses import Response, JSONResponse
from structlog import getLogger

from config import load_config
from core.llm.chains import make_question_answering_chain
from feedbacks import FeedbackService, FeedbackCreate

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Logging setup
log = getLogger()

# Configuration setup
config = load_config()

# Prometheus metrics setup
registry = CollectorRegistry()
request_counter = Counter("requests_total", "Total requests", registry=registry)
response_counter = Counter("responses_total", "Total responses", registry=registry)
response_time_histogram = Histogram("response_latency", "Response latency (seconds)",
                                    labelnames=["path"], registry=registry)

# Embeddings setup
underlying_embeddings: OpenAIEmbeddings = OpenAIEmbeddings()
fs = LocalFileStore(config.embeddings_dir)
cached_embedder = CacheBackedEmbeddings.from_bytes_store(
    underlying_embeddings, fs, namespace=underlying_embeddings.model
)

# Weaviate setup
client = weaviate.Client(url=config.weaviate_url)
vector_store = Weaviate(client,
                        index_name='Zio',
                        text_key="text",
                        attributes=['source', 'doc_source_id', 'doc_title', 'doc_url'],
                        embedding=cached_embedder,
                        by_text=False)

# Feedback service setup
feedback_service = FeedbackService(config.feedbacks_db)


# WebSocket endpoint for chat
@app.websocket("/chat")
async def websocket_chat_endpoint(websocket: WebSocket):
    await websocket.accept()
    start_time = time.time()
    request_counter.inc()

    qa = make_question_answering_chain(
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

        source_documents = extract_source_documents(result)
        unique_refs = extract_references(source_documents)

        await websocket.send_json({"token": "", "completed": True, "references": unique_refs[:3]})
        duration = time.time() - start_time
        response_time_histogram.labels(path="/chat").observe(duration)
        response_counter.inc()


def extract_references(source_documents) -> List[Dict[str, Any]]:
    references = [{k: v for k, v in d.items() if k != "page_content"} for d in source_documents]
    unique_refs = [dict(t) for t in {tuple(d.items()) for d in references}]
    return unique_refs


def extract_source_documents(result) -> list[dict[str, Any]]:
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
                log.warning(f"doc_source {doc_source_id} was not supported")
        else:
            log.warning("The doc_source is not exists in metadata")
    return source_documents


# WebSocket endpoint for dummy chat
@app.websocket("/dummy_chat")
async def websocket_dummy_chat_endpoint(websocket: WebSocket):
    await websocket.accept()
    while True:
        await websocket.receive_text()

        with open('core/bots/web/dummy/chat.md', 'r') as file:
            response = file.read()

        tokens = [{"token": token + " ", "completed": False} for token in response.split(" ")]
        tokens.append(
            {"completed": True,
             "references":
                 [{'page_title': 'Ref', 'page_url': 'https://zio.dev/reference/concurrency/ref'},
                  {'page_title': 'Global Shared State Using Ref',
                   'page_url': 'https://zio.dev/reference/state-management/global-shared-state'},
                  {'page_title': 'TRef', 'page_url': 'https://zio.dev/reference/stm/tref'}]}
        )
        for item in tokens:
            await asyncio.sleep(0.002)
            await websocket.send_json(item)


# Metrics endpoint
@app.get("/metrics")
async def metrics():
    return Response(generate_latest(registry), media_type="text/plain")


# Feedback creation endpoint
@app.post("/feedback/", response_model=FeedbackCreate)
def create_feedback(feedback: FeedbackCreate):
    feedback_service.add_feedback(feedback)
    return JSONResponse(content={"message": "Feedback received"}, status_code=200)


# Main function
def main():
    uvicorn.run("core.bots.web.webservice:app", host=config.webservice.host, port=config.webservice.port, reload=False)


if __name__ == "__main__":
    main()
