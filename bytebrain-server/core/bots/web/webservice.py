import asyncio
import json
import time
from enum import Enum
from typing import Any, List, Dict, Optional

import uvicorn
import weaviate
from fastapi import FastAPI, WebSocket
from fastapi.middleware.cors import CORSMiddleware
from core.dao.feedback_dao import FeedbackDao, Feedback
from langchain.embeddings import OpenAIEmbeddings, CacheBackedEmbeddings
from langchain.storage import LocalFileStore
from langchain.vectorstores.weaviate import Weaviate
from prometheus_client import Counter, Histogram, CollectorRegistry, generate_latest
from pydantic.main import BaseModel
from starlette.responses import Response, JSONResponse
from structlog import getLogger

from config import load_config
from core.dao.metadata_dao import MetadataDao
from core.dao.project_dao import ProjectDao, Project
from core.dao.resource_dao import ResourceType, ResourceDao
from core.docs.db.vectorstore_service import VectorStoreService
from core.llm.chains import make_question_answering_chain
from core.services.document_service import DocumentService
from core.services.project_service import ProjectService
from core.services.resource_service import ResourceService

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
                        index_name='Bytebrain',
                        text_key="text",
                        attributes=['source', 'doc_source_id', 'doc_title', 'doc_url'],
                        embedding=cached_embedder,
                        by_text=False)

# Feedback service setup
feedback_service = FeedbackDao(config.feedbacks_db)

# Resource service setup
document_service = DocumentService(config.weaviate_url,
                                   config.embeddings_dir,
                                   config.metadata_docs_db)
metadata_service = MetadataDao(config.metadata_docs_db)
vectorstore_service = VectorStoreService(url=config.weaviate_url,
                                         embeddings_dir=config.embeddings_dir,
                                         metadata_service=metadata_service)
resource_dao = ResourceDao(config.resources_db)
resource_service = ResourceService(resource_dao, vectorstore_service, metadata_service)

project_dao = ProjectDao(config.projects_db)
project_service = ProjectService(project_dao, resource_service)


# WebSocket endpoint for chat
@app.websocket("/chat/{project_id}")
async def websocket_chat_endpoint(websocket: WebSocket, project_id: str):
    await websocket.accept()
    start_time = time.time()
    request_counter.inc()

    qa = make_question_answering_chain(
        websocket=websocket,
        vector_store=vector_store,
        prompt_template=config.webservice.prompt,
        tenant=project_id
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


@app.post("/feedback/", response_model=Feedback)
def create_feedback(feedback: Feedback):
    feedback_service.add_feedback(feedback)
    return JSONResponse(content={"message": "Feedback received"}, status_code=200)


class WebsiteResourceRequest(BaseModel):
    name: str
    url: str
    project_id: str


@app.post("/resources/website")
async def submit_new_website_resource(resource: WebsiteResourceRequest):
    project = project_service.get_project_by_id(resource.project_id)
    if project is not None:
        resource_id = resource_service.submit_website_resource(resource.name, resource.url, resource.project_id)
    else:
        return JSONResponse({"message": "This project_id does not exist!", "project_id": resource.project_id},
                            status_code=404)
    if resource_id:
        return JSONResponse({"resource_id": resource_id, "status": "pending"}, status_code=202)
    else:
        return JSONResponse({"message": "This resource is already submitted"}, status_code=409)


class WebpageResourceRequest(BaseModel):
    name: str
    url: str
    project_id: str


@app.post("/resources/webpage")
async def submit_new_webpage_resource(resource: WebpageResourceRequest):
    project = project_service.get_project_by_id(resource.project_id)
    if project is not None:
        resource_id = resource_service.submit_webpage_resource(resource.name, resource.url, resource.project_id)
    else:
        return JSONResponse({"message": "This project_id does not exist!", "project_id": resource.project_id},
                            status_code=404)
    if resource_id:
        return JSONResponse({"resource_id": resource_id, "status": "pending"}, status_code=202)
    else:
        return JSONResponse({"message": "This resource is already submitted"}, status_code=409)


class YoutubeResourceRequest(BaseModel):
    name: str
    url: str
    project_id: str


@app.post("/resources/youtube")
async def submit_new_youtube_resource(resource: YoutubeResourceRequest):
    project = project_service.get_project_by_id(resource.project_id)
    if project is not None:
        resource_id = resource_service.submit_youtube_resource(resource.name, resource.url, resource.project_id)
    else:
        return JSONResponse({"message": "This project_id does not exist!", "project_id": resource.project_id},
                            status_code=404)
    if resource_id:
        return JSONResponse({"resource_id": resource_id, "status": "pending"}, status_code=202)
    else:
        return JSONResponse({"message": "This resource is already submitted"}, status_code=409)


class Language(str, Enum):
    CPP = "cpp"
    GO = "go"
    JAVA = "java"
    KOTLIN = "kotlin"
    JS = "js"
    TS = "ts"
    PHP = "php"
    PROTO = "proto"
    PYTHON = "python"
    RST = "rst"
    RUBY = "ruby"
    RUST = "rust"
    SCALA = "scala"
    SWIFT = "swift"
    MARKDOWN = "markdown"
    LATEX = "latex"
    HTML = "html"
    SOL = "sol"
    CSHARP = "csharp"


class GithubResourceRequest(BaseModel):
    name: str
    language: Language
    clone_url: str
    paths: Optional[str]
    branch: Optional[str]
    project_id: str


@app.post("/resources/github")
async def submit_new_github_resource(resource: GithubResourceRequest):
    paths = resource.paths if resource.paths is not None else "*"
    project = project_service.get_project_by_id(resource.project_id)
    if project is not None:
        resource_id = resource_service.submit_github_resource(resource.name,
                                                              resource.language.value,
                                                              resource.clone_url,
                                                              paths,
                                                              resource.branch,
                                                              resource.project_id)
    else:
        return JSONResponse({"message": "This project_id does not exist!", "project_id": resource.project_id},
                            status_code=404)
    if resource_id:
        return JSONResponse({"resource_id": resource_id, "status": "pending"}, status_code=202)
    else:
        return JSONResponse({"message": "This resource is already submitted"}, status_code=409)


@app.get("/resources/{resource_id}")
async def get_resource_status(resource_id: str):
    status_option = resource_service.get_resource_status(resource_id)
    match status_option:
        case None:
            return JSONResponse({"message": "Resource not found"}, status_code=404)
        case status:
            return JSONResponse({"status": status.value})


class UpdateRequest(BaseModel):
    request_id: str


@app.put("/resources/{resource_id}")
async def update_resource(resource_id: str):
    if resource_service.submit_resource_update(resource_id):
        return JSONResponse({
            "resource_id": resource_id,
            "message": "The update request has been submitted successfully."
        })
    else:
        return JSONResponse({
            "resource_id": resource_id,
            "message": f"Update request is forbidden. Last update was less than 24 hours ago."
        }, status_code=403)


@app.get("/resources/")
async def get_all_resources():
    return resource_service.get_all_resources()


@app.get("/resources/website/")
async def get_website_resources():
    return resource_service.get_resources_of_type(ResourceType.Website)


@app.get("/resources/webpage/")
async def get_webpage_resources():
    return resource_service.get_resources_of_type(ResourceType.Webpage)


@app.get("/resources/youtube/")
async def get_youtube_resources():
    return resource_service.get_resources_of_type(ResourceType.Webpage)


@app.get("/resources/github/")
async def get_youtube_resources():
    return resource_service.get_resources_of_type(ResourceType.GitHub)


@app.delete("/resources/{resource_id}", status_code=204)
async def delete_resource(resource_id: str):
    resource_service.delete_resource(resource_id)


@app.delete("/resources/", status_code=204)
async def delete_all_resources():
    resource_service.delete_all_resources()


@app.post("/projects/", response_model=Project, response_model_exclude_none=True)
async def create_project(body: Dict[str, str]):
    return project_service.create_project(name=body['name'])


@app.delete("/projects/{project_id}", status_code=204)
async def delete_project(project_id):
    project_service.delete_project(project_id)


@app.get("/projects/")
# TODO: exclude resources when its empty
async def get_all_projects():
    return project_service.get_all_projects()


@app.get("/projects/{project_id}")
async def get_project_by_id(project_id: str):
    project = project_service.get_project_by_id(project_id)
    if project:
        return project
    else:
        return JSONResponse({"message": f"Project not found!", "project_id": project_id})


# Main function
def main():
    uvicorn.run(app, host=config.webservice.host, port=config.webservice.port, reload=False)


if __name__ == "__main__":
    main()
