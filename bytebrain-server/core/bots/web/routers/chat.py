# Copyright 2023-2024 ByteBrain AI
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

import asyncio
import json
import time
from typing import Any, List
from typing import Dict

from fastapi import APIRouter
from fastapi import WebSocket
from langchain.vectorstores import Weaviate
from prometheus_client import Counter, Histogram, CollectorRegistry, generate_latest
from starlette.responses import Response
from structlog import getLogger
from websockets.exceptions import WebSocketException

from config import load_config
from core.bots.web.auth import *
from core.bots.web.dependencies import project_service
from core.bots.web.dependencies import project_service
from core.bots.web.dependencies import weaviate
from core.llm.chains import make_question_answering_chain
from core.services.project_service import ProjectService

config = load_config()

chat_router = router = APIRouter()

log = getLogger()


class ProjectNotFoundException(WebSocketException):
    def __init__(self, project_id, message, *args):
        super().__init__(*args)
        self.project_id = project_id
        self.message = message


# WebSocket endpoint for chat
@router.websocket("/chat/{apikey}")
async def websocket_chat_endpoint(websocket: WebSocket, apikey: str,
                                  project_service: Annotated[ProjectService, Depends(project_service)],
                                  weaviate: Annotated[Weaviate, Depends(weaviate)]):
    try:
        await websocket.accept()

        domain = websocket.headers.get('host').split(':')[0]

        if not project_service.is_allowed(domain, apikey):
            await websocket.close()
            raise WebSocketException("You cannot access this api from this domain!")

        project = project_service.get_project_by_apikey(apikey)
        if project is None:
            raise Exception("Project not found!")

        start_time = time.time()
        request_counter.inc()

        qa = make_question_answering_chain(
            websocket=websocket,
            vector_store=weaviate,
            prompt_template=config.webservice.prompt
        )

        while True:
            query = json.loads(await websocket.receive_text())
            log.info("Received a new query!", query=query)

            result: dict[str, Any] = await qa.acall(
                {
                    "question": query["question"],
                    "project_name": config.project_name,
                    "chat_history": query["history"]
                },
                return_only_outputs=True
            )

            source_documents = extract_source_documents(result)
            unique_refs = extract_references(source_documents)

            await websocket.send_json({"token": "", "completed": True, "references": unique_refs[:3]})
            duration = time.time() - start_time
            response_time_histogram.labels(path="/chat").observe(duration)
            response_counter.inc()

    except ProjectNotFoundException as e:
        # Handle HTTP exceptions (e.g., project not found)
        await websocket.send_json({"error": e.message})
        await websocket.close()
        log.error("WebSocket closed!", cause=e.message, project_id=e.project_id)

    except Exception as e:
        # Handle other exceptions
        error_message = "Internal server error"
        await websocket.send_json({"error": error_message})
        await websocket.close(code=1011)
        log.error(f"WebSocket error!", cause=str(e))


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
@router.websocket("/dummy_chat/{project_id}")
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


# Prometheus metrics setup
registry = CollectorRegistry()
request_counter = Counter("requests_total", "Total requests", registry=registry)
response_counter = Counter("responses_total", "Total responses", registry=registry)
response_time_histogram = Histogram("response_latency", "Response latency (seconds)",
                                    labelnames=["path"], registry=registry)


# Metrics endpoint
@router.get("/metrics")
async def metrics():
    return Response(generate_latest(registry), media_type="text/plain")
