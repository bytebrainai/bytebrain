from typing import List
from core.db import Database
import config


def get_original_ids() -> List[str]:
    import sqlite3
    con = sqlite3.connect(cfg.db_dir + "/chroma.sqlite3")
    cur = con.cursor()
    sql_query = f"""
      SELECT embedding_id
      FROM embeddings e 
      WHERE embedding_id LIKE 'documentation:github.com/zio/zio:zio-%'
      ORDER BY id Desc 
      """
    try:
        cur.execute(sql_query)
        result = cur.fetchall()
        return [item[0] for item in result]
    except sqlite3.Error as e:
        print("sqlite error: ", e)


cfg = config.load_config()
db = Database(db_dir=cfg.db_dir, embeddings_dir=cfg.embeddings_dir)
ids = get_original_ids()

# db.delete_docs(ids)

print(ids)
