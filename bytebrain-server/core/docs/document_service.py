import sqlite3
import threading
import time
from enum import Enum

from pydantic.main import BaseModel
from structlog import getLogger

from config import load_config
from core.bots.discord.discord_utils import first_message_of_last_indexed_page
from core.docs.db.vectorstore_service import VectorStoreService
from core.docs.document_loader import *
from core.docs.resource_service import Resource, ResourceType
from core.docs.resource_service import ResourceService, ResourceState
from core.docs.metadata_service import DocumentMetadataService
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
    WEBSITE_ID_NAMESPACE = UUID('f6eea9d5-8b70-11ee-b7b1-6c02e09469ba')

    def __init__(self, weaviate_url, embeddings_dir, metadata_docs_db, resources_db, background_job_db):
        self.metadata_service = DocumentMetadataService(metadata_docs_db)
        self.resource_service = ResourceService(resources_db)
        self.vectorstore_service = VectorStoreService(url=weaviate_url,
                                                      embeddings_dir=embeddings_dir,
                                                      metadata_service=self.metadata_service)
        self.background_job_db = background_job_db
        self._create_daemon()

    def _create_daemon(self):
        background_thread = threading.Thread(target=self.run_pending_jobs, daemon=True)
        background_thread.start()

    def _create_table(self):
        conn = sqlite3.connect(self.background_job_db)
        cursor = conn.cursor()
        cursor.execute(f'''
            CREATE TABLE IF NOT EXISTS jobs (
                id TEXT PRIMARY KEY,
                status TEXT DEFAULT 'pending',
                payload json,
                job_type TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                finished_at TIMESTAMP
            )
        ''')
        conn.commit()
        conn.close()

    def submit_index_website(self, name: str, url: str) -> Optional[str]:
        resource_id = str(uuid.uuid5(self.WEBSITE_ID_NAMESPACE, name=url))
        if self.resource_service.get_by_id(resource_id):
            return None
        else:
            self.add_job(resource_id, AddWebsiteResource(name=name, url=url))
            return resource_id

    def add_job(self, job_id, job):
        conn = sqlite3.connect(self.background_job_db)
        cursor = conn.cursor()
        created_at = time.strftime('%Y-%m-%d %H:%M:%S')
        job_str = job.json()
        job_type = job.__class__.__name__
        cursor.execute('INSERT INTO jobs (id, payload, job_type, created_at) VALUES (?, ?, ?, ?)',
                       (job_id, job_str, job_type, created_at))
        conn.commit()
        conn.close()

    def get_website_resources(self) -> List[Resource]:
        return self.resource_service.get_resources_of_type(ResourceType.Website)

    def get_resource_status(self, resource_id) -> Optional[ResourceState]:
        return self.resource_service.get_resource_state(resource_id)

    def get_job_status(self, job_id):
        conn = sqlite3.connect(self.background_job_db)
        cursor = conn.cursor()
        cursor.execute('SELECT status FROM jobs WHERE id=?', (job_id,))
        result = cursor.fetchone()
        status = result[0] if result else None
        conn.close()
        return status

    def set_job_status(self, job_id, status):
        conn = sqlite3.connect(self.background_job_db)
        cursor = conn.cursor()

        cursor.execute('UPDATE jobs SET status=? WHERE id=?', (status, job_id))
        if status == 'running':
            cursor.execute('UPDATE jobs SET finished_at=? WHERE id=?', (time.strftime('%Y-%m-%d %H:%M:%S'), job_id))

        conn.commit()
        conn.close()

    def get_pending_jobs(self):
        conn = sqlite3.connect(self.background_job_db)
        cursor = conn.cursor()

        cursor.execute(f'SELECT id, payload, job_type FROM jobs WHERE status=?', ('pending',))
        pending_jobs = cursor.fetchall()
        print(pending_jobs)

        conn.close()
        return pending_jobs

    def run_pending_jobs(self):
        while True:
            conn = sqlite3.connect(self.background_job_db)
            cursor = conn.cursor()

            pending_jobs = self.get_pending_jobs()

            for job_id, job_payload, job_type in pending_jobs:
                cursor.execute('UPDATE jobs SET status=? WHERE id=?', ('running', job_id,))
                conn.commit()

                def parse_command(job_type: str, job_payload: str):
                    if job_type == AddWebsiteResource.__name__:
                        return AddWebsiteResource.parse_raw(job_payload)
                    elif job_type == AddGitRepoResource.__name__:
                        return AddGitRepoResource.parse_raw(job_payload)

                job = parse_command(job_type, job_payload)

                match job:
                    case AddGitRepoResource() as x:
                        log.info(f"added git repo: {x}")
                    case AddWebsiteResource(name=name, url=url):
                        self.index_website(resource_id=job_id, name=name, url=url)
                        cursor.execute('DELETE from jobs WHERE id=?', (job_id,))
                        conn.commit()
                        log.info(f"New website added {name}")

                self.set_job_status(job_id=job_id, status='finished')

            conn.close()
            time.sleep(2)

    def index_website(self, resource_id, name: str, url: str):
        resource = Resource(resource_id=resource_id, resource_name=name, resource_type=ResourceType.Website,
                            metadata={"url": url})
        self.resource_service.add_resource(resource)
        self.resource_service.set_state(resource_id, ResourceState.Loading)
        ids, docs = load_docs_from_site(doc_source_id=resource_id,
                                        doc_source_type=resource.resource_type.value,
                                        url=resource.metadata['url'])
        self.resource_service.set_state(resource_id, ResourceState.Indexing)
        self.vectorstore_service.index_docs(ids, docs)
        self.metadata_service.save_docs_metadata(docs)  # TODO: do not pass docs, instead pass metadata
        self.resource_service.set_state(resource_id, ResourceState.Finished)

    def delete_resource(self, resource_id: str):
        ids = self.metadata_service.get_docs_ids_by_source_id(resource_id)
        self.vectorstore_service.delete_docs(ids)
        self.metadata_service.delete_docs_by_resource_id(resource_id)
        self.resource_service.delete_resource(resource_id)

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
            ids, docs = load_youtube_docs(video_id)
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
    indexer = DocumentService(config.weaviate_url, config.embeddings_dir, config.metadata_docs_db, config.resources_db,
                              config.background_jobs_db)

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
