import json
from typing import List

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
