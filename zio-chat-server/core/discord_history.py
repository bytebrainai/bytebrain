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
