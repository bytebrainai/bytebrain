import json
import re
from datetime import timedelta
from typing import List
from typing import Optional

from discord.ext.commands import Bot
from discord.guild import Guild

from core.dao.metadata_dao import DocumentMetadataService
from core.models.discord.DiscordMessage import DiscordMessage
from core.utils.utils import split_string_preserve_suprimum_number_of_lines


def get_guild_by_channel(channel_id: int, bot: Bot) -> Optional[Guild]:
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


def server_info(bot: Bot) -> str:
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


async def send_and_log(ctx, log, message: str):
    await ctx.send(message)
    log.info(message)


async def first_message_of_last_indexed_page(channel_id: int, metadata_service: DocumentMetadataService, bot: Bot) -> Optional[DiscordMessage]:
    """
    Retrieves the first message of the last indexed page associated with a given channel from the database.
    """
    last_item = metadata_service.fetch_last_item_in_discord_channel(doc_source_id="discord", channel_id=channel_id)
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
