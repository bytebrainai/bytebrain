# Copyright 2023-2024 ByteBrain AI
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

import sqlite3

from config import load_config

cfg = load_config()

con = sqlite3.connect(cfg.db_dir + "/chroma.sqlite3")
cur = con.cursor()
sql_query = f"""
  SELECT embedding_id
  FROM embeddings e 
  WHERE embedding_id LIKE 'documentation:github.com/zio/zio:zio-sbt%'
  ORDER BY id Desc 
  """
try:
    cur.execute(sql_query)
    result = cur.fetchall()
    print(result)
    print([item[0] for item in result])
except sqlite3.Error as e:
    print("sqlite error: ", e)
