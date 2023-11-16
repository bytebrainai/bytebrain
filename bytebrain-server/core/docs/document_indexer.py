import os
from datetime import datetime
from typing import Optional, List
from uuid import UUID

from discord.ext.commands import Bot
from langchain.schema import Document
from structlog import getLogger

from config import load_config
from core.bots.discord.discord_utils import first_message_of_last_indexed_page
from core.docs.db.vector_store import VectorStore
from core.docs.discord_loader import dump_channel_history
from core.docs.document_loader import generate_uuid
from core.docs.document_loader import load_source_code, load_zionomicon_docs, load_zio_website_docs, load_youtube_docs
from core.models.discord.ChannelHistory import ChannelHistory
from core.models.discord.DiscordMessage import DiscordMessage
from core.utils.github import zio_ecosystem_projects
from core.utils.utils import calculate_md5_checksum
from core.utils.utils import clone_repo
from core.utils.youtube import list_of_channel_videos
from stored_docs import StoredDocsService

NAMESPACE_DISCORD: UUID = UUID('e66dbce0-e817-4d27-bca5-72f1c4442b4a')

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

    async def index_channel_history(
            self,
            channel_id: int,
            after: Optional[str],
            window_size: Optional[int],
            common_length: Optional[int],
            discord_cache_dir: str,
            bot: Bot):
        last: DiscordMessage | None = await first_message_of_last_indexed_page(channel_id, self.stored_docs, bot)
        last_created_at = last.created_at if last is not None else None

        after_datetime = last_created_at if after is None else datetime.strptime(after, "%Y-%m-%d")

        channel_history: ChannelHistory = await dump_channel_history(channel_id, after_datetime, bot,
                                                                     discord_cache_dir)
        if last is not None:
            # Add the first message of last indexed page
            channel_history.history.insert(0, last)

        channel_id = channel_history.channel_id
        channel_name = channel_history.channel_name
        guild_id = channel_history.guild_id
        guild_name = channel_history.guild_name
        batched_messages = sliding_window_with_common_length(channel_history.history, window_size, common_length)
        pages = [(x[0], add_header(channel_name=channel_name, chat_history=x[1])) for x in
                 [generate_chat_transcript(i) for i in batched_messages]]
        documents = [
            Document(
                page_content=page[1],
                metadata={
                    "doc_source_id": "discord.com",
                    "doc_source_type": "chat",
                    "doc_id": f"discord.com/channels/{guild_id}/{channel_id}/{page[0]}",
                    "source": f"discord.com/channels/{guild_id}/{channel_id}/{page[0]}",
                    "doc_first_message_id": f"{page[0]}",
                    "doc_channel_id": str(channel_id),
                    "doc_channel_name": channel_name,
                    "doc_guild_id": str(guild_id),
                    "doc_guild_name": guild_name,
                    "doc_hash": calculate_md5_checksum(page[1]),
                    "doc_uuid":
                        str(
                            generate_uuid(
                                namespace=NAMESPACE_DISCORD,
                                doc_source_type="chat",
                                doc_source_id="discord.com",
                                doc_path=f"discord.com/channels/{guild_id}/{channel_id}/{page[0]}",
                                doc_hash=calculate_md5_checksum(page[1])
                            )
                        )
                }) for page in pages]

        log.info(f"Number of pages: {len(pages)}")

        ids = [doc.metadata['doc_uuid'] for doc in documents]
        assert (len(ids) == len(documents))
        self.vector_store.index_docs(ids, documents)
        self.stored_docs.save_docs_metadata(documents=documents)


def sliding_window_with_common_length(my_list, window_size, common_length):
    """
    Generate a list of sliding windows over the input list with a common overlap.

    Args:
        my_list (list): The input list to create sliding windows from.
        window_size (int): The size of each sliding window.
        common_length (int): The common length of overlap between adjacent windows.

    Returns:
        list: A list of sliding windows (lists) with the specified window size and overlap.

    Example:
        >>> input_list = [1, 2, 3, 4, 5, 6, 7, 8, 9]
        >>> window_size = 3
        >>> common_length = 1
        >>> sliding_window_with_common_length(input_list, window_size, common_length)
        [[1, 2, 3], [3, 4, 5], [5, 6, 7], [7, 8, 9]]
    """
    result = []
    i = 0

    while True:
        window = my_list[i:i + window_size]

        result.append(window)
        i += window_size - common_length

        if i + window_size > len(my_list):
            break

    return result


def add_header(channel_name: str, chat_history: str) -> str:
    return f"# Chat History for {channel_name}\n\n{chat_history}"


def generate_chat_transcript(messages: List[DiscordMessage]) -> (id, str):
    """
    Convert a list of Discord messages into a transcript with timestamps and user information.

    This function takes a list of Discord messages and creates a human-readable transcript.
    Each message is formatted with a timestamp, the user who sent it, and the message content.
    The resulting transcript is a string.

    Args:
        messages (List[DiscordMessage]): A list of DiscordMessage objects representing chat messages.

    Returns:
        Tuple[id, str]: A tuple containing the ID of the first message in the list and the transcript string.

    Example:
        >>> from core.models.discord.DiscordMessage import DiscordMessage
        >>> messages = [
        ...     DiscordMessage(1,"User1", datetime(2023, 9, 11, 10, 0, 0), "Hello!"),
        ...     DiscordMessage(2,"User2", datetime(2023, 9, 11, 10, 5, 0), "Hi there!"),
        ... ]
        >>> generate_chat_transcript(messages)
        (1, '2023-09-11 10:00:00 - User1 said: Hello!\n\n2023-09-11 10:05:00 - User2 said: Hi there!\n\n')
    """
    transcript = ""
    for m in messages:
        transcript = transcript + f"{m.created_at.strftime('%Y-%m-%d %H:%M:%S')} - {m.user} said: {m.content}\n\n"

    return messages[0].id, transcript


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
