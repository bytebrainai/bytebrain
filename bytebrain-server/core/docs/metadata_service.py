import json
import sqlite3
from datetime import datetime
from sqlite3 import Connection
from typing import Optional, List
from uuid import UUID

from langchain.schema import Document


class DocumentMetadataService:
    def __init__(self, database_file: str):
        self.database_file = database_file
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
            conn = self.create_connection()
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

    def get_docs_ids_by_source_id(self, resource_id) -> List[UUID]:
        with sqlite3.connect(self.database_file) as connection:
            try:
                cursor = connection.cursor()
                select_query = "SELECT uuid FROM stored_docs WHERE source_id = ?"
                cursor.execute(select_query, (resource_id,))
                doc_ids = [UUID(row[0]) for row in cursor.fetchall()]
                return doc_ids

            except sqlite3.Error as e:
                print(f"Error retrieving document IDs: {e}")
                return []

    def delete_docs_by_resource_id(self, resource_id: str):
        with sqlite3.connect(self.database_file) as connection:
            try:
                cursor = connection.cursor()
                delete_query = "DELETE FROM stored_docs WHERE source_id = ?"
                cursor.execute(delete_query, (resource_id,))
                connection.commit()
                print(f"Deleted {cursor.rowcount} rows with source_id {resource_id}")

            except sqlite3.Error as e:
                print(f"Error deleting rows: {e}")

    def get_metadata_list(self, doc_source_type: str, doc_source_id: str) -> List[dict]:
        conn = self.create_connection()
        cur = conn.cursor()
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
            conn = self.create_connection()
            cursor = conn.cursor()
            cursor.execute('''
                INSERT or REPLACE INTO stored_docs (uuid, source_id, source_type, created_at, metadata)
                VALUES (?, ?, ?, ?, ?)
            ''', (str(doc_uuid), doc_source_id, doc_source_type, created_at, json.dumps(metadata)))
            conn.commit()
        except sqlite3.Error as e:
            print(e)

    # TODO: do not pass docs, instead pass metadata
    def save_docs_metadata(self, documents: List[Document]):
        stored_data = [
            (x.metadata['doc_uuid'], x.metadata['doc_source_id'], x.metadata['doc_source_type'], datetime.now(),
             x.metadata) for x in documents]
        self.insert_batch_data(stored_data)

    def insert_batch_data(self, data_list):
        try:
            conn = self.create_connection()
            cursor = conn.cursor()

            cursor.executemany('''
                INSERT OR REPLACE INTO stored_docs (uuid, source_id, source_type, created_at, metadata)
                VALUES (?, ?, ?, ?, ?)
            ''', [(str(doc_uuid), doc_source_id, doc_source_type, created_at, json.dumps(metadata)) for
                  doc_uuid, doc_source_id, doc_source_type, created_at, metadata in data_list])

            conn.commit()
        except sqlite3.Error as e:
            print(e)

    def fetch_last_item(self, doc_source_id: str):
        try:
            conn = self.create_connection()
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

    def fetch_last_item_in_discord_channel(self, doc_source_id: str, channel_id: id):
        try:
            conn = self.create_connection()
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
