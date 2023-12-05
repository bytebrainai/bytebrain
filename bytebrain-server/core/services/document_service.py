from enum import Enum

from pydantic.main import BaseModel
from structlog import getLogger

from config import load_config
from core.bots.discord.discord_utils import first_message_of_last_indexed_page
from core.docs.db.vectorstore_service import VectorStoreService
from core.docs.document_loader import *
from core.dao.metadata_dao import MetadataDao
from core.models.discord.DiscordMessage import DiscordMessage
from core.utils.github import zio_ecosystem_projects
from core.utils.utils import clone_repo
from core.utils.youtube import list_of_channel_videos

log = getLogger()


class JobStatus(Enum):
    Pending = "pending"
    Running = "running"
    Finished = "finished"


class AddWebsiteResource(BaseModel):
    name: str
    url: str


class AddGitRepoResource(BaseModel):
    name: str
    clone_url: str


class DocumentService:

    def __init__(self, weaviate_url, embeddings_dir, metadata_docs_db):
        self.metadata_service = MetadataDao(metadata_docs_db)
        self.vectorstore_service = VectorStoreService(url=weaviate_url,
                                                      embeddings_dir=embeddings_dir,
                                                      metadata_service=self.metadata_service)

    def index_zio_project_docs(self):
        ids, docs = load_zio_website_docs(os.environ["ZIOCHAT_DOCS_DIR"])
        self.vectorstore_service.upsert_docs(ids, docs)
        self.metadata_service.save_docs_metadata(docs)

    def index_zionomicon_book(self):
        ids, docs = load_zionomicon_docs(os.environ["ZIOCHAT_ZIONOMICON_DOCS_DIR"])
        self.vectorstore_service.upsert_docs(ids, docs)
        self.metadata_service.save_docs_metadata(docs)

    def index_zio_project_source_code(self):
        source_identifier = "github.com/zio/zio"
        ids, docs = load_source_code(os.environ["ZIOCHAT_ZIO_REPO_DIR"], "series/2.x", source_identifier)
        self.vectorstore_service.upsert_docs(ids, docs)
        self.metadata_service.save_docs_metadata(docs)

    def index_zio_ecosystem_source_code(self):
        for p in zio_ecosystem_projects():
            project_dir = clone_repo(p['clone_url'])
            log.info(f"Indexing {p['id']} source code")
            ids, docs = load_source_code(
                repo_path=project_dir,
                branch=None,
                source_id=p['id']
            )
            self.vectorstore_service.upsert_docs(ids, docs)
            log.info(f"Indexed {p['id']} source code")
            self.metadata_service.save_docs_metadata(docs)

    def index_youtube_video(self, video_id: str):
        try:
            ids, docs = load_youtube_docs_from_video_id(video_id)
            log.info(f"Loaded youtube docs for {video_id}!")
            # TODO: use upsert instead of index_docs
            self.vectorstore_service.index_docs(ids, docs)
            self.metadata_service.save_docs_metadata(docs)
            log.info(f"Updated youtube docs for {video_id}!")
        except Exception as e:
            log.error(f"An exception occurred while indexing video id {video_id}: {type(e).__name__}: {e}")

    def index_ziverge_youtube_channel(self):
        ziverge_channel_id = os.environ['YOUTUBE_CHANNEL_ID']
        video_ids = list_of_channel_videos(ziverge_channel_id)
        for video_id in video_ids:
            self.index_youtube_video(video_id)

    async def index_channel_history(
            self,
            channel_id: int,
            after: Optional[str],
            window_size: Optional[int],
            common_length: Optional[int],
            discord_cache_dir: str,
            bot: Bot):
        last: DiscordMessage | None = await first_message_of_last_indexed_page(channel_id, self.metadata_service, bot)
        ids, docs = await load_discord_channel_messages(channel_id, after, last, window_size, common_length,
                                                        discord_cache_dir, bot)

        self.vectorstore_service.index_docs(ids, docs)
        self.metadata_service.save_docs_metadata(documents=docs)
        return len(docs)


def index_all():
    config = load_config()
    indexer = DocumentService(config.weaviate_url, config.embeddings_dir, config.metadata_docs_db)

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
