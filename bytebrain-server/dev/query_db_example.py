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
