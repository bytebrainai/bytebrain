import os
from typing import Any

import discord
from structlog import getLogger

from config import load_config
from core.chatbot import make_question_answering_chatbot

logger = getLogger()
config = load_config()

intents = discord.Intents.default()
intents.message_content = True

client = discord.Client(intents=intents)


@client.event
async def on_ready():
    logger.info('We have logged in as {0.user}'.format(client))


@client.event
async def on_message(message):
    if message.author == client.user:
        return

    def is_mentioned():
        return any([user.id == client.user.id for user in message.mentions])

    if is_mentioned():
        qa = make_question_answering_chatbot(
            None,
            config.db_dir,
            config.discord_prompt
        )
        result: dict[str, Any] = await qa.acall(
            {
                "question": message.content,
                "project_name": config.project_name,
                "chat_history": []
            },
            return_only_outputs=True
        )
        logger.info("response for discord is ready", response={
            "question": message.content,
            "result": result['answer']
        })
        await message.channel.send(result['answer'])


def main():
    client.run(token=os.environ['DISCORD_BOT_TOKEN'])
