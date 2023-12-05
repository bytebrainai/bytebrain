import datetime
import os
from datetime import datetime
from typing import Any
from typing import Optional

import chat_exporter
import discord
from discord.ext import commands, tasks
from discord.ext.commands import Bot
from langchain.embeddings import CacheBackedEmbeddings
from langchain.embeddings.openai import OpenAIEmbeddings
from langchain.storage import LocalFileStore
from langchain.vectorstores import VectorStore
from langchain.vectorstores import Weaviate
from structlog import getLogger
from weaviate import Client

import discord_utils
from config import load_config
from core.dao.metadata_dao import MetadataDao
from core.docs.discord_loader import dump_channel_history, fetch_message_thread
from core.llm.chains import make_question_answering_chain
from core.services.document_service import DocumentService
from core.services.vectorstore_service import VectorStoreService
from core.utils.utils import annotate_history_with_turns_v2
from core.utils.utils import split_string_preserve_suprimum_number_of_lines
from discord_utils import remove_discord_mention, send_and_log, send_message_in_chunks

config = load_config()
stored_docs = MetadataDao(config.metadata_docs_db)


os.environ['WEAVIATE_URL'] = config.weaviate_url
embeddings_dir = config.embeddings_dir
weaviate_client = Client(url=config.weaviate_url)
underlying_embeddings: OpenAIEmbeddings = OpenAIEmbeddings()
fs = LocalFileStore(config.embeddings_dir)
cached_embedder = CacheBackedEmbeddings.from_bytes_store(
    underlying_embeddings, fs, namespace=underlying_embeddings.model
)
index_name = 'Zio'
text_key = "text"

weaviate: VectorStore = Weaviate(weaviate_client,
                                 index_name=index_name,
                                 text_key=text_key,
                                 attributes=['source'],
                                 embedding=cached_embedder,
                                 by_text=False)

vectorstore_service = VectorStoreService(weaviate, weaviate_client, cached_embedder, index_name, text_key)
metadata_dao = MetadataDao(config.metadata_docs_db)
indexer = DocumentService(vectorstore_service, metadata_dao)

intents = discord.Intents.default()
intents.message_content = True
intents.members = True

bot: Bot = commands.Bot(command_prefix="!", intents=intents)
log = getLogger()


@bot.event
async def on_ready():
    log.info(f"Hello! I'm {config.name} and ready to receive commands!")


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

    await dump_channel_history(channel_id, after_datetime, bot, config.discord_cache_dir)

    response_msg = f"Channel {channel_id} was dumped!"
    log.info(response_msg)
    await ctx.send(response_msg)


@bot.command()
@commands.has_permissions(administrator=True)
async def index_zio_docs(ctx):
    await send_and_log(ctx, log, "Started indexing ZIO docs on zio.dev")
    indexer.index_zio_project_docs()
    await send_and_log(ctx, log, "Finished indexing zio project docs!")


@bot.command()
@commands.has_permissions(administrator=True)
async def index_ziverge_youtube_channel(ctx):
    await send_and_log(ctx, log, "Started indexing Ziverge's Youtube Channel!")
    indexer.index_ziverge_youtube_channel()
    await send_and_log(ctx, log, "Finished indexing Ziverge's Youtube Channel!")


@bot.command()
@commands.has_permissions(administrator=True)
async def index_zionomicon(ctx):
    await send_and_log(ctx, log, "Started indexing Zionomicon book")
    indexer.index_zionomicon_book()
    await send_and_log(ctx, log, "Finished indexing zionomicon book!")


@bot.command()
@commands.has_permissions(administrator=True)
async def index_zio_source(ctx):
    await send_and_log(ctx, log, "Started indexing ZIO's source code")
    indexer.index_zio_project_source_code()
    await send_and_log(ctx, log, "Finished indexing zio's source codes!")


@bot.command()
@commands.has_permissions(administrator=True)
async def index_zio_ecosystem_source(ctx):
    await send_and_log(ctx, log, "Started indexing ZIO's")
    indexer.index_zio_ecosystem_source_code()
    await send_and_log(ctx, log, "Started indexing ZIO's")


@bot.command()
@commands.has_permissions(administrator=True)
async def server_info(ctx):
    info = discord_utils.server_info(bot)
    log.info(info)
    await send_message_in_chunks(ctx, info)


@bot.command("index_channel")
@commands.has_permissions(administrator=True)
async def index_channel(ctx, channel_id: int,
                        after: Optional[str] = None,
                        window_size: Optional[int] = config.discord.messages_window_size,
                        common_length: Optional[int] = config.discord.messages_common_length):
    await update_discord_channel(ctx, channel_id, after, window_size, common_length)


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
            qa = make_question_answering_chain(
                websocket=None,
                vector_store=weaviate,
                prompt_template=config.discord.prompt,
                tenant = None
            )

            chat_history = ["FULL CHAT HISTORY:"] + annotate_history_with_turns_v2(
                await fetch_message_thread(ctx, message))

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
async def update_discord_channel(ctx, channel_id: int,
                                 after: Optional[str] = None,
                                 window_size: Optional[int] = config.discord.messages_window_size,
                                 common_length: Optional[int] = config.discord.messages_common_length):
    channel_name = bot.get_channel(channel_id).name
    await send_and_log(ctx, log, f"Started updating {channel_name} channel.")
    try:
        length = await indexer.index_channel_history(
            channel_id,
            after,
            window_size,
            common_length,
            config.discord_cache_dir,
            bot
        )
        log.info(f"Updated {length} of docs for channel {channel_name}")
    except Exception as e:
        log.error(f"Exception occurred during updating {channel_name} channel! + {str(e)}")

    await send_and_log(ctx, log, f"The {channel_name} channel updated!")


@bot.command()
async def update_discord_channels(ctx, guild_id: int):
    guild_name = bot.get_guild(guild_id).name
    await ctx.send(f"Started updating channels inside {guild_name} guild!")
    update_discord_channels_periodically.start(ctx, guild_id)


@tasks.loop(hours=config.discord.update_interval)
async def update_discord_channels_periodically(ctx, guild_id: int):
    for ch in bot.get_guild(guild_id).channels:
        await update_discord_channel(ctx, ch.id)
    await send_and_log(ctx, log, "All channels were updated!")


def main():
    import sqlite3
    log.info(f"started with sqlite version: ${sqlite3.sqlite_version}")
    bot.run(token=os.environ['DISCORD_BOT_TOKEN'])


if __name__ == "__main__":
    main()
