from dataclasses import dataclass
from typing import Optional

import yaml
import os


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
    stored_docs_db: str
    embeddings_dir: Optional[str]
    weaviate_url: Optional[str]
    webservice: WebserviceConfig
    discord: DiscordBotConfig


def load_config() -> ByteBrainConfig:
    with open('bytebrain.yml', 'r') as file:
        config = yaml.safe_load(file)

    name = config['name']
    project_name = config['project_name']
    stored_docs_db = config['stored_docs_db']
    embeddings_dir = config['embeddings_dir']
    weaviate_url = config['weaviate_url'] \
        if os.environ.get('APP_ENV', 'development') == 'production' else "http://localhost:8080"
    webservice = WebserviceConfig(**config['webservice'])
    discord = DiscordBotConfig(**config['discord'])

    return ByteBrainConfig(name, project_name, stored_docs_db, embeddings_dir, weaviate_url, webservice, discord)
