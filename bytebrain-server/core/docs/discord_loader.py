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

import asyncio
import os
from datetime import datetime
from datetime import timedelta
from typing import Optional, List, Tuple

from discord.ext.commands import Bot
from discord.message import Message
from structlog import getLogger

import discord
from core.bots.discord.discord_utils import get_guild_by_channel, combine_user_messages
from core.models.discord.ChannelHistory import ChannelHistory, read_from_cache
from core.models.discord.DiscordMessage import DiscordMessage

log = getLogger()


async def dump_channel_history(channel_id: int, after: Optional[datetime], bot: Bot, cache_dir: str) -> ChannelHistory:
    """
    This function first checks if there is a cached file for the channel's history that is not older than two weeks.
    If a valid cache is found, it reads the history from the cache. If no cache is found or if it's older than two
    weeks, it downloads the channel history from the server, combines user messages, and caches the new history.
    """
    channel_name = bot.get_channel(channel_id).name
    guild = get_guild_by_channel(channel_id, bot)
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
        history = await asyncio.wait_for(download_channel_history(channel_id, bot, after=after), 360)
        combined_messages: List[DiscordMessage] = combine_user_messages(history, time_threshold=4)
        channel_history = ChannelHistory(guild_id=guild.id,
                                         guild_name=guild.name,
                                         channel_id=channel_id,
                                         channel_name=channel_name,
                                         history=combined_messages)
        channel_history.dump(file_name=file_path, cache_dir=cache_dir)

    return channel_history


async def download_channel_history(channel_id: int, bot: Bot, after: Optional[datetime] = None) -> List[DiscordMessage]:
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


async def fetch_message_thread(
        ctx: discord.ext.commands.Context,
        message: discord.message.Message) -> List[Tuple[str, str]]:
    before = await get_message_before(ctx, message)
    message_content: List[Tuple[str, str]]

    if message.reference is not None:
        referenced_message = await ctx.fetch_message(message.reference.message_id)
        message_content = await fetch_message_thread(ctx, referenced_message) + [
            (referenced_message.author.name, referenced_message.content)]
    elif abs(before.created_at - message.created_at) < timedelta(
            minutes=5) and before.author.name == message.author.name:
        message_content = await fetch_message_thread(ctx, before) + [(before.author.name, before.content)]
    else:
        message_content = []

    return message_content


async def get_message_before(ctx, message: Message) -> Optional[Message]:
    channel = ctx.channel
    try:
        async for previous_message in channel.history(limit=2, before=message):
            # The limit is set to 2, so it will fetch the message before the target message
            if previous_message.id != message.id:
                return previous_message
    except discord.NotFound:
        return None
