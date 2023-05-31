import os

from langchain.embeddings.openai import OpenAIEmbeddings
from langchain.schema import Document
from langchain.text_splitter import MarkdownTextSplitter
from langchain.vectorstores import Chroma


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


def index_zio_project():
    docs = index_markdown_docs(os.environ["ZIOCHAT_DOCS_DIR"])
    update_vectorestore(docs)


def index_zionomicon():
    docs = index_markdown_docs(os.environ["ZIONOMICON_DOCS_DIR"])
    update_vectorestore(docs)


def index_all():
    index_zio_project()
    index_zionomicon()
