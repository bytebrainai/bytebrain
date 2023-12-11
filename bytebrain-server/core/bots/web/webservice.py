import asyncio
import json
import os
import time
from enum import Enum
from typing import Any, List
from typing import Dict

import uvicorn
from fastapi import FastAPI, WebSocket
from fastapi.middleware.cors import CORSMiddleware
from fastapi.security import OAuth2PasswordRequestForm
from langchain.embeddings import CacheBackedEmbeddings
from langchain.embeddings.openai import OpenAIEmbeddings
from langchain.storage import LocalFileStore
from langchain.vectorstores import VectorStore
from langchain.vectorstores import Weaviate
from prometheus_client import Counter, Histogram, CollectorRegistry, generate_latest
from pydantic.main import BaseModel
from starlette.responses import Response, JSONResponse
from structlog import getLogger
from weaviate import Client
from websockets.exceptions import WebSocketException

from config import load_config
from core.bots.web.auth import *
from core.dao.feedback_dao import FeedbackDao, Feedback
from core.dao.metadata_dao import MetadataDao
from core.dao.project_dao import ProjectDao, Project
from core.dao.resource_dao import ResourceDao
from core.dao.user_dao import UserInDB, UserDao, User
from core.llm.chains import make_question_answering_chain
from core.services.document_service import DocumentService
from core.services.project_service import ProjectService
from core.services.resource_service import ResourceService
from core.services.vectorstore_service import VectorStoreService

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

# Feedback service setup
feedback_service = FeedbackDao(config.feedbacks_db)

# Vectorstore setup
index_name = 'Bytebrain'
text_key = "text"
os.environ['WEAVIATE_URL'] = config.weaviate_url
embeddings_dir = config.embeddings_dir
weaviate_client = Client(url=config.weaviate_url)
underlying_embeddings: OpenAIEmbeddings = OpenAIEmbeddings()
fs = LocalFileStore(config.embeddings_dir)
cached_embedder = CacheBackedEmbeddings.from_bytes_store(
    underlying_embeddings, fs, namespace=underlying_embeddings.model
)
weaviate: VectorStore = Weaviate(weaviate_client,
                                 index_name=index_name,
                                 text_key=text_key,
                                 attributes=['source'],
                                 embedding=cached_embedder,
                                 by_text=False)

# Vectorstore service setup
vectorstore_service = VectorStoreService(weaviate, weaviate_client, cached_embedder, index_name, text_key)

# Resource service setup
metadata_dao = MetadataDao(config.metadata_docs_db)
resource_dao = ResourceDao(config.resources_db)
resource_service = ResourceService(resource_dao, vectorstore_service, metadata_dao)

# Document service setup
document_service = DocumentService(vectorstore_service, metadata_dao)

# Project service setup
project_dao = ProjectDao(config.projects_db)
project_service = ProjectService(project_dao, resource_service)


class Token(BaseModel):
    access_token: str
    token_type: str


def user_dao():
    return UserDao()


class ProjectNotFoundException(WebSocketException):
    def __init__(self, project_id, message, *args):
        super().__init__(*args)
        self.project_id = project_id
        self.message = message


# WebSocket endpoint for chat
@app.websocket("/chat/{project_id}")
async def websocket_chat_endpoint(websocket: WebSocket, project_id: str):
    try:
        await websocket.accept()

        if project_service.get_project_by_id(project_id) is None:
            raise ProjectNotFoundException(message="Project not found!", project_id=project_id)

        start_time = time.time()
        request_counter.inc()

        qa = make_question_answering_chain(
            websocket=websocket,
            vector_store=weaviate,
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
@app.websocket("/dummy_chat/{project_id}")
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


# TODO: use resource_type instead of separate apis for each resource
@app.post("/resources/website", tags=["Resources"])
async def submit_new_website_resource(resource: WebsiteResourceRequest,
                                      current_user: Annotated[User, Depends(get_current_active_user)]):
    project = project_service.get_project_by_id(resource.project_id)
    if project is not None:
        if project.username == current_user.username:
            resource_id = resource_service.submit_website_resource(resource.name, resource.url, resource.project_id)
        else:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="User does not have permission to add resource to the specified project!"
            )
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


@app.post("/resources/webpage", tags=["Resources"])
async def submit_new_webpage_resource(resource: WebpageResourceRequest,
                                      current_user: Annotated[User, Depends(get_current_active_user)]):
    project = project_service.get_project_by_id(resource.project_id)
    if project is not None:
        if project.username == current_user.username:
            resource_id = resource_service.submit_webpage_resource(resource.name, resource.url, resource.project_id)
        else:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="User does not have permission to add resource to the specified project!"
            )
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


@app.post("/resources/youtube", tags=["Resources"])
async def submit_new_youtube_resource(resource: YoutubeResourceRequest,
                                      current_user: Annotated[User, Depends(get_current_active_user)]):
    project = project_service.get_project_by_id(resource.project_id)
    if project is not None:
        if project.username == current_user.username:
            resource_id = resource_service.submit_youtube_resource(resource.name, resource.url, resource.project_id)
        else:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="User does not have permission to add resource to the specified project!"
            )
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
    branch: str = "main"
    project_id: str


@app.post("/resources/github", tags=["Resources"])
async def submit_new_github_resource(resource: GithubResourceRequest,
                                     current_user: Annotated[User, Depends(get_current_active_user)]):
    paths = resource.paths if resource.paths is not None else "*"
    project = project_service.get_project_by_id(resource.project_id)
    if project is not None:
        if project.username == current_user.username:
            resource_id = resource_service.submit_github_resource(resource.name,
                                                                  resource.language.value,
                                                                  resource.clone_url,
                                                                  paths,
                                                                  resource.branch,
                                                                  resource.project_id)
        else:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="User does not have permission to add resource to specified project!"
            )
    else:
        return JSONResponse({"message": "This project_id does not exist!", "project_id": resource.project_id},
                            status_code=404)
    if resource_id:
        return JSONResponse({"resource_id": resource_id, "status": "pending"}, status_code=202)
    else:
        return JSONResponse({"message": "This resource is already submitted"}, status_code=409)


class UpdateRequest(BaseModel):
    request_id: str


@app.put("/resources/{resource_id}", tags=["Resources"])
async def update_resource(
        resource_id: str,
        current_user: Annotated[User, Depends(get_current_active_user)]):
    resource = resource_service.get_resource_by_id(resource_id)
    project = project_service.get_project_by_id(resource.project_id)
    if project.username == current_user.username:
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
    else:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="User does not have permission to update this resource!"
        )


@app.delete("/resources/{resource_id}", status_code=204, tags=["Resources"])
async def delete_resource(resource_id: str,
                          current_user: Annotated[User, Depends(get_current_active_user)]):
    resource = resource_service.get_resource_by_id(resource_id)
    if resource is not None:
        project = project_service.get_project_by_id(resource.project_id)
        if project is not None:
            if project.username == current_user.username:
                resource_service.delete_resource(resource_id)
            else:
                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN,
                    detail="User does not have permission to delete the resource!"
                )
    else:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Resource not found!"
        )


class ProjectCreation(BaseModel):
    name: str


@app.post("/projects/", response_model=Project, response_model_exclude_none=True, tags=["Projects"])
async def create_project(project: ProjectCreation,
                         current_user: Annotated[User, Depends(get_current_active_user)]):
    return project_service.create_project(name=project.name, username=current_user.username)


@app.delete("/projects/{project_id}", status_code=204, tags=["Projects"])
async def delete_project(
        project_id,
        current_user: Annotated[User, Depends(get_current_active_user)]):
    project_service.delete_project(project_id, current_user.username)


@app.delete("/projects/", status_code=204, tags=["Projects"])
async def delete_all_project(
        current_user: Annotated[User, Depends(get_current_active_user)]):
    project_service.delete_projects_owned_by(current_user.username)


@app.get("/projects/", response_model=list[Project], tags=["Projects"])
# TODO: exclude resources when its empty
async def get_all_projects(current_user: Annotated[User, Depends(get_current_active_user)]) -> Any:
    return project_service.get_all_projects(current_user.username)


@app.get("/projects/{project_id}", tags=["Projects"])
async def get_project_by_id(project_id: str, current_user: Annotated[User, Depends(get_current_active_user)]):
    project = project_service.get_project_by_id(project_id)
    if project.username == current_user.username:
        if project:
            return project
        else:
            return JSONResponse({"message": f"Project not found!", "project_id": project_id})
    else:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="User does not have permission to this project!"
        )


@app.post("/token", response_model=Token, tags=['Authentication'])
async def login_for_access_token(
        form_data: Annotated[OAuth2PasswordRequestForm, Depends()],
        user_dao: Annotated[UserDao, Depends(user_dao)]
):
    user = authenticate_user(form_data.username, form_data.password, user_dao)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": user.username}, expires_delta=access_token_expires
    )
    return {"access_token": access_token, "token_type": "bearer"}


@app.get("/users/me/", response_model=User, tags=["Authentication"])
async def read_users_me(
        current_user: Annotated[User, Depends(get_current_active_user)]
):
    return current_user


@app.post("/register", response_model=Dict[str, str], tags=["Authentication"])
async def register(
        form_data: Annotated[OAuth2PasswordRequestForm, Depends()],
        user_dao: Annotated[UserDao, Depends(user_dao)]
):
    existing_user = user_dao.get_user(form_data.username)
    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Username already registered",
        )

    hashed_password = get_password_hash(form_data.password)
    user_dao.save_user(UserInDB(username=form_data.username, hashed_password=hashed_password))

    return {"username": form_data.username}


# Main function
def main():
    uvicorn.run(app, host=config.webservice.host, port=config.webservice.port, reload=False)


if __name__ == "__main__":
    main()
