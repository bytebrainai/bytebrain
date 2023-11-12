import json
import sqlite3
from sqlite3 import Connection
from typing import Optional, List
from langchain.schema import Document
from datetime import datetime

import config


def create_connection(database_file: str) -> Optional[Connection]:
    try:
        conn: Connection = sqlite3.connect(database_file)
        return conn
    except sqlite3.Error as e:
        print(e)
    return None


def create_table(conn: Connection):
    try:
        cursor = conn.cursor()
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS stored_docs (
                uuid TEXT PRIMARY KEY,
                source_id TEXT,
                source_type TEXT,
                created_at DATETIME,
                metadata JSON
            )
        ''')
        conn.commit()
    except sqlite3.Error as e:
        print(e)


def get_metadata_list(doc_source_type: str, doc_source_id: str) -> List[dict[any, any]]:
    con = create_connection(config.load_config().stored_docs_db)
    cur = con.cursor()
    sql_query = f"""
      SELECT uuid, source_id, source_type, created_at, metadata 
      FROM stored_docs
      WHERE source_id = '{doc_source_id}' AND source_type = '{doc_source_type}'
      ORDER BY created_at;
      """
    try:
        cur.execute(sql_query)
        result = cur.fetchall()
        from datetime import datetime
        import json

        return [json.loads(item[4]) for item in result]
    except sqlite3.Error as e:
        print("sqlite error: ", e)


def insert_data(conn, doc_uuid, doc_source_id, doc_source_type, created_at, metadata):
    try:
        cursor = conn.cursor()
        cursor.execute('''
            INSERT INTO stored_docs (uuid, source_id, source_type, created_at, metadata)
            VALUES (?, ?, ?, ?, ?)
        ''', (str(doc_uuid), doc_source_id, doc_source_type, created_at, json.dumps(metadata)))
        conn.commit()
    except sqlite3.Error as e:
        print(e)


def save_docs_metadata(documents: List[Document], conn: Optional[Connection] = None):
    stored_data = [
        (x.metadata['doc_uuid'], x.metadata['doc_source_id'], x.metadata['doc_source_type'], datetime.now(), x.metadata)
        for x in documents]
    if conn is None:
        cfg = config.load_config()
        with create_connection(cfg.stored_docs_db) as connection:
            create_table(connection)
            insert_batch_data(connection, stored_data)
    else:
        with conn as c:
            insert_batch_data(c, stored_data)


def insert_batch_data(conn, data_list):
    try:
        cursor = conn.cursor()

        cursor.executemany('''
            INSERT OR REPLACE INTO stored_docs (uuid, source_id, source_type, created_at, metadata)
            VALUES (?, ?, ?, ?, ?)
        ''', [(str(doc_uuid), doc_source_id, doc_source_type, created_at, json.dumps(metadata)) for
              doc_uuid, doc_source_id, doc_source_type, created_at, metadata in data_list])

        conn.commit()
    except sqlite3.Error as e:
        print(e)


def fetch_last_item(conn: Connection, doc_source_id: str):
    try:
        cursor = conn.cursor()

        cursor.execute('''
            SELECT * FROM stored_docs
            WHERE source_id = ?
            ORDER BY created_at DESC
            LIMIT 1
        ''', (doc_source_id,))

        result = cursor.fetchone()

        return result

    except sqlite3.Error as e:
        print(e)
        return None


def fetch_last_item_in_discord_channel(conn: Connection, doc_source_id: str, channel_id: str):
    try:
        cursor = conn.cursor()

        cursor.execute('''
            SELECT * FROM stored_docs
            WHERE source_id = ? AND
                  json_extract(metadata, '$.channel_id') = ?
            ORDER BY created_at DESC
            LIMIT 1
        ''', (doc_source_id, channel_id))

        result = cursor.fetchone()

        return result

    except sqlite3.Error as e:
        print(e)
        return None


if __name__ == '__main__':
    res = get_metadata_list("documentation", "zio.dev")
    print(res)
