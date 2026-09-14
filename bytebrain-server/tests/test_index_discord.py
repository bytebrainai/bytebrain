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
        from core.bots.discord.discord_bot import index_channel
        from datetime import datetime, timedelta
        from config import load_config
        config = load_config()
        channel_id = 630498701860929559

        index_channel(ctx=1, channel_id=channel_id, after=(datetime.now() - timedelta(days=1)).strftime("%Y-%m-%d"))
        bot.run(token=os.environ['DISCORD_BOT_TOKEN'])

if __name__ == '__main__':
    unittest.main()
