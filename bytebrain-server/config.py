from dataclasses import dataclass

import yaml


@dataclass
class ByteBrainConfig:
    name: str
    project_name: str
    webservice_prompt: str
    discord_prompt: str
    db_dir: str
    host: str
    port: int
    discord_messages_window_size: int
    discord_messages_common_length: int
    discord_update_interval: int


def load_config() -> ByteBrainConfig:
    with open('bytebrain.yml', 'r') as file:
        config = yaml.safe_load(file)

    return ByteBrainConfig(**config)
