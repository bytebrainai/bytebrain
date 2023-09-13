from dataclasses import dataclass

import yaml


@dataclass
class DiscordBotConfig:
    prompt: str
    messages_window_size: int
    messages_common_length: int
    update_interval: int


@dataclass
class WebserviceConfig:
    prompt: str
    host: str
    port: int


@dataclass
class ByteBrainConfig:
    name: str
    project_name: str
    db_dir: str
    webservice: WebserviceConfig
    discord: DiscordBotConfig


def load_config() -> ByteBrainConfig:
    with open('bytebrain.yml', 'r') as file:
        config = yaml.safe_load(file)

    name = config['name']
    project_name = config['project_name']
    db_dir = config['db_dir']
    webservice = WebserviceConfig(**config['webservice'])
    discord = DiscordBotConfig(**config['discord'])

    return ByteBrainConfig(name, project_name, db_dir, webservice, discord)
