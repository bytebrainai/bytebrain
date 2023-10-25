import asyncio
import datetime
import json
import os
import re
from datetime import datetime
from datetime import timedelta
from typing import Any, Tuple
from typing import List, Optional
from datetime import timezone
from uuid import UUID

import chat_exporter
import discord
from discord.ext import commands, tasks
from discord.ext.commands import Bot
from discord.guild import Guild
from discord.message import Message
from langchain.schema import Document
from structlog import getLogger

import index.index as index
from config import load_config
from core.ChannelHistory import ChannelHistory
from core.DiscordMessage import DiscordMessage
from core.chatbot_v2 import make_question_answering_chatbot
from core.document_loader import generate_uuid
from core.stored_docs import fetch_last_item_in_discord_channel, create_connection
from core.stored_docs import save_docs_metadata
from core.utils import annotate_history_with_turns_v2
from core.utils import calculate_md5_checksum
from core.utils import split_string_preserve_suprimum_number_of_lines
from core.weaviate_db import WeaviateDatabase

config = load_config()
vector_store = WeaviateDatabase(url=config.weaviate_url, embeddings_dir=config.embeddings_dir)

intents = discord.Intents.default()
intents.message_content = True
intents.members = True

bot: Bot = commands.Bot(command_prefix="!", intents=intents)
log = getLogger()

NAMESPACE_DISCORD: UUID = UUID('e66dbce0-e817-4d27-bca5-72f1c4442b4a')


@bot.event
async def on_ready():
    log.info("Hello! I'm Chat Bot and ready to receive commands!")


@bot.command()
@commands.has_permissions(administrator=True)
async def export(ctx: commands.Context):
    transcript = await chat_exporter.export(
        ctx.channel,
        limit=None,
        bot=bot,
    )

    if transcript is None:
        return

    file_path = f"transcript-{ctx.channel.name}.json"

    # Open the file and write data
    with open(file_path, "w", encoding="utf-8") as file:
        file.write(transcript)

    log.info(f"Transcript has been written to '{file_path}'.")


@bot.command()
@commands.has_permissions(administrator=True)
async def dump_channel(ctx: commands.Context, channel_id: int, after: Optional[str] = None):
    channel_name = bot.get_channel(channel_id).name
    after_datetime = None if after is None else datetime.strptime(after, "%Y-%m-%d")

    response_msg = f"Started to dump channel {channel_name}" if after is None \
        else f"Started to dump channel {channel_name} after {after}"
    log.info(response_msg)
    await ctx.send(response_msg)

    await fetch_channel_history(channel_id, after_datetime)

    response_msg = f"Channel {channel_id} was dumped!"
    log.info(response_msg)
    await ctx.send(response_msg)


@bot.command()
@commands.has_permissions(administrator=True)
async def index_zio_docs(ctx):
    await send_and_log(ctx, "Started indexing ZIO docs on zio.dev")
    index.index_zio_project_docs()
    await send_and_log(ctx, "Finished indexing zio project docs!")


@bot.command()
@commands.has_permissions(administrator=True)
async def index_ziverge_youtube_channel(ctx):
    await send_and_log(ctx, "Started indexing Ziverge's Youtube Channel!")
    index.index_ziverge_youtube_channel()
    await send_and_log(ctx, "Finished indexing Ziverge's Youtube Channel!")


@bot.command()
@commands.has_permissions(administrator=True)
async def index_zionomicon(ctx):
    await send_and_log(ctx, "Started indexing Zionomicon book")
    index.index_zionomicon_book()
    await send_and_log(ctx, "Finished indexing zionomicon book!")


@bot.command()
@commands.has_permissions(administrator=True)
async def index_zio_source(ctx):
    await send_and_log(ctx, "Started indexing ZIO's source code")
    index.index_zio_project_source_code()
    await send_and_log(ctx, "Finished indexing zio's source codes!")


@bot.command()
@commands.has_permissions(administrator=True)
async def index_zio_ecosystem_source(ctx):
    await send_and_log(ctx, "Started indexing ZIO's")
    index.index_zio_ecosystem_source_code()
    await send_and_log(ctx, "Started indexing ZIO's")


@bot.command()
@commands.has_permissions(administrator=True)
async def server_info(ctx):
    info = _server_info()
    log.info(info)
    await send_message_in_chunks(ctx, info)


@bot.command("index_channel")
@commands.has_permissions(administrator=True)
async def index_channel(ctx, channel_id: int,
                        after: Optional[str] = None,
                        window_size: Optional[int] = config.discord.messages_window_size,
                        common_length: Optional[int] = config.discord.messages_common_length):
    channel = bot.get_channel(channel_id)
    channel_name = channel.name
    after_datetime = None if after is None else datetime.strptime(after, "%Y-%m-%d")

    await send_and_log(
        ctx,
        f"started indexing channel {channel_name}" if after is None
        else f"started indexing channel {channel_name} after {after}"
    )

    channel_history: ChannelHistory = await fetch_channel_history(channel_id, after_datetime)
    await index_channel_history(
        channel_history=channel_history,
        window_size=window_size,
        common_length=common_length
    )

    await send_and_log(
        ctx,
        f"Index process for {channel_name} done!"
    )


def is_private_message(message):
    return isinstance(message.channel, discord.DMChannel)


@bot.event
async def on_message(message):
    ctx = await bot.get_context(message)
    if message.author == bot.user:
        return

    # Do not respond to messages containing @here and @everyone
    if message.mention_everyone:
        return

    if bot.user.mentioned_in(message) or is_private_message(message):
        async with message.channel.typing():
            log.info(f"received message from {message.channel} channel")
            qa = make_question_answering_chatbot(
                websocket=None,
                vector_store=vector_store.weaviate,
                prompt_template=config.discord.prompt
            )

            chat_history = ["FULL CHAT HISTORY:"] + annotate_history_with_turns_v2(
                await fetch_message_thread_v2(ctx, message))

            result: dict[str, Any] = await qa.acall(
                {
                    "question": remove_discord_mention(message.content),
                    "project_name": config.project_name,
                    "chat_history": chat_history
                },
                return_only_outputs=True
            )
            log.info("response for discord is ready", response={
                "question": message.content,
                "result": result['answer']
            })

            source_documents: list[dict[str, Any]] = []
            for doc_source in result["source_documents"]:
                metadata = doc_source.metadata
                if "doc_source" in metadata:
                    source_doc = metadata["doc_source"]
                    if source_doc == "zio.dev":
                        entry = {
                            "title": metadata["doc_title"],
                            "url": f"{metadata['doc_id']}",
                            "page_content": doc_source.page_content
                        }
                        log.info(entry)
                        source_documents.append(entry)
                    elif source_doc == "discord":
                        metadata = doc_source.metadata
                        entry = {
                            "message_id": metadata["message_id"],
                            "channel_id": metadata["channel_id"],
                            "channel_name": metadata["channel_name"],
                            "guild_id": metadata["guild_id"],
                            "guild_name": metadata["guild_name"],
                            "page_content": doc_source.page_content
                        }
                        log.info(entry)
                        source_documents.append(entry)
                    else:
                        log.warning(f"source_doc {source_doc} was not supported")
                else:
                    log.warning("source_doc is not exist in metadata")

            chunks = split_string_preserve_suprimum_number_of_lines(result['answer'], chunk_size=2000)
            await message.reply(chunks[0])
            for chunk in chunks[1:]:
                await ctx.send(chunk)
    else:
        await bot.process_commands(message)


@bot.command()
@commands.has_permissions(administrator=True)
async def update_discord_channel(ctx, channel_id: int):
    last: DiscordMessage | None = await first_message_of_last_indexed_page(channel_id=channel_id)
    channel_name = bot.get_channel(channel_id).name
    last_created_at = last.created_at if last is not None else None
    await send_and_log(ctx, f"Started updating {channel_name} channel.")
    try:
        channel_history: ChannelHistory = await fetch_channel_history(channel_id, last_created_at)
        if last is not None:
            # Add the first messaged of last indexed page
            channel_history.history.insert(0, last)
        await index_channel_history(
            channel_history,
            config.discord.messages_window_size,
            config.discord.messages_common_length
        )
    except Exception as e:
        log.error(f"Exception occurred during updating {channel_name} channel! + {str(e)}")

    await send_and_log(ctx, f"The {channel_name} channel updated!")


@bot.command()
async def update_discord_channels(ctx, guild_id: int):
    guild_name = bot.get_guild(guild_id).name
    await ctx.send(f"Started updating channels inside {guild_name} guild!")
    update_discord_channels_periodically.start(ctx, guild_id)


@tasks.loop(hours=config.discord.update_interval)
async def update_discord_channels_periodically(ctx, guild_id: int):
    for ch in bot.get_guild(guild_id).channels:
        await update_discord_channel(ctx, ch.id)
    await send_and_log(ctx, "All channels were updated!")


async def first_message_of_last_indexed_page(channel_id: int) -> Optional[DiscordMessage]:
    """
    Retrieves the first message of the last indexed page associated with a given channel from the database.
    """
    with create_connection(config.stored_docs_db) as connection:
        last_item = fetch_last_item_in_discord_channel(connection,
                                                       doc_source_id="discord",
                                                       channel_id=str(channel_id))
    metadata = json.loads(last_item[3])
    msg_id = int(metadata['message_id'])
    guild_id = int(metadata['guild_id'])

    discord_msg = await bot.get_guild(guild_id).get_channel(channel_id).fetch_message(msg_id)
    return DiscordMessage(
        discord_msg.id,
        discord_msg.author.name,
        discord_msg.created_at,
        discord_msg.content
    )


def get_guild_by_channel(channel_id: int) -> Optional[Guild]:
    """
    Retrieves the guild (server) that contains a Discord channel with the specified channel ID.

    Note:
        This function iterates through the available guilds the bot is a member of and checks if any of them contain a
        channel with the specified ID. If a matching channel is found, it returns the associated Guild (server) object.
        If no match is found, it returns None.
    """
    for guild in bot.guilds:
        channel = guild.get_channel(channel_id)
        if channel:
            return guild
    return None


async def download_channel_history(channel_id: int, after: Optional[datetime] = None) -> List[DiscordMessage]:
    """
    Downloads and retrieves the channel history for a Discord channel, starting from a specified datetime if provided.
    """
    messages = [
        DiscordMessage(
            m.id,
            m.author.name,
            m.created_at,
            m.content
        ) async for m in
        bot.get_channel(channel_id).history(limit=None, oldest_first=True, after=after)
    ]

    return messages


def dump_channel_history(channel_history: ChannelHistory, file_name: str):
    cache_dir = "./db/discord-cache"
    with open(file_name, 'w') as file:
        file.write(channel_history.to_json())

    # Check if the directory exists, and create it if it doesn't
    if not os.path.exists(cache_dir):
        os.makedirs(cache_dir)

    with open(os.path.join(cache_dir, file_name), 'w') as file:
        file.write(channel_history.to_json())


async def send_and_log(ctx, message: str):
    await ctx.send(message)
    log.info(message)


def filter_messages_from(history: List[DiscordMessage], after: Optional[datetime]) -> List[DiscordMessage]:
    """
    Filter a list of Discord messages to include only those created from a specified timestamp.

    This function takes a list of Discord messages and filters them to include only messages
    created from the specified timestamp, if provided. If no timestamp is given (after is None),
    all messages in the input list are included in the result.

    Note:
        - Messages with timestamps greater than or equal to the provided 'after' timestamp
          are included in the result.
    """
    filtered_messages = []
    if after is not None:
        for message in history:
            if message.created_at >= after.replace(tzinfo=timezone.utc):
                filtered_messages.append(message)
    else:
        filtered_messages = history
    return filtered_messages


def read_from_cache(file_path: str, after: Optional[datetime]) -> ChannelHistory:
    with open(file_path, 'r') as file:
        messages: ChannelHistory = ChannelHistory.from_json(file.read())
        messages.history = filter_messages_from(messages.history, after)
    return messages


async def fetch_channel_history(channel_id: int, after: Optional[datetime]) -> ChannelHistory:
    """
    This function first checks if there is a cached file for the channel's history that is not older than two weeks.
    If a valid cache is found, it reads the history from the cache. If no cache is found or if it's older than two
    weeks, it downloads the channel history from the server, combines user messages, and caches the new history.
    """
    channel_name = bot.get_channel(channel_id).name
    guild = get_guild_by_channel(channel_id)
    file_path = f"channel_{channel_name}_{channel_id}.json"
    two_week_ago = datetime.now() - timedelta(days=14)

    def is_older_than_two_week(file: str) -> bool:
        return os.path.getmtime(file) < two_week_ago.timestamp()

    if os.path.exists(file_path) and not is_older_than_two_week(file_path):
        log.info(f"Cached data found for channel {channel_name}")
        channel_history = read_from_cache(file_path, after)
    else:
        if os.path.exists(file_path):
            os.remove(file_path)
            log.info("Removed the old cached file!")

        log.info(f"Started to download channel history for {channel_name}")
        history = await asyncio.wait_for(download_channel_history(channel_id, after=after), 360)
        combined_messages: List[DiscordMessage] = combine_user_messages(history, time_threshold=4)
        channel_history = ChannelHistory(guild_id=guild.id, guild_name=guild.name, channel_id=channel_id,
                                         channel_name=channel_name, history=combined_messages)
        dump_channel_history(channel_history, file_path)

    return channel_history


async def index_channel_history(
        channel_history: ChannelHistory,
        window_size: Optional[int],
        common_length: Optional[int]):
    """
    Indexes the channel history into the db by processing and structuring the messages.

    Args:
        channel_history (ChannelHistory): The channel history to be indexed.
        window_size (Optional[int]): The size of the sliding window used to batch messages.
        common_length (Optional[int]): The length at which common parts of messages are truncated.

    Notes:
        This function processes the given channel history, divides it into batches, adds metadata, and indexes it
        for search purposes. It generates chat transcripts and creates documents with appropriate metadata to
        be indexed in a search database.
    """
    channel_id = channel_history.channel_id
    channel_name = bot.get_channel(channel_id).name
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
    vector_store.index_docs(ids, documents)
    save_docs_metadata(documents=documents)


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


def combine_user_messages(messages: List[DiscordMessage], time_threshold: int) -> List[DiscordMessage]:
    """
     Combines consecutive user messages that are sent within a specified time threshold.

     Parameters:
     - messages (List[DiscordMessage]): A list of DiscordMessage objects representing user messages.
     - time_threshold (int): The time threshold (in minutes) within which consecutive messages will be combined.

     Returns:
     - combined_messages (List[DiscordMessage]): A list of combined DiscordMessage objects.

     Example Usage:
     >>> messages = [...]  # List of DiscordMessage objects
     >>> threshold = 5  # Time threshold of 5 minutes
     >>> combined = combine_user_messages(messages, threshold)
     >>> print(combined)
     [Combined DiscordMessage 1, Combined DiscordMessage 2, ...]
    """
    result: List[DiscordMessage] = []
    current_message: DiscordMessage = messages[0]

    for i in range(1, len(messages)):
        time_difference = messages[i].created_at - messages[i - 1].created_at
        user_not_changed = messages[i].user == messages[i - 1].user

        if (time_difference <= timedelta(minutes=time_threshold)) and user_not_changed:
            current_message.content = current_message.content + "\n" + messages[i].content
        else:
            result.append(current_message)
            current_message = messages[i]

    result.append(current_message)
    return result


def serialize_datetime(obj):
    """
    Serialize a datetime object into an ISO 8601 formatted string.

    Example:
        >>> dt = datetime(2023, 9, 12, 15, 30)
        >>> serialize_datetime(dt)
        '2023-09-12T15:30:00'
    """
    if isinstance(obj, datetime):
        return obj.isoformat()
    raise TypeError(f"Object of type {type(obj)} is not JSON serializable")


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
        >>> from core.DiscordMessage import DiscordMessage
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


def add_header(channel_name: str, chat_history: str) -> str:
    return f"# Chat History for {channel_name}\n\n{chat_history}"


def remove_discord_mention(msg: str) -> str:
    """
    Remove Discord user mentions from a given message.

    This function takes a message string and removes any Discord user mentions
    in the format <@123456789>. It returns the modified message with mentions removed.

    Args:
        msg (str): The message string possibly containing user mentions.

    Returns:
        str: The message with mentions removed.

    Example:
        >>> message = "Hello, <@123456789>! How are you today?"
        >>> cleaned_message = remove_discord_mention(message)
        >>> print(cleaned_message)
        'Hello, ! How are you today?'
    """
    return re.sub(r"<@.*?>", "", msg)


async def get_message_before_v2(ctx, message: Message) -> Optional[Message]:
    channel = ctx.channel
    try:
        async for previous_message in channel.history(limit=2, before=message):
            # The limit is set to 2, so it will fetch the message before the target message
            if previous_message.id != message.id:
                return previous_message
    except discord.NotFound:
        return None


async def get_message_before(ctx, message_id: int) -> Optional[Message]:
    channel = ctx.channel
    try:
        message = await channel.fetch_message(message_id)
        async for previous_message in channel.history(limit=2, before=message):
            # The limit is set to 2, so it will fetch the message before the target message
            if previous_message.id != message_id:
                return previous_message
    except discord.NotFound:
        return None


async def fetch_message_thread_v2(
        ctx: discord.ext.commands.Context,
        message: discord.message.Message) -> List[Tuple[str, str]]:
    before = await get_message_before_v2(ctx, message)
    message_content: List[Tuple[str, str]]

    if message.reference is not None:
        referenced_message = await ctx.fetch_message(message.reference.message_id)
        message_content = await fetch_message_thread_v2(ctx, referenced_message) + [
            (referenced_message.author.name, referenced_message.content)]
    elif abs(before.created_at - message.created_at) < timedelta(
            minutes=5) and before.author.name == message.author.name:
        message_content = await fetch_message_thread_v2(ctx, before) + [(before.author.name, before.content)]
    else:
        message_content = []

    return message_content


async def fetch_message_thread(
        ctx: discord.ext.commands.Context,
        reference: discord.message.MessageReference) -> List[str]:
    """
    Retrieve a message thread including the referenced message.

    This asynchronous function takes a `MessageReference` object as input and
    retrieves a message thread, which includes the content of the referenced
    message and its parent messages if they exist. The messages are returned
    as a list in chronological order, with the referenced message first.

    Args:
        ctx (discord.ext.commands.Context): The Discord Message's Context.
        reference (discord.message.MessageReference): A `MessageReference` object containing
            information about the referenced message.

    Returns:
        List[str]: A list of message contents in chronological order.
    """
    if reference is None:
        return []
    referenced_message = await ctx.fetch_message(reference.message_id)
    parent_reference = referenced_message.reference
    parent_messages = await fetch_message_thread(ctx, parent_reference) if parent_reference else []
    message_content: list[str] = [referenced_message.content]
    return parent_messages + message_content


async def send_message_in_chunks(ctx, msg: str, chunk_size: int = 2000):
    """
    Send a long message in chunks to a Discord channel.

    This asynchronous function takes a Discord context (`ctx`), a message string (`msg`),
    and an optional chunk size (`chunk_size`) as input. It splits the message into chunks
    of the specified size while preserving line breaks and sends each chunk as a separate
    message to the specified context.

    Args:
        ctx: The Discord context representing the message sender and channel.
        msg (str): The message text to be sent.
        chunk_size (int, optional): The maximum character limit for each message chunk.
            Default is 2000 characters.
    """
    for chunk in split_string_preserve_suprimum_number_of_lines(msg, chunk_size):
        await ctx.send(chunk)


def _server_info() -> str:
    channels = bot.get_all_channels()
    guilds = set([(ch.guild.name, ch.guild.id) for ch in channels])

    guild_info = """===== Guild Info ====="""
    for guild in guilds:
        guild_info = guild_info + f"""\nguild name: {guild[0]}\nguild id: {guild[1]}\n"""

    channels = bot.get_all_channels()
    channels_info = "====== Channels ======="
    for channel in channels:
        channels_info = channels_info + f"\nguild: {channel.guild}, name: {channel.name} id: {channel.id}"

    info = guild_info + "\n" + channels_info
    return info


def main():
    import sqlite3
    log.info(f"started with sqlite version: ${sqlite3.sqlite_version}")
    bot.run(token=os.environ['DISCORD_BOT_TOKEN'])


if __name__ == "__main__":
    main()
