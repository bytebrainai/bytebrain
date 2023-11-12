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
