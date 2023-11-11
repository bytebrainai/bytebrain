import json
import os
import tempfile
from urllib.error import HTTPError

import googleapiclient.discovery
import requests
from git import Repo
from structlog import getLogger

from config import load_config
from core.docs.document_loader import load_source_code, load_zionomicon_docs, load_zio_website_docs, load_youtube_docs
from core.docs.weaviate_db import WeaviateDatabase
from core.docs.stored_docs import save_docs_metadata

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
        log.info(f"Indexing {p['id']} source code")
        ids, docs = load_source_code(
            repo_path=project_dir,
            branch=None,
            source_id=p['id']
        )
        db.upsert_docs(ids, docs)
        log.info(f"Indexed {p['id']} source code")
        save_docs_metadata(docs)


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


def list_of_channel_videos(channel_id: str):
    youtube = googleapiclient.discovery.build(
        'youtube',
        'v3',
        developerKey=os.environ["GOOGLE_API_KEY"]
    )

    cache_file = 'video_ids_cache.json'
    if os.path.exists(cache_file):
        with open(cache_file, 'r') as file:
            cached_data = json.load(file)
        if channel_id in cached_data:
            return cached_data[channel_id]

    video_ids = []
    page_token = None

    try:
        while True:
            response = youtube.search().list(
                part='id',
                channelId=channel_id,
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

    cached_data[channel_id] = video_ids

    with open(cache_file, 'w') as file:
        json.dump(cached_data, file)

    return video_ids


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
