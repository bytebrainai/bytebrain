import json
import os
import tempfile
from typing import Optional, Dict
from urllib.error import HTTPError

import googleapiclient.discovery
import requests
import yaml
from git import Repo
from langchain.document_loaders import GitLoader
from langchain.document_loaders import UnstructuredMarkdownLoader
from langchain.document_loaders import YoutubeLoader
from langchain.embeddings.openai import OpenAIEmbeddings
from langchain.schema import Document
from langchain.text_splitter import MarkdownTextSplitter
from langchain.vectorstores import Chroma


def update_vectorestore(texts: list[Document]):
    embeddings: OpenAIEmbeddings = OpenAIEmbeddings()
    Chroma.from_documents(texts, embeddings, persist_directory=os.environ["ZIOCHAT_CHROMA_DB_DIR"])


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


def index_markdown_docs(directory: str):
    documents: list[Document] = []

    for root, dirs, files in os.walk(directory):
        for filename in files:
            if filename.endswith('.md'):
                md_path = os.path.join(root, filename)
                print(md_path)

                docs: list[Document] = UnstructuredMarkdownLoader(md_path).load()

                metadata: dict[str, str] = extract_metadata(md_path)
                absolute_path = root.split("/zio/docs/")[1] + "/" + metadata["id"]

                # Add url to docs metadata
                for doc in docs:
                    doc.metadata.setdefault("url", f"https://zio.dev/{absolute_path}")
                    doc.metadata.setdefault("title", metadata["title"])

                documents.extend(docs)

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


def clone_repo(repo_url, depth=1) -> str:
    temp_folder: str = tempfile.mkdtemp()
    Repo.clone_from(repo_url, temp_folder, depth=depth)
    return temp_folder


def zio_ecosystem_clone_urls():
    file_path = "zio-ecosystem.json"
    try:
        with open(file_path, 'r') as file:
            return json.load(file)
    except FileNotFoundError:
        print(f"Error: File '{file_path}' not found.")


def index_zio_ecosystem_source_code():
    for prj in zio_ecosystem_clone_urls():
        print(prj)
        prj_dir = clone_repo(prj['clone_url'])
        index_source_code(prj_dir, prj['default_branch'])


def index_source_code(repo_path: str, branch: Optional[str]):
    loader = GitLoader(
        repo_path=repo_path,
        branch=branch,
        file_filter=lambda file_path: file_path.endswith(".scala")
    )
    docs = loader.load()
    update_vectorestore(docs)


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
            update_vectorestore(docs)
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
                repo_infos.append({
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
