import datetime
import json
import os
import re
from datetime import datetime
from datetime import timedelta
from typing import Any
from typing import List, Optional

import chat_exporter
import discord
from discord.ext import commands
from discord.guild import Guild
from discord.message import MessageReference
from langchain.embeddings.openai import OpenAIEmbeddings
from langchain.schema import Document
from langchain.vectorstores import Chroma
from structlog import getLogger

import index.index as index
from config import load_config
from core.chatbot import make_question_answering_chatbot

config = load_config()

intents = discord.Intents.default()
intents.message_content = True
intents.members = True

# client = discord.Client(intents=intents)
bot = commands.Bot(command_prefix="!", intents=intents)
log = getLogger()


class Message:
    def __init__(self, id: int, user: str, created_at: datetime, content):
        self.id = id
        self.user = user
        self.created_at = created_at
        self.content = content

    def __str__(self):
        return f"Message(is: {self.id}, user: {self.user}, created_at: {self.created_at}, content: '{self.content}')"

    def to_dict(self):
        return {
            "id": self.id,
            "user": self.user,
            "created_at": self.created_at.isoformat(),
            "content": self.content
        }

    def to_json(self):
        return json.dumps(self.to_dict(), indent=2)

    @classmethod
    def from_json(cls, json_str):
        data = json.loads(json_str)
        created_at = datetime.fromisoformat(data["created_at"])
        return cls(data["id"], data["user"], created_at, data["content"])


class ChannelHistory:
    def __init__(self,
                 guild_id: int,
                 guild_name: str,
                 channel_id: int,
                 channel_name: str,
                 history: List[Message]):
        self.guild_id = guild_id
        self.guild_name = guild_name
        self.channel_id = channel_id
        self.channel_name = channel_name
        self.history = history

    def __str__(self):
        return f"ChannelHistory"

    def to_dict(self):
        return {
            "guild_id": self.guild_id,
            "guild_name": self.guild_name,
            "channel_id": self.channel_id,
            "channel_name": self.channel_name,
            "history": [message.to_dict() for message in self.history]
        }

    def to_json(self):
        return json.dumps(self.to_dict(), indent=2)

    @classmethod
    def from_json(cls, json_str):
        data = json.loads(json_str)
        history = [Message.from_json(json.dumps(message_json)) for message_json in data["history"]]
        return cls(data["guild_id"], data["guild_name"], data["channel_id"], data["channel_name"], history)


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


def get_guild_by_channel(channel_id: int) -> Optional[Guild]:
    for guild in bot.guilds:
        channel = guild.get_channel(channel_id)
        if channel:
            return guild
    return None


@bot.command()
@commands.has_permissions(administrator=True)
async def dump_channel(ctx: commands.Context, channel_id: str, after: Optional[str] = None):
    channel_name = bot.get_channel(int(channel_id)).name
    file_name = f"channel_{channel_name}_{channel_id}.json"
    after_datetime = None if after is None else datetime.strptime(after, "%Y-%m-%d")

    response_msg = f"Started to dump channel {channel_name}" if after is None \
        else f"Started to dump channel {channel_name} after {after}"
    log.info(response_msg)
    await ctx.send(response_msg)

    channel_history = await download_channel_history(int(channel_id), after_datetime)
    file_name = f"channel_{channel_name}_{channel_id}.json"
    dump_channel_history(channel_history, file_name)

    response_msg = f"Channel {channel_id} dumped in {file_name}!"
    log.info(response_msg)
    await ctx.send(response_msg)


async def download_channel_history(channel_id: int, after: Optional[datetime] = None) -> ChannelHistory:
    channel_name = bot.get_channel(int(channel_id)).name
    guild = get_guild_by_channel(int(channel_id))

    messages: list[Message] = [Message(m.id, m.author.name, m.created_at, m.content) async for m in
                               bot.get_channel(channel_id).history(limit=None, oldest_first=True, after=after)]
    combined_messages: list[Message] = combine_user_messages(messages, time_threshold=4)

    channel_history = ChannelHistory(guild_id=guild.id, guild_name=guild.name, channel_id=int(channel_id),
                                     channel_name=channel_name, history=combined_messages)
    return channel_history


def dump_channel_history(channel_history: ChannelHistory, file_name: str):
    with open(file_name, 'w') as file:
        file.write(channel_history.to_json())


async def send_and_log(ctx, message: str):
    await ctx.send(message)
    log.info(message)


@bot.command()
@commands.has_permissions(administrator=True)
async def index_zio_docs(ctx):
    await send_and_log(ctx, "Started indexing ZIO docs on zio.dev")
    index.index_zio_project_docs()
    await send_and_log(ctx, "Finished indexing zio project docs!")


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
    # Ignore messages from bots
    if ctx.author.bot:
        return

    # Ignore messages from users that are not admin
    if not any(role.name == "admin" for role in ctx.author.roles):
        log.error("you are not admin")
        return

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
    log.info(info)

    for chunk in split_string(info, 2000):
        await ctx.send(chunk)


def filter_messages(channel_history: ChannelHistory, after: Optional[datetime]) -> ChannelHistory:
    filtered_messages = []
    if after is not None:
        for message in channel_history.history:
            if message.created_at.replace(tzinfo=None) >= after:
                filtered_messages.append(message)
    else:
        filtered_messages = channel_history.history

    channel_history.history = filtered_messages
    return channel_history


def read_from_cache(file_path: str, after: Optional[datetime]) -> ChannelHistory:
    with open(file_path, 'r') as file:
        messages: ChannelHistory = ChannelHistory.from_json(file.read())
    return filter_messages(messages, after)


async def fetch_channel_history(channel_name: str,
                                channel_id: str,
                                after_datetime: Optional[datetime]) -> ChannelHistory:
    file_path = f"channel_{channel_name}_{channel_id}.json"

    if os.path.exists(file_path):
        channel_history = read_from_cache(file_path, after_datetime)
    else:
        history = await download_channel_history(int(channel_id), after=after_datetime)
        dump_channel_history(history, file_path)
        channel_history = history

    return channel_history


@bot.command("index_channel")
@commands.has_permissions(administrator=True)
async def index_channel(ctx, channel_id: str,
                        after: Optional[str] = None,
                        window_size: Optional[int] = 10,
                        common_length: Optional[int] = 5):
    channel = bot.get_channel(int(channel_id))
    channel_name = channel.name
    after_datetime = None if after is None else datetime.strptime(after, "%Y-%m-%d")

    started_msg = f"started indexing channel {channel_name}" if after is None \
        else f"started indexing channel {channel_name} after {after}"
    log.info(started_msg)
    await ctx.send(started_msg)

    channel_history: ChannelHistory = await fetch_channel_history(channel_name, channel_id, after_datetime)
    batched_messages = sliding_window_with_common_length(channel_history.history, window_size, common_length)
    pages = [(x[0], add_header(channel_name=channel_name, chat_history=x[1])) for x in
             [convert_messages_to_transcript(i) for i in batched_messages]]
    documents = [Document(page_content=page[1], metadata={
        "doc_source": "discord",
        "message_id": f"{page[0]}",
        "channel_id": f"{channel_id}",
        "channel_name": channel_name,
        "guild_id": f"{channel_history.guild_id}",
        "guild_name": channel_history.guild_name
    }) for page in pages]
    log.info(f"Number of pages: {len(pages)}")
    ids = ["discord.com/channels/" + doc.metadata['guild_id'] + '/' + doc.metadata['channel_id'] + '/' + doc.metadata[
        'message_id'] for doc in documents]
    assert (len(ids) == len(documents))
    update_db(documents, ids)
    done_msg = f"Index process for {channel_name} done!"
    log.info(done_msg)
    await ctx.send(done_msg)


def split_string(long_string, chunk_size):
    chunks = []
    current_chunk = ""

    for line in long_string.splitlines():
        if len(current_chunk) + len(line) + 1 > chunk_size:
            chunks.append(current_chunk)
            current_chunk = ""
        current_chunk += line + "\n"

    if current_chunk:
        chunks.append(current_chunk)

    return chunks


def sliding_window_with_common_length(my_list, window_size, common_length):
    result = []
    i = 0

    while True:
        window = my_list[i:i + window_size]

        result.append(window)
        i += window_size - common_length

        if i + window_size > len(my_list):
            break

    return result


def combine_user_messages(messages, time_threshold):
    result: List[Message] = []
    current_message: Message = messages[0]

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
    if isinstance(obj, datetime):
        return obj.isoformat()
    raise TypeError(f"Object of type {type(obj)} is not JSON serializable")


def convert_messages_to_transcript(messages: List[Message]) -> (id, str):
    transcript = ""
    for m in messages:
        transcript = transcript + f"{m.created_at.strftime('%Y-%m-%d %H:%M:%S')} - {m.user} said: {m.content}\n\n"

    return messages[0].id, transcript


def add_header(channel_name: str, chat_history: str) -> str:
    return f"# Chat History for {channel_name}\n\n{chat_history}"


def update_db(texts: List[Document], ids=Optional[List[str]]):
    embeddings: OpenAIEmbeddings = OpenAIEmbeddings()
    Chroma.from_documents(texts, embeddings, ids=ids, persist_directory=config.db_dir)

def add_metadata_to_history(history: List[str]):
    def turn_generator():
        while True:
            yield "User"
            yield "Bot"

    turn_gen = turn_generator()
    history_with_metadata = []

    for index, m in enumerate(history, start=1):
        turn = next(turn_gen)
        history_with_metadata.append(f"{index}. {turn}: {m}")

    return history_with_metadata


def remove_discord_mention(msg: str) -> str:
    """removes any mention inside the meessage like <@234123495>"""
    return re.sub(r"<@.*?>", "", msg)


async def message_history(reference: MessageReference) -> List[str]:
    if reference is None:
        return []
    referenced_message = await bot.get_channel(reference.channel_id).fetch_message(reference.message_id)
    parent_reference = referenced_message.reference
    parent_messages = await message_history(parent_reference) if parent_reference else []
    message_content: list[str] = [referenced_message.content]
    return parent_messages + message_content


@bot.event
async def on_message(message):
    if message.author == bot.user:
        return

    if bot.user.mentioned_in(message):
        chat_history = ["FULL CHAT HISTORY:"] + add_metadata_to_history(await message_history(message.reference))

        async with message.channel.typing():
            log.info(f"received message from {message.channel} channel")
            qa = make_question_answering_chatbot(
                None,
                config.db_dir,
                config.discord_prompt
            )

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

            await message.reply(result['answer'])
    else:
        await bot.process_commands(message)


def main():
    bot.run(token=os.environ['DISCORD_BOT_TOKEN'])
