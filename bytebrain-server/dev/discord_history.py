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

# Enter the channel ID of the channel you want to download the history from
CHANNEL_ID = 0

intents = discord.Intents.default()
intents.message_content = True

client = discord.Client(intents=intents)


@client.event
async def on_ready():
    print(f'We have logged in as {client.user}')

    # Get the channel object
    channel = client.get_channel(CHANNEL_ID)
    if channel is None:
        print('Invalid channel ID')
        await client.close()
        return

    # Fetch all the messages from the channel's history
    messages = []
    async for message in channel.history(limit=None):
        messages.append(message)

    # Process the downloaded messages here
    for message in messages:
        print(f'Author: {message.author.name}')
        print(f'Content: {message.content}')
        print(f'data: {message.created_at}')
        print('---')

    # Close the client connection
    await client.close()


def main():
    client.run(os.environ['DISCORD_BOT_TOKEN'])
