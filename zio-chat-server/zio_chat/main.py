import asyncio
import json
import os
import time
from typing import Any

import uvicorn
from fastapi import FastAPI, WebSocket
from prometheus_client import Counter, Histogram, CollectorRegistry, generate_latest
from starlette.responses import Response
from structlog import getLogger

from zio_chat.chatbot import make_question_answering_chatbot

app = FastAPI()
log = getLogger()

registry = CollectorRegistry()

# Define your metrics
request_counter = Counter("requests_total", "Total requests", registry=registry)
response_counter = Counter("responses_total", "Total responses", registry=registry)
response_time_histogram = Histogram("response_latency", "Response latency (seconds)",
                                    labelnames=["path"], registry=registry)


@app.websocket("/chat")
async def websocket_endpoint(websocket: WebSocket):
    await websocket.accept()
    start_time = time.time()
    request_counter.inc()
    qa = make_question_answering_chatbot(websocket, os.environ["ZIOCHAT_CHROMA_DB_DIR"])
    while True:
        raw_data = await websocket.receive_text()
        obj = json.loads(raw_data)
        log.info("Received a new query!", query=obj)
        result: dict[str, Any] = await qa.acall(
            {
                "question": obj["question"],
                "project_name": "ZIO",
                "chat_history": obj["history"]
            },
            return_only_outputs=True
        )

        source_documents: list[dict[str, Any]] = []
        for src_doc in result["source_documents"]:
            try:
                page_content = src_doc.page_content
                metadata = src_doc.metadata
                entry = {"title": metadata["title"], "url": metadata["url"], "page_content": page_content}
                source_documents.append(entry)
            except (KeyError, AttributeError) as e:
                print(f"no title and url metadata found: {str(e)}")

        response = {
            "answer": result["answer"],
            "source_documents": source_documents
        }

        references = [{k: v for k, v in d.items() if k != "page_content"} for d in source_documents]

        log.info("Response is generated!", response=response)
        await websocket.send_json({"token": "", "completed": True, "references": references[:3]})
        duration = time.time() - start_time
        response_time_histogram.labels(path="/chat").observe(duration)
        response_counter.inc()


@app.websocket("/dummy_chat")
async def websocket_endpoint(websocket: WebSocket):
    await websocket.accept()
    while True:
        await websocket.receive_text()

        with open('zio_chat/dummy/chat.md', 'r') as file:
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


def start():
    uvicorn.run("zio_chat.main:app", host="0.0.0.0", port=8081, reload=True)
