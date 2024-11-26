import os
import uuid
from typing import Optional, List, Dict
from uuid import UUID
import re

import yaml
from langchain.document_loaders import GitLoader
from langchain.document_loaders import UnstructuredMarkdownLoader
from langchain.document_loaders import YoutubeLoader
from langchain.document_loaders.recursive_url_loader import RecursiveUrlLoader
from langchain.document_transformers.html2text import Html2TextTransformer
from langchain.schema import Document
from langchain.text_splitter import Language
from langchain.text_splitter import MarkdownTextSplitter
from langchain.text_splitter import RecursiveCharacterTextSplitter

from core.utils import calculate_md5_checksum

NAMESPACE_DOCUMENT = UUID('f924e0a9-69a7-11ee-aa84-6c02e09469ba')
NAMESPACE_WEBSITE = UUID('c88b857e-be16-4d80-9f45-b5c41fdd4a11')
NAMESPACE_YOUTUBE = UUID('1572e8de-29bf-464e-9253-656bd7c78938')
NAMESPACE_SOURCECODE = UUID('86adfa90-25d6-45bc-894c-8e1bb5c8ce76')


def generate_uuid(namespace: UUID, doc_source_type, doc_source_id, doc_path, doc_hash) -> UUID:
    return uuid.uuid5(namespace, f"{doc_source_type}:{doc_source_id}:{doc_path}:{doc_hash}")


def load_zio_website_docs(directory: str) -> (List[UUID], List[Document]):
    def extract_metadata(md_file_path: str) -> Dict[str, str]:
        with open(md_file_path, 'r') as file:
            content = file.read()

        # Parse YAML front matter
        try:
            _, yaml_content, _ = content.split('---', 2)
            meta_data = yaml.safe_load(yaml_content)
            return {"id": meta_data.get('id'), "title": meta_data.get("title")}
        except ValueError:
            file_name = os.path.basename(md_file_path)
            return {"id": file_name, "title": file_name}

    documents: list[Document] = []
    for root, dirs, files in os.walk(directory):
        for filename in files:
            if filename.endswith('.md'):
                md_path = os.path.join(root, filename)
                docs: list[Document] = UnstructuredMarkdownLoader(md_path).load()
                docs = MarkdownTextSplitter().split_documents(docs)
                metadata: dict[str, str] = extract_metadata(md_path)
                for index, doc in enumerate(docs):
                    doc_id = root.split("/zio/website/docs/")[1] + '/' + metadata["id"]
                    doc.metadata["doc_path"] = doc.metadata["source"].split("/zio/website/docs/")[1]
                    doc.metadata["source"] = doc_id
                    doc.metadata.setdefault("doc_source_type", "documentation")
                    doc.metadata.setdefault("doc_source_id", "zio.dev")
                    doc.metadata.setdefault("doc_id", doc_id)
                    doc.metadata.setdefault("doc_title", metadata["title"])
                    doc.metadata.setdefault("doc_url", f"https://zio.dev/{doc.metadata['doc_id']}")
                    doc.metadata.setdefault("doc_hash", calculate_md5_checksum(doc.page_content))
                    doc.metadata.setdefault("doc_uuid",
                                            str(generate_uuid(
                                                NAMESPACE_DOCUMENT,
                                                doc.metadata['doc_source_type'],
                                                doc.metadata['doc_source_id'],
                                                doc.metadata['doc_path'],
                                                doc.metadata['doc_hash']
                                            )))
                documents.extend(docs)

    ids: List[UUID] = [UUID(doc.metadata['doc_uuid']) for doc in documents]

    assert (len(ids) == len(documents))
    return ids, documents


def load_source_code(
        repo_path: str,
        branch: Optional[str],
        source_id: str
) -> (List[UUID], List[Document]):
    loader = GitLoader(
        repo_path=repo_path,
        branch=branch,
        file_filter=lambda file_path: file_path.endswith(".scala")
    )
    docs = loader.load()
    splitter = RecursiveCharacterTextSplitter.from_language(language=Language.SCALA)
    docs = splitter.transform_documents(docs)

    for index, doc in enumerate(docs):
        doc.metadata.setdefault("doc_source_type", "source_code")
        doc.metadata.setdefault("doc_source_id", source_id)
        doc.metadata.setdefault("doc_hash", calculate_md5_checksum(doc.page_content))
        doc.metadata.setdefault("doc_path", doc.metadata.pop('file_path'))
        doc.metadata.setdefault("doc_uuid",
                                str(generate_uuid(NAMESPACE_SOURCECODE,
                                                  doc.metadata['doc_source_type'],
                                                  doc.metadata['doc_source_id'],
                                                  doc.metadata['doc_path'],
                                                  doc.metadata['doc_hash'])))

    ids: List[UUID] = [UUID(doc.metadata['doc_uuid']) for doc in docs]

    assert (len(ids) == len(docs))
    return ids, docs


def extract_first_heading(content: str) -> str:
    # Look for ATX-style headers (# Title) or Setext-style (Title\n===)
    atx_match = re.search(r'^#\s+(.+?)$', content, re.MULTILINE)
    if atx_match:
        return atx_match.group(1).strip()

    setext_match = re.search(r'^(.+?)\n[=]+\s*$', content, re.MULTILINE)
    if setext_match:
        return setext_match.group(1).strip()

    return "Untitled"  # Fallback if no heading found

def load_zionomicon_docs(directory: str) -> (List[UUID], List[Document]):
    documents: list[Document] = []

    # Debug: Print the directory being searched
    print(f"Searching for markdown files in: {directory}")

    if not os.path.exists(directory):
        print(f"Error: Directory {directory} does not exist")
        return [], []

    for root, dirs, files in os.walk(directory):
        # Debug: Print current directory being processed
        print(f"Processing directory: {root}")
        print(f"Found files: {files}")

        for file_name in files:
            if file_name.endswith('.md'):
                md_path = os.path.join(root, file_name)
                print(f"Processing markdown file: {md_path}")

                try:
                    # Read the file content first to extract the title
                    with open(md_path, 'r', encoding='utf-8') as f:
                        content = f.read()
                        title = extract_first_heading(content)
                        print(f"Extracted title: {title}")

                    docs: list[Document] = UnstructuredMarkdownLoader(md_path).load()
                    docs = MarkdownTextSplitter().split_documents(docs)
                    print(f"Split into {len(docs)} documents")

                    for index, doc in enumerate(docs):
                        doc.metadata.setdefault("doc_source_id", "zionomicon")
                        doc.metadata.setdefault("doc_source_type", "documentation")
                        doc.metadata.setdefault("doc_path", doc.metadata.pop('source').split("/zionomicon/docs/")[1])
                        doc.metadata.setdefault("doc_chapter", title)
                        doc.metadata.setdefault("doc_hash", calculate_md5_checksum(doc.page_content))
                        doc.metadata.setdefault(
                            "doc_uuid",
                            str(
                                generate_uuid(
                                    NAMESPACE_DOCUMENT,
                                    doc.metadata['doc_source_type'],
                                    doc.metadata['doc_source_id'],
                                    doc.metadata['doc_path'],
                                    doc.metadata['doc_hash']
                                )
                            )
                        )
                    documents.extend(docs)
                except Exception as e:
                    print(f"Error processing file {md_path}: {str(e)}")
                    continue

    ids: List[UUID] = [UUID(doc.metadata['doc_uuid']) for doc in documents]

    # Debug: Print final counts
    print(f"Total documents processed: {len(documents)}")
    print(f"Total IDs generated: {len(ids)}")

    assert (len(ids) == len(documents))
    return ids, documents


def load_youtube_docs(video_id: str) -> (List[UUID], List[Document]):
    video_url = f"https://www.youtube.com/watch?v={video_id}"
    loader = YoutubeLoader.from_youtube_url(video_url, add_video_info=True)
    docs: list[Document] = loader.load()
    text_splitter = RecursiveCharacterTextSplitter(chunk_size=2000, chunk_overlap=200)
    docs = text_splitter.split_documents(docs)
    for index, doc in enumerate(docs):
        doc.metadata.setdefault("doc_source_id", "youtube.com")
        doc.metadata.setdefault("doc_source_type", "subtitle")
        doc.metadata.setdefault("doc_url", video_url)
        doc.metadata.setdefault("doc_title", doc.metadata.pop('title'))
        doc.metadata.setdefault("doc_view_count", doc.metadata.pop('view_count'))
        doc.metadata.setdefault("doc_thumbnail_url", doc.metadata.pop('thumbnail_url'))
        doc.metadata.setdefault("doc_publish_date", doc.metadata.pop("publish_date"))
        doc.metadata.setdefault("doc_length", doc.metadata.pop("length"))
        doc.metadata.setdefault("doc_author", doc.metadata.pop("author"))
        doc.metadata.setdefault("doc_uuid", str(uuid.uuid5(NAMESPACE_YOUTUBE, video_url + doc.page_content)))
    ids = [UUID(c.metadata['doc_uuid']) for c in docs]
    assert (len(ids) == len(docs))
    return ids, docs


def load_docs_from_site(doc_source_id: str, **kwargs) -> (List[UUID], List[Document]):
    # Set default values
    default_loader_params = {
        "max_depth": None,
        "use_async": True,
        "extractor": None,
        "exclude_dirs": None,
        "timeout": None,
        "prevent_outside": True
    }

    # Update default values with user-specified values
    loader_params = {**default_loader_params, **kwargs}

    loader = RecursiveUrlLoader(**loader_params)
    docs = loader.load()

    docs = Html2TextTransformer(ignore_images=True).transform_documents(docs)
    docs = MarkdownTextSplitter().transform_documents(docs)
    for index, doc in enumerate(docs):
        doc.metadata.setdefault("doc_source_id", doc_source_id)
        doc.metadata.setdefault("doc_source_type", "website")
        doc.metadata.setdefault("doc_url", doc.metadata["source"])
        if title := doc.metadata.pop('title', None):
            doc.metadata.setdefault("doc_title", title)
        if description := doc.metadata.pop('description', None):
            doc.metadata.setdefault("doc_description", description)
        if language := doc.metadata.pop('language', None):
            doc.metadata.setdefault("doc_language", language)
        doc.metadata.setdefault("doc_hash", calculate_md5_checksum(doc.page_content))
        doc.metadata.setdefault("doc_uuid",
                                generate_uuid(NAMESPACE_WEBSITE,
                                              doc.metadata['doc_source_type'],
                                              doc.metadata['doc_source_id'],
                                              doc.metadata['doc_url'],
                                              doc.metadata['doc_hash']))

    ids: List[UUID] = [UUID(doc.metadata['doc_uuid']) for doc in docs]

    assert (len(ids) == len(docs))
    return ids, docs
