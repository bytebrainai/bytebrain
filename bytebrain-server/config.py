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
    metadata_docs_db: str
    feedbacks_db: str
    background_jobs_db: str
    resources_db: str
    projects_db: str
    users_db: str
    embeddings_dir: Optional[str]
    discord_cache_dir: Optional[str]
    weaviate_url: Optional[str]
    webservice: WebserviceConfig
    discord: DiscordBotConfig


def load_config() -> ByteBrainConfig:
    with open('bytebrain.yml', 'r') as file:
        config = yaml.safe_load(file)

    name = config['name']
    project_name = config['project_name']
    metadata_docs_db = config['metadata_docs_db']
    feedbacks_db = config['feedbacks_db']
    background_jobs_db = config['background_jobs_db']
    resources_db = config['resources_db']
    projects_db = config['projects_db']
    users_db = config['users_db']
    embeddings_dir = config['embeddings_dir']
    discord_cache_dir = config['discord_cache_dir']
    weaviate_url = config['weaviate_url'] \
        if os.environ.get('APP_ENV', 'development') == 'production' else "http://localhost:8080"
    webservice = WebserviceConfig(**config['webservice'])
    discord = DiscordBotConfig(**config['discord'])

    return ByteBrainConfig(name,
                           project_name,
                           metadata_docs_db,
                           feedbacks_db,
                           background_jobs_db,
                           resources_db,
                           projects_db,
                           users_db,
                           embeddings_dir,
                           discord_cache_dir,
                           weaviate_url,
                           webservice,
                           discord)
