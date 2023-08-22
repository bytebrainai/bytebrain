import os
from typing import Any, List

import discord
from discord.message import MessageReference
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

    async def message_history(reference: MessageReference) -> List[str]:
        if reference is None:
            return []
        referenced_message = await client.get_channel(reference.channel_id).fetch_message(reference.message_id)
        parent_reference = referenced_message.reference
        parent_messages = await message_history(parent_reference) if parent_reference else []
        message_content: list[str] = [referenced_message.content]
        return parent_messages + message_content

    if is_mentioned():
        def add_metadata_to_history(history: List[str]):
            def turn_generator():
                while True:
                    yield "User"
                    yield "Bot"

            turn_gen = turn_generator()
            history_with_metadata = []

            for index, m in enumerate(history, start=1):
                turn = next(turn_gen)
                history_with_metadata.append(f"{index}. {turn}: {m}")

            return history_with_metadata

        chat_history = ["CHAT HISTORY:"] + add_metadata_to_history(await message_history(message.reference))
        qa = make_question_answering_chatbot(
            None,
            config.db_dir,
            config.discord_prompt
        )
        result: dict[str, Any] = await qa.acall(
            {
                "question": message.content,
                "project_name": config.project_name,
                "chat_history": chat_history
            },
            return_only_outputs=True
        )
        logger.info("response for discord is ready", response={
            "question": message.content,
            "result": result['answer']
        })
        await message.reply(result['answer'])


def main():
    client.run(token=os.environ['DISCORD_BOT_TOKEN'])
