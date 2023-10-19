import unittest

import discord
from discord.ext import commands
from discord.ext.commands import Bot
from structlog import getLogger

from config import load_config

config = load_config()

intents = discord.Intents.default()
intents.message_content = True
intents.members = True

bot: Bot = commands.Bot(command_prefix="!", intents=intents)
client = discord.Client(intents=intents)
log = getLogger()

import os


class TestIndexOperations(unittest.TestCase):
    def test_index_channel(self):
        from core.discord_bot import index_channel
        from datetime import datetime, timedelta
        from config import load_config
        config = load_config()
        channel_id = 630498701860929559

        index_channel(ctx=1, channel_id=channel_id, after=(datetime.now() - timedelta(days=1)).strftime("%Y-%m-%d"))
        bot.run(token=os.environ['DISCORD_BOT_TOKEN'])

if __name__ == '__main__':
    unittest.main()
