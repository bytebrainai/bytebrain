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

import os

import discord
from discord.ext import commands
from discord.ext.commands import Bot
from structlog import getLogger

from config import load_config
from core.bots.discord.discord_bot import fetch_message_thread

config = load_config()

intents = discord.Intents.default()
intents.message_content = True
intents.members = True

bot: Bot = commands.Bot(command_prefix="!", intents=intents)

log = getLogger()

from discord.message import Message


@bot.event
async def on_ready():
    print("I'm ready")


@bot.event
async def on_message(message):
    message: Message

    ctx = await bot.get_context(message)
    if message.author == bot.user:
        return

    # Do not respond to messages containing @here and @everyone
    if message.mention_everyone:
        return

    thread: list[tuple[str, str]] = await fetch_message_thread(ctx, message)
    print("----")
    for m in thread:
        print(m)

    await bot.process_commands(message)


bot.run(token=os.environ['DISCORD_BOT_TOKEN'])
