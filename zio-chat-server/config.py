from dataclasses import dataclass

import yaml


@dataclass
class ByteBrainConfig:
    name: str
    project_name: str
    prompt_template: str
    db_dir: str
    host: str
    port: int


def load_config() -> ByteBrainConfig:
    with open('bytebrain.yml', 'r') as file:
        config = yaml.safe_load(file)

    return ByteBrainConfig(**config)
