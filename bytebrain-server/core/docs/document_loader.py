import os
import uuid
from datetime import datetime
from typing import Optional, List, Dict
from uuid import UUID

import yaml
from discord.ext.commands import Bot
from langchain.document_loaders import GitLoader
from langchain.document_loaders import UnstructuredMarkdownLoader
from langchain.document_loaders import YoutubeLoader
from langchain.document_loaders.recursive_url_loader import RecursiveUrlLoader
from langchain.document_transformers.html2text import Html2TextTransformer
from langchain.schema import Document
from langchain.text_splitter import Language
from langchain.text_splitter import MarkdownTextSplitter
from langchain.text_splitter import RecursiveCharacterTextSplitter

from core.docs.discord_loader import dump_channel_history
from core.models.discord.ChannelHistory import ChannelHistory
from core.models.discord.DiscordMessage import DiscordMessage
from core.utils.utils import calculate_md5_checksum

NAMESPACE_DOCUMENT = UUID('f924e0a9-69a7-11ee-aa84-6c02e09469ba')
NAMESPACE_WEBSITE = UUID('c88b857e-be16-4d80-9f45-b5c41fdd4a11')
NAMESPACE_YOUTUBE = UUID('1572e8de-29bf-464e-9253-656bd7c78938')
NAMESPACE_SOURCECODE = UUID('86adfa90-25d6-45bc-894c-8e1bb5c8ce76')
NAMESPACE_DISCORD: UUID = UUID('e66dbce0-e817-4d27-bca5-72f1c4442b4a')


def generate_uuid(namespace: UUID, doc_source_type, doc_source_id, doc_path, doc_hash) -> UUID:
    return uuid.uuid5(namespace, f"{doc_source_type}:{doc_source_id}:{doc_path}:{doc_hash}")


def load_zio_website_docs(directory: str) -> (List[UUID], List[Document]):
    def extract_metadata(md_file_path: str) -> Dict[str, str]:
        with open(md_file_path, 'r') as file:
            content = file.read()

        # Parse YAML front matter
        try:
            _, yaml_content, _ = content.split('---', 2)
            meta_data = yaml.safe_load(yaml_content)
            return {"id": meta_data.get('id'), "title": meta_data.get("title")}
        except ValueError:
            file_name = os.path.basename(md_file_path)
            return {"id": file_name, "title": file_name}

    documents: list[Document] = []
    for root, dirs, files in os.walk(directory):
        for filename in files:
            if filename.endswith('.md'):
                md_path = os.path.join(root, filename)
                docs: list[Document] = UnstructuredMarkdownLoader(md_path).load()
                docs = MarkdownTextSplitter().split_documents(docs)
                metadata: dict[str, str] = extract_metadata(md_path)
                for index, doc in enumerate(docs):
                    doc_id = root.split("/zio/website/docs/")[1] + '/' + metadata["id"]
                    doc.metadata["doc_path"] = doc.metadata["source"].split("/zio/website/docs/")[1]
                    doc.metadata["source"] = doc_id
                    doc.metadata.setdefault("doc_source_type", "documentation")
                    doc.metadata.setdefault("doc_source_id", "zio.dev")
                    doc.metadata.setdefault("doc_id", doc_id)
                    doc.metadata.setdefault("doc_title", metadata["title"])
                    doc.metadata.setdefault("doc_url", f"https://zio.dev/{doc.metadata['doc_id']}")
                    doc.metadata.setdefault("doc_hash", calculate_md5_checksum(doc.page_content))
                    doc.metadata.setdefault("doc_uuid",
                                            str(generate_uuid(
                                                NAMESPACE_DOCUMENT,
                                                doc.metadata['doc_source_type'],
                                                doc.metadata['doc_source_id'],
                                                doc.metadata['doc_path'],
                                                doc.metadata['doc_hash']
                                            )))
                documents.extend(docs)

    ids: List[UUID] = [UUID(doc.metadata['doc_uuid']) for doc in documents]

    assert (len(ids) == len(documents))
    return ids, documents


def load_source_code(
        repo_path: str,
        branch: Optional[str],
        source_id: str
) -> (List[UUID], List[Document]):
    loader = GitLoader(
        repo_path=repo_path,
        branch=branch,
        file_filter=lambda file_path: file_path.endswith(".scala")
    )
    docs = loader.load()
    splitter = RecursiveCharacterTextSplitter.from_language(language=Language.SCALA)
    docs = splitter.transform_documents(docs)

    for index, doc in enumerate(docs):
        doc.metadata.setdefault("doc_source_type", "source_code")
        doc.metadata.setdefault("doc_source_id", source_id)
        doc.metadata.setdefault("doc_hash", calculate_md5_checksum(doc.page_content))
        doc.metadata.setdefault("doc_path", doc.metadata.pop('file_path'))
        doc.metadata.setdefault("doc_uuid",
                                str(generate_uuid(NAMESPACE_SOURCECODE,
                                                  doc.metadata['doc_source_type'],
                                                  doc.metadata['doc_source_id'],
                                                  doc.metadata['doc_path'],
                                                  doc.metadata['doc_hash'])))

    ids: List[UUID] = [UUID(doc.metadata['doc_uuid']) for doc in docs]

    assert (len(ids) == len(docs))
    return ids, docs


def load_zionomicon_docs(directory: str) -> (List[UUID], List[Document]):
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
                docs: list[Document] = UnstructuredMarkdownLoader(md_path).load()
                docs = MarkdownTextSplitter().split_documents(docs)
                for index, doc in enumerate(docs):
                    doc.metadata.setdefault("doc_source_id", "zionomicon")
                    doc.metadata.setdefault("doc_source_type", "documentation")
                    doc.metadata.setdefault("doc_path", doc.metadata.pop('source').split("/zionomicon/docs/")[1])
                    doc.metadata.setdefault("doc_chapter", chapters[file_name])
                    doc.metadata.setdefault("doc_hash", calculate_md5_checksum(doc.page_content))
                    doc.metadata.setdefault(
                        "doc_uuid",
                        str(
                            generate_uuid(
                                NAMESPACE_DOCUMENT,
                                doc.metadata['doc_source_type'],
                                doc.metadata['doc_source_id'],
                                doc.metadata['doc_path'],
                                doc.metadata['doc_hash']
                            )
                        )
                    )

                documents.extend(docs)

    ids: List[UUID] = [UUID(doc.metadata['doc_uuid']) for doc in documents]

    assert (len(ids) == len(documents))
    return ids, documents


def load_youtube_docs(video_id: str) -> (List[UUID], List[Document]):
    video_url = f"https://www.youtube.com/watch?v={video_id}"
    loader = YoutubeLoader.from_youtube_url(video_url, add_video_info=True)
    docs: list[Document] = loader.load()
    text_splitter = RecursiveCharacterTextSplitter(chunk_size=2000, chunk_overlap=200)
    docs = text_splitter.split_documents(docs)
    for index, doc in enumerate(docs):
        doc.metadata.setdefault("doc_source_id", "youtube.com")
        doc.metadata.setdefault("doc_source_type", "subtitle")
        doc.metadata.setdefault("doc_url", video_url)
        doc.metadata.setdefault("doc_title", doc.metadata.pop('title'))
        doc.metadata.setdefault("doc_view_count", doc.metadata.pop('view_count'))
        doc.metadata.setdefault("doc_thumbnail_url", doc.metadata.pop('thumbnail_url'))
        doc.metadata.setdefault("doc_publish_date", doc.metadata.pop("publish_date"))
        doc.metadata.setdefault("doc_length", doc.metadata.pop("length"))
        doc.metadata.setdefault("doc_author", doc.metadata.pop("author"))
        doc.metadata.setdefault("doc_uuid", str(uuid.uuid5(NAMESPACE_YOUTUBE, video_url + doc.page_content)))
    ids = [UUID(c.metadata['doc_uuid']) for c in docs]
    assert (len(ids) == len(docs))
    return ids, docs


def load_docs_from_site(doc_source_id: str, **kwargs) -> (List[UUID], List[Document]):
    # Set default values
    default_loader_params = {
        "max_depth": None,
        "use_async": True,
        "extractor": None,
        "exclude_dirs": None,
        "timeout": None,
        "prevent_outside": True
    }

    # Update default values with user-specified values
    loader_params = {**default_loader_params, **kwargs}

    loader = RecursiveUrlLoader(**loader_params)
    docs = loader.load()

    docs = Html2TextTransformer(ignore_images=True).transform_documents(docs)
    docs = MarkdownTextSplitter().transform_documents(docs)
    for index, doc in enumerate(docs):
        doc.metadata.setdefault("doc_source_id", doc_source_id)
        doc.metadata.setdefault("doc_source_type", "website")
        doc.metadata.setdefault("doc_url", doc.metadata["source"])
        if title := doc.metadata.pop('title', None):
            doc.metadata.setdefault("doc_title", title)
        if description := doc.metadata.pop('description', None):
            doc.metadata.setdefault("doc_description", description)
        if language := doc.metadata.pop('language', None):
            doc.metadata.setdefault("doc_language", language)
        doc.metadata.setdefault("doc_hash", calculate_md5_checksum(doc.page_content))
        doc.metadata.setdefault("doc_uuid",
                                generate_uuid(NAMESPACE_WEBSITE,
                                              doc.metadata['doc_source_type'],
                                              doc.metadata['doc_source_id'],
                                              doc.metadata['doc_url'],
                                              doc.metadata['doc_hash']))

    ids: List[UUID] = [UUID(doc.metadata['doc_uuid']) for doc in docs]

    assert (len(ids) == len(docs))
    return ids, docs


async def load_discord_channel_messages(
        channel_id: int,
        after_date: Optional[str],
        from_msg: Optional[DiscordMessage],
        window_size: Optional[int],
        common_length: Optional[int],
        discord_cache_dir: str,
        bot: Bot):
    created_at = from_msg.created_at if from_msg is not None else None
    after = created_at if after_date is None else datetime.strptime(after_date, "%Y-%m-%d")
    channel_history: ChannelHistory = await dump_channel_history(channel_id, after, bot, discord_cache_dir)
    if from_msg is not None:
        # Add the first message of last indexed page
        channel_history.history.insert(0, from_msg)

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

    ids = [doc.metadata['doc_uuid'] for doc in documents]
    assert (len(ids) == len(documents))
    return ids, documents


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
