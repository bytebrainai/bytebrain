import datetime
import json
import os
from datetime import datetime
from datetime import timedelta
from typing import List, Optional

import chat_exporter
import discord
from discord.ext import commands
from discord.guild import Guild
from langchain.embeddings.openai import OpenAIEmbeddings
from langchain.schema import Document
from langchain.vectorstores import Chroma
from structlog import getLogger

from core.utils.upgrade_sqlite import upgrade_sqlite_version

intents = discord.Intents.default()
intents.members = True

# Enable message content intents
intents.message_content = True

client = discord.Client(intents=intents)
bot = commands.Bot(command_prefix="!", intents=intents)
logger = getLogger()


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


@bot.command()
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

    logger.info(f"Transcript has been written to '{file_path}'.")


def get_guild_by_channel(channel_id: int) -> Optional[Guild]:
    for guild in bot.guilds:
        channel = guild.get_channel(channel_id)
        if channel:
            return guild
    return None


@bot.command()
async def dump_channel(ctx: commands.Context, channel_id: str, after: Optional[str] = None):
    channel_name = bot.get_channel(int(channel_id)).name
    file_name = f"channel_{channel_name}_{channel_id}.json"
    after_datetime = None if after is None else datetime.strptime(after, "%Y-%m-%d")

    response_msg = f"Started to dump channel {channel_name}" if after is None \
        else f"Started to dump channel {channel_name} after {after}"
    logger.info(response_msg)
    await ctx.send(response_msg)

    channel_history = await download_channel_history(int(channel_id), after_datetime)
    file_name = f"channel_{channel_name}_{channel_id}.json"
    dump_channel_history(channel_history, file_name)

    response_msg = f"Channel {channel_id} dumped in {file_name}!"
    logger.info(response_msg)
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


@bot.command()
async def server_info(ctx):
    # Ignore messages from bots
    if ctx.author.bot:
        return

    # Ignore messages from users that are not admin
    if not any(role.name == "admin" for role in ctx.author.roles):
        logger.error("you are not admin")
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
    logger.info(info)

    for chunk in split_string(info, 2000):
        await ctx.send(chunk)


def filter_messages(channelhistory: ChannelHistory, after: Optional[datetime]) -> ChannelHistory:
    filtered_messages = []
    if after is not None:
        for message in channelhistory.history:
            if message.created_at.replace(tzinfo=None) >= after:
                filtered_messages.append(message)
    else:
        filtered_messages = channelhistory

    channelhistory.history = filtered_messages
    return channelhistory


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


@bot.command()
async def index_channel(ctx, channel_id: str,
                        after: Optional[str] = None,
                        window_size: Optional[int] = 10,
                        common_length: Optional[int] = 5):
    channel_name = bot.get_channel(int(channel_id)).name
    after_datetime = None if after is None else datetime.strptime(after, "%Y-%m-%d")

    started_msg = f"started indexing channel {channel_name}" if after is None \
        else f"started indexing channel {channel_name} after {after}"
    logger.info(started_msg)
    await ctx.send(started_msg)

    channel_history: ChannelHistory = await fetch_channel_history(channel_name, channel_id, after_datetime)
    batched_messages = sliding_window_with_common_length(channel_history.history, window_size, common_length)
    pages = [convert_messages_to_transcript(i) for i in batched_messages]
    documents = [Document(page_content=page[1], metadata={
        "source_doc": "discord",
        "message_id": f"{page[0]}",
        "channel_id": f"{channel_id}",
        "channel_name": channel_name,
        "guild_id": f"{channel_history.guild_id}",
        "guild_name": channel_history.guild_name
    }) for page in pages]
    logger.info(f"Number of pages: {len(pages)}")
    update_vectorestore(documents)
    logger.info("Index process done!")


@bot.event
async def on_ready():
    logger.info("Hello! I'm ready to receive commands!")


def main():
    bot.run(token=os.environ['DISCORD_BOT_TOKEN'])


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

    while i + window_size <= len(my_list):
        window = my_list[i:i + window_size]

        result.append(window)
        i += window_size - common_length

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


def update_vectorestore(texts: List[Document]):
    upgrade_sqlite_version()
    embeddings: OpenAIEmbeddings = OpenAIEmbeddings()
    Chroma.from_documents(texts, embeddings, persist_directory=os.environ["ZIOCHAT_CHROMA_DB_DIR"])
