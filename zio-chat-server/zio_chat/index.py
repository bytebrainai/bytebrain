import os

from langchain.embeddings.openai import OpenAIEmbeddings
from langchain.schema import Document
from langchain.text_splitter import MarkdownTextSplitter
from langchain.vectorstores import Chroma
from langchain.document_loaders import GitLoader


def update_vectorestore(texts: list[Document]):
    embeddings: OpenAIEmbeddings = OpenAIEmbeddings()
    Chroma.from_documents(texts, embeddings, persist_directory=os.environ["ZIOCHAT_CHROMA_DB_DIR"])


def index_markdown_docs(directory: str):
    documents: list[Document] = []

    for root, dirs, files in os.walk(directory):
        for filename in files:
            if filename.endswith('.md'):
                print(os.path.join(root, filename))
                from langchain.document_loaders import UnstructuredMarkdownLoader

                loader = UnstructuredMarkdownLoader(os.path.join(root, filename))
                documents.extend(loader.load())

    texts: list[Document] = MarkdownTextSplitter().split_documents(documents)
    return texts


def index_zio_project_docs():
    docs = index_markdown_docs(os.environ["ZIOCHAT_DOCS_DIR"])
    update_vectorestore(docs)


def index_zionomicon_book():
    docs = index_markdown_docs(os.environ["ZIOCHAT_ZIONOMICON_DOCS_DIR"])
    update_vectorestore(docs)


def index_zio_project_source_code():
    loader = GitLoader(
        repo_path=os.environ["ZIOCHAT_ZIO_REPO_DIR"],
        branch="series/2.x",
        file_filter=lambda file_path: file_path.endswith(".scala")
    )
    docs = loader.load()
    for doc in docs:
        print(doc.json())
    update_vectorestore(docs)


def index_all():
    index_zio_project_docs()
    index_zionomicon_book()
    index_zio_project_source_code()
