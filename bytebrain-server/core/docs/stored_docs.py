import json
import sqlite3
from datetime import datetime
from sqlite3 import Connection
from typing import Optional, List

from langchain.schema import Document

import config


class StoredDocsService:
    def __init__(self, database_file: str):
        self.database_file = database_file
        self.conn = self.create_connection()
        self.create_table()

    def create_connection(self) -> Optional[Connection]:
        try:
            conn: Connection = sqlite3.connect(self.database_file)
            return conn
        except sqlite3.Error as e:
            print(e)
        return None

    def create_table(self):
        try:
            cursor = self.conn.cursor()
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS stored_docs (
                    uuid TEXT PRIMARY KEY,
                    source_id TEXT,
                    source_type TEXT,
                    created_at DATETIME,
                    metadata JSON
                )
            ''')
            self.conn.commit()
        except sqlite3.Error as e:
            print(e)

    def get_metadata_list(self, doc_source_type: str, doc_source_id: str) -> List[dict]:
        cur = self.conn.cursor()
        sql_query = f"""
          SELECT uuid, source_id, source_type, created_at, metadata 
          FROM stored_docs
          WHERE source_id = '{doc_source_id}' AND source_type = '{doc_source_type}'
          ORDER BY created_at;
          """
        try:
            cur.execute(sql_query)
            result = cur.fetchall()
            return [json.loads(item[4]) for item in result]
        except sqlite3.Error as e:
            print("sqlite error: ", e)

    def insert_data(self, doc_uuid, doc_source_id, doc_source_type, created_at, metadata):
        try:
            cursor = self.conn.cursor()
            cursor.execute('''
                INSERT INTO stored_docs (uuid, source_id, source_type, created_at, metadata)
                VALUES (?, ?, ?, ?, ?)
            ''', (str(doc_uuid), doc_source_id, doc_source_type, created_at, json.dumps(metadata)))
            self.conn.commit()
        except sqlite3.Error as e:
            print(e)

    def save_docs_metadata(self, documents: List[Document]):
        stored_data = [
            (x.metadata['doc_uuid'], x.metadata['doc_source_id'], x.metadata['doc_source_type'], datetime.now(),
             x.metadata) for x in documents]
        self.insert_batch_data(stored_data)

    def insert_batch_data(self, data_list):
        try:
            cursor = self.conn.cursor()

            cursor.executemany('''
                INSERT OR REPLACE INTO stored_docs (uuid, source_id, source_type, created_at, metadata)
                VALUES (?, ?, ?, ?, ?)
            ''', [(str(doc_uuid), doc_source_id, doc_source_type, created_at, json.dumps(metadata)) for
                  doc_uuid, doc_source_id, doc_source_type, created_at, metadata in data_list])

            self.conn.commit()
        except sqlite3.Error as e:
            print(e)

    def fetch_last_item(self, doc_source_id: str):
        try:
            cursor = self.conn.cursor()

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

    def fetch_last_item_in_discord_channel(self, doc_source_id: str, channel_id: id):
        try:
            cursor = self.conn.cursor()

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
    service = StoredDocsService(config.load_config().stored_docs_db)
    res = service.get_metadata_list("documentation", "zio.dev")
    print(res)
