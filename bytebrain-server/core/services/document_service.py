# Copyright 2023-2024 ByteBrain AI
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

from enum import Enum

from structlog import getLogger

from config import load_config
from core.bots.discord.discord_utils import first_message_of_last_indexed_page
from core.dao.metadata_dao import MetadataDao
from core.docs.document_loader import *
from core.models.discord.DiscordMessage import DiscordMessage
from core.services.vectorstore_service import VectorStoreService
from core.utils.github import zio_ecosystem_projects
from core.utils.utils import clone_repo
from core.utils.youtube import list_of_channel_videos


class JobStatus(Enum):
    Pending = "pending"
    Running = "running"
    Finished = "finished"


class DocumentService:

    def __init__(self, vectorstore_service: VectorStoreService, metadata_dao: MetadataDao):
        self.metadata_dao = metadata_dao
        self.vectorstore_service = vectorstore_service
        self.log = getLogger(self.__class__.__name__)

    def index_zio_project_docs(self):
        ids, docs = load_zio_website_docs(os.environ["ZIOCHAT_DOCS_DIR"])

        doc_source_type = docs[0].metadata['doc_source_type']
        doc_source_id = docs[0].metadata['doc_source_id']
        old_metadata_list: List[Dict[any, any]] = self.metadata_dao.get_metadata_list(doc_source_type,
                                                                                      doc_source_id)
        self.vectorstore_service.upsert_docs(ids, docs, old_metadata_list)
        self.metadata_dao.save_docs_metadata(docs)

    def index_zionomicon_book(self):
        ids, docs = load_zionomicon_docs(os.environ["ZIOCHAT_ZIONOMICON_DOCS_DIR"])

        doc_source_type = docs[0].metadata['doc_source_type']
        doc_source_id = docs[0].metadata['doc_source_id']
        old_metadata_list: List[Dict[any, any]] = self.metadata_dao.get_metadata_list(doc_source_type,
                                                                                      doc_source_id)
        self.vectorstore_service.upsert_docs(ids, docs, old_metadata_list)
        self.metadata_dao.save_docs_metadata(docs)

    def index_zio_project_source_code(self):
        source_identifier = "github.com/zio/zio"
        ids, docs = load_source_code(os.environ["ZIOCHAT_ZIO_REPO_DIR"], "series/2.x", source_identifier)

        doc_source_type = docs[0].metadata['doc_source_type']
        doc_source_id = docs[0].metadata['doc_source_id']
        old_metadata_list: List[Dict[any, any]] = self.metadata_dao.get_metadata_list(doc_source_type,
                                                                                      doc_source_id)

        self.vectorstore_service.upsert_docs(ids, docs, old_metadata_list)
        self.metadata_dao.save_docs_metadata(docs)

    def index_zio_ecosystem_source_code(self):
        for p in zio_ecosystem_projects():
            project_dir = clone_repo(p['clone_url'])
            self.log.info(f"Indexing {p['id']} source code")
            ids, docs = load_source_code(
                repo_path=project_dir,
                branch=None,
                source_id=p['id']
            )

            doc_source_type = docs[0].metadata['doc_source_type']
            doc_source_id = docs[0].metadata['doc_source_id']
            old_metadata_list: List[Dict[any, any]] = self.metadata_dao.get_metadata_list(doc_source_type,
                                                                                          doc_source_id)
            self.vectorstore_service.upsert_docs(ids, docs, old_metadata_list)
            self.log.info(f"Indexed {p['id']} source code")
            self.metadata_dao.save_docs_metadata(docs)

    def index_youtube_video(self, video_id: str):
        try:
            ids, docs = load_youtube_docs_from_video_id(video_id)
            self.log.info(f"Loaded youtube docs for {video_id}!")
            # TODO: use upsert instead of index_docs
            self.vectorstore_service.index_docs(ids, docs)
            self.metadata_dao.save_docs_metadata(docs)
            self.log.info(f"Updated youtube docs for {video_id}!")
        except Exception as e:
            self.log.error(f"An exception occurred while indexing video id {video_id}: {type(e).__name__}: {e}")

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
        last: DiscordMessage | None = await first_message_of_last_indexed_page(channel_id, self.metadata_dao, bot)
        ids, docs = await load_discord_channel_messages(channel_id, after, last, window_size, common_length,
                                                        discord_cache_dir, bot)

        self.vectorstore_service.index_docs(ids, docs)
        self.metadata_dao.save_docs_metadata(documents=docs)
        return len(docs)


def index_all():
    config = load_config()
    vectorstore_service = VectorStoreService(config.weaviate_url, config.embeddings_dir)
    metadata_dao = MetadataDao(config.metadata_docs_db)
    indexer = DocumentService(vectorstore_service, metadata_dao)

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
