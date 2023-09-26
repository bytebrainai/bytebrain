import json
import os
import tempfile
from typing import Optional, Dict, List
from urllib.error import HTTPError

import googleapiclient.discovery
import requests
import yaml
from git import Repo
from langchain.document_loaders import UnstructuredMarkdownLoader
from langchain.document_loaders import YoutubeLoader
from langchain.embeddings.openai import OpenAIEmbeddings
from langchain.schema import Document
from langchain.text_splitter import MarkdownTextSplitter
from langchain.vectorstores import Chroma
from structlog import getLogger

from config import load_config
from core.db import upsert_docs
from core.document_loader import load_source_code
from core.utils import calculate_md5_checksum

config = load_config()

log = getLogger()


def update_db(texts: list[Document], ids: Optional[List[str]] = None):
    embeddings: OpenAIEmbeddings = OpenAIEmbeddings()
    Chroma.from_documents(texts, embeddings, ids=ids, persist_directory=config.db_dir)


def extract_metadata(md_file_path: str) -> Dict[str, str]:
    with open(md_file_path, 'r') as file:
        content = file.read()

    # Parse YAML front matter
    try:
        _, yaml_content, _ = content.split('---', 2)
        metadata = yaml.safe_load(yaml_content)
        return {"id": metadata.get('id'), "title": metadata.get("title")}
    except ValueError:
        file_name = os.path.basename(md_file_path)
        return {"id": file_name, "title": file_name}


def load_zio_website_docs(directory: str) -> (List[str], List[Document]):
    documents: list[Document] = []
    for root, dirs, files in os.walk(directory):
        for filename in files:
            if filename.endswith('.md'):
                md_path = os.path.join(root, filename)
                log.info(md_path)
                docs: list[Document] = UnstructuredMarkdownLoader(md_path).load()
                metadata: dict[str, str] = extract_metadata(md_path)
                for index, doc in enumerate(docs):
                    doc.metadata["doc_path"] = doc.metadata.pop("source").split("/zio/website/docs/")[1]
                    doc.metadata.setdefault("doc_source", "zio.dev")
                    doc.metadata.setdefault("doc_id", root.split("/zio/website/docs/")[1] + '/' + metadata["id"])
                    doc.metadata.setdefault("doc_title", metadata["title"])
                documents.extend(docs)

    log.info(f"Number of original docs: {len(documents)}")
    fragmented_docs = MarkdownTextSplitter().split_documents(documents)
    log.info(f"Number of docs after split phase: {len(fragmented_docs)}")

    ids: List[str] = []
    for d in fragmented_docs:
        hash = calculate_md5_checksum(d.page_content)
        doc_type = "documentation"
        source_identifier = "github.com/zio/zio"
        id = f"{doc_type}:{source_identifier}:{d.metadata['doc_path']}:{hash}"
        ids.append(id)

    assert (len(ids) == len(fragmented_docs))
    return ids, fragmented_docs


def index_zio_project_docs():
    ids, docs = load_zio_website_docs(os.environ["ZIOCHAT_DOCS_DIR"])
    upsert_docs(ids, docs, config.db_dir)


def load_zionomicon_docs(directory: str) -> (List[str], List[Document]):
    documents: list[Document] = []

    chapters = {
        "05-integrating-with-zio.md": "Essentials: Integrating With ZIO",
        "22-advanced-stm.md": "Software Transactional Memory: Advanced STM",
        "34-assertions.md": "Testing: Assertions",
        "21-stm-data-structures.md": "Software Transaction Memory: STM Data Structures",
        "07-concurrency-operators.md": "Parallelism And Concurrency: Concurrency Operators",
        "24-debugging.md": "Advanced Error Management: Debugging",
        "33-basic-testing.md": "Testing: Basic Testing",
        "40-reporting.md": "Testing: Reporting",
        "02-first-steps-with-zio.md": "Essentials: First Steps With ZIO",
        "48-applications-spark.md": "Applications: Spark",
        "13-hub-broadcasting.md": "Concurrent Structures: Hub - Broadcasting",
        "49-appendix-a-the-scala-type-system.md": "Appendix: The Scala Type System",
        "30-combining-streams.md": "Streaming: Combining Streams",
        "03-testing-zio-programs.md": "Essentials: Testing ZIO Programs",
        "29-transforming-streams.md": "Streaming: Transforming Streams",
        "26-first-steps-with-zstream.md": "Streaming: First Steps With ZStream",
        "39-test-annotations.md": "Testing: Test Annotations",
        "38-property-based-testing.md": "Testing: Property Based Testing",
        "32-sinks.md": "Streaming: Sinks",
        "10-references-functional-descriptions-of-mutable-state.md": "Concurrent Structures: Ref - Shared State",
        "11-promise-work-synchronization.md": "Concurrent Structures: Promise - Work Synchronization",
        "41-applications-parallel-web-crawler.md": "Applications: Parallel Web Crawler",
        "08-fiber-supervision-in-depth.md": "Parallelism And Concurrency: Fiber Supervision In Depth",
        "06-the-fiber-model.md": "Parallelism And Concurrency: The Fiber Model",
        "25-best-practices.md": "Advanced Error Management: Best Practices",
        "47-applications-graphql-api.md": "Applications: GraphQL API",
        "14-semaphore-work-limiting.md": "Concurrent Structures: Semaphore - Work Limiting",
        "31-pipelines.md": "Streaming: Pipelines",
        "45-applications-grpc-microservices.md": "Applications: gRPC Microservices",
        "44-applications-kafka-stream-processor.md": "Applications: Kafka Stream Processor",
        "28-channels.md": "Channels: Unifying Streams, Sinks, and Pipelines",
        "20-stm-composing-atomicity.md": "Software Transactional Memory: Composing Atomicity",
        "36-test-aspects.md": "Testing: Test Aspects",
        "16-scope-composable-resources.md": "Resource Handling: Scope - Composable Resources",
        "42-applications-file-processing.md": "Applications: File Processing",
        "46-applications-rest-api.md": "Applications: REST API",
        "43-applications-command-line-interface.md": "Applications: Command Line Interface",
        "27-next-steps-with-zstream.md": "Streaming: Next Steps With ZStream",
        "01-foreword.md": "Foreword by John A. De Goes",
        "50-appendix-b-mastering-variance.md": "Appendix: Mastering Variance",
        "15-acquire-release-safe-resource-handling-for-asynchronous-code.md": "Resource Handling: Acquire Release - Safe Resource Handling",
        "23-retries.md": "Advanced Error Management: Retries",
        "12-queue-work-distribution.md": "Concurrent Structures: Queue - Work Distribution",
        "35-the-test-environment.md": "Testing: The Test Environment",
        "04-the-zio-error-model.md": "Essentials: The ZIO Error Model",
        "09-interruption-in-depth.md": "Parallelism And Concurrency: Interruption In Depth",
        "19-advanced-dependency-injection.md": "Dependency Injection: Advanced Dependency Injection",
        "18-dependency-injection-essentials.md": "Dependency Injection: Essentials",
        "37-using-resources-in-tests.md": "Testing: Using Resources In Tests",
        "17-advanced-scopes.md": "Resource Handling: Advanced Scopes",
    }

    for root, dirs, files in os.walk(directory):
        for file_name in files:
            if file_name.endswith('.md'):
                md_path = os.path.join(root, file_name)
                log.info(md_path)
                docs: list[Document] = UnstructuredMarkdownLoader(md_path).load()
                for index, doc in enumerate(docs):
                    doc.metadata.setdefault("doc_source", "zionomicon")
                    doc.metadata.setdefault("doc_path", doc.metadata.pop('source').split("/zionomicon/docs/")[1])
                    doc.metadata.setdefault("doc_chapter", chapters[file_name])
                documents.extend(docs)

    fragmented_docs = MarkdownTextSplitter().split_documents(documents)

    ids: List[str] = []
    for d in fragmented_docs:
        hash = calculate_md5_checksum(d.page_content)
        doc_type = "documentation"
        source_identifier = "github.com/zivergetech/zionomicon"
        id = f"{doc_type}:{source_identifier}:{d.metadata['doc_path']}:{hash}"
        ids.append(id)

    assert (len(ids) == len(fragmented_docs))
    return ids, fragmented_docs


def index_zionomicon_book():
    ids, docs = load_zionomicon_docs(os.environ["ZIOCHAT_ZIONOMICON_DOCS_DIR"])
    upsert_docs(ids, docs, config.db_dir)


def index_zio_project_source_code():
    source_identifier = "github.com/zio/zio"
    ids, docs = load_source_code(os.environ["ZIOCHAT_ZIO_REPO_DIR"], "series/2.x", source_identifier)
    upsert_docs(ids, docs, config.db_dir)


def clone_repo(repo_url, depth=1) -> str:
    temp_folder: str = tempfile.mkdtemp()
    Repo.clone_from(repo_url, temp_folder, depth=depth)
    return temp_folder


def zio_ecosystem_projects():
    file_path = "index/zio-ecosystem.json"
    try:
        with open(file_path, 'r') as file:
            return json.load(file)
    except FileNotFoundError:
        print(f"Error: File '{file_path}' not found.")


def index_zio_ecosystem_source_code():
    for p in zio_ecosystem_projects():
        project_dir = clone_repo(p['clone_url'])
        ids, docs = load_source_code(
            repo_path=project_dir,
            branch=p['default_branch'],
            source_identifier=p['id']
        )
        upsert_docs(ids, docs, config.db_dir)


def list_of_channel_videos():
    youtube = googleapiclient.discovery.build(
        'youtube',
        'v3',
        developerKey=os.environ["GOOGLE_API_KEY"]
    )

    # Check if cached data exists
    cache_file = 'video_ids_cache.json'
    if os.path.exists(cache_file):
        with open(cache_file, 'r') as file:
            cached_data = json.load(file)
        if os.environ['YOUTUBE_CHANNEL_ID'] in cached_data:
            return cached_data[os.environ['YOUTUBE_CHANNEL_ID']]

    video_ids = []
    page_token = None

    try:
        while True:
            response = youtube.search().list(
                part='id',
                channelId=os.environ['YOUTUBE_CHANNEL_ID'],
                maxResults=50,
                pageToken=page_token
            ).execute()

            for item in response['items']:
                if item['id']['kind'] == 'youtube#video':
                    video_ids.append(item['id']['videoId'])

            if 'nextPageToken' in response:
                page_token = response['nextPageToken']
            else:
                break

    except HTTPError:
        print(f'An HTTP error occurred')

    if os.path.exists(cache_file):
        with open(cache_file, 'r') as file:
            cached_data = json.load(file)
    else:
        cached_data = {}

    cached_data[os.environ['YOUTUBE_CHANNEL_ID']] = video_ids

    with open(cache_file, 'w') as file:
        json.dump(cached_data, file)

    return video_ids


def index_youtube_video():
    video_ids = list_of_channel_videos()
    for video_id in video_ids:
        try:
            print(video_id)
            loader = YoutubeLoader.from_youtube_url(
                "https://www.youtube.com/watch?v=" + video_id,
                # TODO: For better user experience it is better to include metadata
                add_video_info=False
            )
            docs: list[Document] = loader.load()
            # TODO: All the transcript is loaded into one document
            #       We need to split that into multiple smaller documents
            update_db(docs)
        except Exception:
            print("Failed to index video id: " + video_id)


def get_zio_ecosystem_repo_info():
    base_url = f"https://api.github.com/orgs/zio/repos"
    headers = {"Accept": "application/vnd.github.v3+json"}  # Set headers to use GitHub API v3

    repo_infos = []
    page = 1
    per_page = 100  # Number of repositories per page

    while True:
        params = {"page": page, "per_page": per_page}
        response = requests.get(base_url, headers=headers, params=params)

        if response.status_code == 200:
            repos = response.json()
            if len(repos) == 0:
                break  # No more repositories to retrieve

            for repo in repos:
                clone_url = repo["clone_url"]
                default_branch = repo["default_branch"]
                print(clone_url)
                repo_infos.append({  # TODO: Add id field for each entry
                    "clone_url": clone_url,
                    "default_branch": default_branch
                })

            page += 1
        else:
            print(f"Failed to retrieve repositories. Error: {response.status_code} - {response.text}")
            return []

    with open("zio-ecosystem.json", 'w') as file:
        json.dump(repo_infos, file)


def index_all():
    index_zio_project_docs()
    index_zionomicon_book()
    index_zio_project_source_code()
    index_zio_ecosystem_source_code()

