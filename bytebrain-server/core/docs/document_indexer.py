import os

from structlog import getLogger

from config import load_config
from core.docs.db.vector_store import VectorStore
from core.docs.document_loader import load_source_code, load_zionomicon_docs, load_zio_website_docs, load_youtube_docs
from core.utils.github import zio_ecosystem_projects
from core.utils.utils import clone_repo
from core.utils.youtube import list_of_channel_videos
from stored_docs import StoredDocsService

log = getLogger()


class DocumentIndexer:
    def __init__(self, weaviate_url, embeddings_dir, stored_docs_db):
        self.stored_docs = StoredDocsService(stored_docs_db)
        self.vector_store = VectorStore(url=weaviate_url, embeddings_dir=embeddings_dir, stored_docs=stored_docs_db)

    def index_zio_project_docs(self):
        ids, docs = load_zio_website_docs(os.environ["ZIOCHAT_DOCS_DIR"])
        self.vector_store.upsert_docs(ids, docs)
        self.stored_docs.save_docs_metadata(docs)

    def index_zionomicon_book(self):
        ids, docs = load_zionomicon_docs(os.environ["ZIOCHAT_ZIONOMICON_DOCS_DIR"])
        self.vector_store.upsert_docs(ids, docs)
        self.stored_docs.save_docs_metadata(docs)

    def index_zio_project_source_code(self):
        source_identifier = "github.com/zio/zio"
        ids, docs = load_source_code(os.environ["ZIOCHAT_ZIO_REPO_DIR"], "series/2.x", source_identifier)
        self.vector_store.upsert_docs(ids, docs)
        self.stored_docs.save_docs_metadata(docs)

    def index_zio_ecosystem_source_code(self):
        for p in zio_ecosystem_projects():
            project_dir = clone_repo(p['clone_url'])
            log.info(f"Indexing {p['id']} source code")
            ids, docs = load_source_code(
                repo_path=project_dir,
                branch=None,
                source_id=p['id']
            )
            self.vector_store.upsert_docs(ids, docs)
            log.info(f"Indexed {p['id']} source code")
            self.stored_docs.save_docs_metadata(docs)

    def index_youtube_video(self, video_id: str):
        try:
            ids, docs = load_youtube_docs(video_id)
            log.info(f"Loaded youtube docs for {video_id}!")
            # TODO: use upsert instead of index_docs
            self.vector_store.index_docs(ids, docs)
            self.stored_docs.save_docs_metadata(docs)
            log.info(f"Updated youtube docs for {video_id}!")
        except Exception as e:
            print(f"An exception occurred while indexing video id {video_id}: {type(e).__name__}: {e}")

    def index_ziverge_youtube_channel(self):
        ziverge_channel_id = os.environ['YOUTUBE_CHANNEL_ID']
        video_ids = list_of_channel_videos(ziverge_channel_id)
        for video_id in video_ids:
            self.index_youtube_video(video_id)


def index_all():
    config = load_config()
    indexer = DocumentIndexer(config.weaviate_url, config.embeddings_dir, config.stored_docs_db)

    indexer.index_zio_project_docs()
    print("index_zio_project_docs finished")
    indexer.index_zionomicon_book()
    print("index_zionomicon_book finished")
    indexer.index_zio_project_source_code()
    print("index_zio_project_source_code finished")
    indexer.index_zio_ecosystem_source_code()
    print("index_zio_ecosystem_source_code finished")
    indexer.index_ziverge_youtube_channel()
    print("index_ziverge_youtube_channel finished")
