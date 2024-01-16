import sqlite3
from datetime import datetime
from typing import List, Optional

from pydantic import BaseModel


class ChatModel(BaseModel):
    id: str
    project_id: str
    name: str
    prompt: str
    created_at: datetime = datetime.now().replace(microsecond=0)


class ChatModelDao:
    def __init__(self, project_db):
        self.db_path = project_db
        self._create_table()

    def add_model(self, chatmodel: ChatModel) -> Optional[ChatModel]:
        with sqlite3.connect(self.db_path) as connection:
            cursor = connection.cursor()
            query = '''
                INSERT OR IGNORE INTO chatmodel (id, project_id, name, prompt, created_at)
                VALUES (?, ?, ?, ?, ?)
            '''
            values = (
                chatmodel.id,
                chatmodel.project_id,
                chatmodel.name,
                chatmodel.prompt,
                chatmodel.created_at,
            )
            cursor.execute(query, values)
            connection.commit()

            # Check if a new row was inserted
            if cursor.rowcount > 0:
                return chatmodel
            else:
                return None

    def get_models(self, project_id) -> List[ChatModel]:
        chatmodels = []

        try:
            connection = sqlite3.connect(self.db_path)
            cursor = connection.cursor()

            # Fetch API keys based on project_id
            cursor.execute(
                """
                SELECT id, name, prompt, created_at
                FROM chatmodels
                WHERE project_id = ?
                """,
                (project_id,)
            )

            # Fetch all rows
            rows = cursor.fetchall()

            # Convert rows to ApiKey objects
            for row in rows:
                id, name, prompt, created_at = row
                chatmodel = ChatModel(
                    id=id,
                    project_id=project_id,
                    name=name,
                    prompt=prompt,
                    created_at=created_at
                )
                chatmodels.append(chatmodel)

            connection.close()

        except Exception as e:
            print(f"Error fetching chatmodel: {e}")

        return chatmodels

    def get_model(self, id) -> Optional[ChatModel]:
        try:
            with sqlite3.connect(self.db_path) as connection:
                cursor = connection.cursor()

                cursor.execute(
                    """
                    SELECT id, project_id, name, prompt, created_at
                    FROM chatmodels 
                    WHERE id = ?
                    """,
                    (id,)
                )

                # Fetch the first row
                row = cursor.fetchone()

                if row:
                    id, project_id, name, prompt, created_at = row
                    chatmodel = ChatModel(
                        id=id,
                        project_id=project_id,
                        name=name,
                        prompt=prompt,
                        created_at=datetime.strptime(created_at, '%Y-%m-%d %H:%M:%S')
                    )
                    return chatmodel
                else:
                    return None

        except Exception as e:
            print(f"Error fetching chatmodel: {e}")
            return None

    def delete_model(self, id):
        with sqlite3.connect(self.db_path) as connection:
            cursor = connection.cursor()

            resource_query = 'DELETE FROM apikeys WHERE id = ?'
            resource_values = (id,)
            cursor.execute(resource_query, resource_values)

            connection.commit()

    def _create_table(self):
        with sqlite3.connect(self.db_path) as connection:
            cursor = connection.cursor()
            query = f'''
                CREATE TABLE IF NOT EXISTS chatmodels (
                    id VARCHAR(255) PRIMARY KEY,
                    project_id VARCHAR(255) NOT NULL,
                    name VARCHAR(255) NOT NULL,
                    prompt TEXT NOT NULL,
                    created_at TIMESTAMP DEFAULT (strftime('%Y-%m-%d %H:%M:%S', 'now', 'localtime')),
                    FOREIGN KEY (project_id) REFERENCES projects(id)
                );
            '''
            cursor.execute(query)
            connection.commit()
