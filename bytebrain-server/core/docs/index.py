import json
import os

import requests
from structlog import getLogger

from config import load_config
from core.docs.document_loader import load_source_code, load_zionomicon_docs, load_zio_website_docs, load_youtube_docs
from core.docs.stored_docs import save_docs_metadata
from core.docs.weaviate_db import WeaviateDatabase
from core.utils.utils import clone_repo
from core.utils.youtube import list_of_channel_videos

config = load_config()
log = getLogger()
db = WeaviateDatabase(url=config.weaviate_url, embeddings_dir=config.embeddings_dir)


def index_zio_project_docs():
    ids, docs = load_zio_website_docs(os.environ["ZIOCHAT_DOCS_DIR"])
    db.upsert_docs(ids, docs)
    save_docs_metadata(docs)


def index_zionomicon_book():
    ids, docs = load_zionomicon_docs(os.environ["ZIOCHAT_ZIONOMICON_DOCS_DIR"])
    db.upsert_docs(ids, docs)
    save_docs_metadata(docs)


def index_zio_project_source_code():
    source_identifier = "github.com/zio/zio"
    ids, docs = load_source_code(os.environ["ZIOCHAT_ZIO_REPO_DIR"], "series/2.x", source_identifier)
    db.upsert_docs(ids, docs)
    save_docs_metadata(docs)


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
        log.info(f"Indexing {p['id']} source code")
        ids, docs = load_source_code(
            repo_path=project_dir,
            branch=None,
            source_id=p['id']
        )
        db.upsert_docs(ids, docs)
        log.info(f"Indexed {p['id']} source code")
        save_docs_metadata(docs)


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


def index_youtube_video(video_id: str):
    try:
        ids, docs = load_youtube_docs(video_id)
        log.info(f"Loaded youtube docs for {video_id}!")
        # TODO: use upsert instead of index_docs
        db.index_docs(ids, docs)
        save_docs_metadata(docs)
        log.info(f"Updated youtube docs for {video_id}!")
    except Exception as e:
        print(f"An exception occurred while indexing video id {video_id}: {type(e).__name__}: {e}")


def index_ziverge_youtube_channel():
    ziverge_channel_id = os.environ['YOUTUBE_CHANNEL_ID']
    video_ids = list_of_channel_videos(ziverge_channel_id)
    for video_id in video_ids:
        index_youtube_video(video_id)


def index_all():
    index_zio_project_docs()
    print("index_zio_project_docs finished")
    index_zionomicon_book()
    print("index_zionomicon_book finished")
    index_zio_project_source_code()
    print("index_zio_project_source_code finished")
    index_zio_ecosystem_source_code()
    print("index_zio_ecosystem_source_code finished")
    index_ziverge_youtube_channel()
    print("index_ziverge_youtube_channel finished")
