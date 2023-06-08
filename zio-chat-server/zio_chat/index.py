import os
from urllib.error import HTTPError
import json
import googleapiclient.discovery

from langchain.embeddings.openai import OpenAIEmbeddings
from langchain.schema import Document
from langchain.text_splitter import MarkdownTextSplitter
from langchain.vectorstores import Chroma
from langchain.document_loaders import GitLoader
from langchain.document_loaders import YoutubeLoader


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


def index_all():
    index_zio_project_docs()
    index_zionomicon_book()
    index_zio_project_source_code()
