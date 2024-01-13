import json
import sqlite3
from datetime import datetime
from typing import List, Optional

from pydantic import BaseModel


class ApiKey(BaseModel):
    apikey: str
    name: str
    allowed_domains: List[str]
    project_id: str
    created_at: datetime = datetime.now().replace(microsecond=0)


class ApiKeyDao:
    def __init__(self, project_db):
        self.db_path = project_db
        self._create_table()

    def add_apikey(self, apikey: ApiKey) -> Optional[ApiKey]:
        with sqlite3.connect(self.db_path) as connection:
            cursor = connection.cursor()
            query = '''
                INSERT OR IGNORE INTO apikeys (apikey, name, allowed_domains, project_id, created_at)
                VALUES (?, ?, ?, ?, ?)
            '''
            values = (
                apikey.apikey,
                apikey.name,
                json.dumps(apikey.allowed_domains),
                apikey.project_id,
                apikey.created_at,
            )
            cursor.execute(query, values)
            connection.commit()

            # Check if a new row was inserted
            if cursor.rowcount > 0:
                return apikey
            else:
                return None

    def get_apikeys(self, project_id) -> List[ApiKey]:
        apikeys = []

        try:
            connection = sqlite3.connect(self.db_path)
            cursor = connection.cursor()

            # Fetch API keys based on project_id
            cursor.execute(
                """
                SELECT name, apikey, allowed_domains, project_id, created_at
                FROM apikeys
                WHERE project_id = ?
                """,
                (project_id,)
            )

            # Fetch all rows
            rows = cursor.fetchall()

            # Convert rows to ApiKey objects
            for row in rows:
                name, apikey, allowed_domains_json, project_id, created_at = row
                allowed_domains = json.loads(allowed_domains_json)
                apikey_obj = ApiKey(
                    name=name,
                    apikey=apikey,
                    allowed_domains=allowed_domains,
                    project_id=project_id,
                    created_at=created_at
                )
                apikeys.append(apikey_obj)

            # Close the connection
            connection.close()

        except Exception as e:
            # Handle exceptions (e.g., log the error)
            print(f"Error fetching apikeys: {e}")

        return apikeys

    def get_apikey(self, apikey) -> Optional[ApiKey]:
        try:
            with sqlite3.connect(self.db_path) as connection:
                cursor = connection.cursor()

                cursor.execute(
                    """
                    SELECT apikey, name, allowed_domains, project_id, created_at
                    FROM apikeys
                    WHERE apikey = ?
                    """,
                    (apikey,)
                )

                # Fetch the first row
                row = cursor.fetchone()

                if row:
                    apikey, name, allowed_domains_json, project_id, created_at = row
                    allowed_domains = json.loads(allowed_domains_json)
                    apikey_obj = ApiKey(
                        apikey=apikey,
                        name=name,
                        allowed_domains=allowed_domains,
                        project_id=project_id,
                        created_at=datetime.strptime(created_at, '%Y-%m-%d %H:%M:%S')
                    )
                    return apikey_obj
                else:
                    return None

        except Exception as e:
            # Handle exceptions (e.g., log the error)
            print(f"Error fetching apikey: {e}")
            return None

    def delete_apikey(self, apikey):
        with sqlite3.connect(self.db_path) as connection:
            cursor = connection.cursor()

            resource_query = 'DELETE FROM apikeys WHERE apikey = ?'
            resource_values = (apikey,)
            cursor.execute(resource_query, resource_values)

            connection.commit()

    def _create_table(self):
        with sqlite3.connect(self.db_path) as connection:
            cursor = connection.cursor()
            query = f'''
                CREATE TABLE IF NOT EXISTS apikeys (
                    apikey VARCHAR(255) PRIMARY KEY,
                    name VARCHAR(255) NOT NULL,
                    allowed_domains JSON,
                    project_id VARCHAR(255) NOT NULL,
                    created_at TIMESTAMP DEFAULT (strftime('%Y-%m-%d %H:%M:%S', 'now', 'localtime')),
                    FOREIGN KEY (project_id) REFERENCES projects(id)
                );
            '''
            cursor.execute(query)
            connection.commit()
