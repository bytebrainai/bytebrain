import asyncio
import json
import time
from typing import Any

import uvicorn
from fastapi import FastAPI, WebSocket
from prometheus_client import Counter, Histogram, CollectorRegistry, generate_latest
from starlette.responses import Response
from structlog import getLogger

from config import load_config
from core.chatbot import make_question_answering_chatbot

app = FastAPI()
log = getLogger()
config = load_config()

registry = CollectorRegistry()

request_counter = Counter("requests_total", "Total requests", registry=registry)
response_counter = Counter("responses_total", "Total responses", registry=registry)
response_time_histogram = Histogram("response_latency", "Response latency (seconds)",
                                    labelnames=["path"], registry=registry)


@app.websocket("/chat")
async def websocket_endpoint(websocket: WebSocket):
    await websocket.accept()
    start_time = time.time()
    request_counter.inc()
    qa = make_question_answering_chatbot(
        websocket,
        config.db_dir,
        config.webservice_prompt
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
            if "source_doc" in metadata:
                source_doc = metadata["source_doc"]
                if source_doc == "zio.dev":
                    entry = {
                        "title": metadata["title"],
                        "url": metadata["url"],
                        "page_content": src_doc.page_content
                    }
                    log.info(entry)
                    source_documents.append(entry)
                elif source_doc == "discord":
                    metadata = src_doc.metadata
                    entry = {
                        "message_id": metadata["message_id"],
                        "channel_id": metadata["channel_id"],
                        "channel_name": metadata["channel_name"],
                        "guild_id": metadata["guild_id"],
                        "guild_name": metadata["guild_name"],
                        "page_content": src_doc.page_content
                    }
                    log.info(entry)
                    source_documents.append(entry)
                else:
                    log.warning(f"source_doc {source_doc} was not supported")
            else:
                log.warning("source_doc is not exist in metadata")

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


def main():
    uvicorn.run("core.webservice:app", host=config.host, port=config.port, reload=True)
