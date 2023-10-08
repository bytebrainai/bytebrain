import json
import os
from typing import Any, List
from urllib.error import HTTPError

import googleapiclient.discovery
from structlog import getLogger

from config import load_config
from core.db import Database

config = load_config()
log = getLogger()
db = Database(config.db_dir, config.embeddings_dir)


from index import index

index.index_ziverge_youtube_channel()

