import os

from langchain.embeddings import CacheBackedEmbeddings
from langchain.embeddings.openai import OpenAIEmbeddings
from langchain.storage import LocalFileStore
from langchain.vectorstores import Weaviate
from weaviate import Client

from config import load_config
from core.bots.web.auth import *
from core.dao.apikey_dao import ApiKeyDao
from core.dao.feedback_dao import FeedbackDao
from core.dao.metadata_dao import MetadataDao
from core.dao.project_dao import ProjectDao
from core.dao.resource_dao import ResourceDao
from core.services.project_service import ProjectService
from core.services.resource_service import ResourceService
from core.services.vectorstore_service import VectorStoreService

config = load_config()

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


def weaviate():
    return Weaviate(weaviate_client,
                    index_name=index_name,
                    text_key=text_key,
                    attributes=['source'],
                    embedding=cached_embedder,
                    by_text=False)


# Vectorstore service setup
def vectorstore_service(weaviate: Annotated[Weaviate, Depends(weaviate)]):
    return VectorStoreService(weaviate, weaviate_client, cached_embedder, index_name, text_key)


# Resource service setup
def metadata_dao():
    return MetadataDao(config.metadata_docs_db)


def resource_dao():
    return ResourceDao(config.resources_db)


def resource_service(
        resource_dao: Annotated[ResourceDao, Depends(resource_dao)],
        vectorstore_service: Annotated[VectorStoreService, Depends(vectorstore_service)],
        metadata_dao: Annotated[MetadataDao, Depends(metadata_dao)]):
    return ResourceService(resource_dao, vectorstore_service, metadata_dao)


# document_service = DocumentService(vectorstore_service, metadata_dao)

def project_dao():
    return ProjectDao(config.projects_db)


def apikey_dao():
    return ApiKeyDao(config.projects_db)


def project_service(project_dao: Annotated[ProjectDao, Depends(project_dao)],
                    resource_service: Annotated[ResourceService, Depends(resource_service)],
                    apikey_dao: Annotated[ApiKeyDao, Depends(apikey_dao)]):
    return ProjectService(project_dao, resource_service, apikey_dao)
