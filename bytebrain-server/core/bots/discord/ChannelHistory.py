import json
import os
from datetime import datetime
from datetime import timezone
from typing import List, Optional

from core.bots.discord.DiscordMessage import DiscordMessage


class ChannelHistory:
    def __init__(self,
                 guild_id: int,
                 guild_name: str,
                 channel_id: int,
                 channel_name: str,
                 history: List[DiscordMessage]):
        self.guild_id = guild_id
        self.guild_name = guild_name
        self.channel_id = channel_id
        self.channel_name = channel_name
        self.history = history

    def __str__(self):
        return f"ChannelHistory"

    def to_dict(self):
        return {
            "guild_id": self.guild_id,
            "guild_name": self.guild_name,
            "channel_id": self.channel_id,
            "channel_name": self.channel_name,
            "history": [message.to_dict() for message in self.history]
        }

    def to_json(self):
        return json.dumps(self.to_dict(), indent=2)

    @classmethod
    def from_json(cls, json_str):
        data = json.loads(json_str)
        history = [DiscordMessage.from_json(json.dumps(message_json)) for message_json in data["history"]]
        return cls(data["guild_id"], data["guild_name"], data["channel_id"], data["channel_name"], history)

    def dump_channel_history(self, file_name: str, cache_dir):
        with open(file_name, 'w') as file:
            file.write(self.to_json())

        # Check if the directory exists, and create it if it doesn't
        if not os.path.exists(cache_dir):
            os.makedirs(cache_dir)

        with open(os.path.join(cache_dir, file_name), 'w') as file:
            file.write(self.to_json())


def read_from_cache(file_path: str, after: Optional[datetime]) -> ChannelHistory:
    with open(file_path, 'r') as file:
        messages: ChannelHistory = ChannelHistory.from_json(file.read())
        messages.history = filter_messages_from(messages.history, after)
    return messages


def filter_messages_from(history: List[DiscordMessage], after: Optional[datetime]) -> List[DiscordMessage]:
    """
    Filter a list of Discord messages to include only those created from a specified timestamp.

    This function takes a list of Discord messages and filters them to include only messages
    created from the specified timestamp, if provided. If no timestamp is given (after is None),
    all messages in the input list are included in the result.

    Note:
        - Messages with timestamps greater than or equal to the provided 'after' timestamp
          are included in the result.
    """
    filtered_messages = []
    if after is not None:
        for message in history:
            if message.created_at >= after.replace(tzinfo=timezone.utc):
                filtered_messages.append(message)
    else:
        filtered_messages = history
    return filtered_messages
