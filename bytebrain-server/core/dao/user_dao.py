import sqlite3
from typing import Optional

from pydantic import BaseModel

import config


class User(BaseModel):
    username: str
    disabled: bool | None = None


class UserInDB(User):
    hashed_password: str


class UserDao:
    _instance = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(UserDao, cls).__new__(cls)
            cls._instance.db_path = config.load_config().users_db
            cls.create_user_table(cls._instance)
        return cls._instance

    def create_user_table(self):
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS users (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                username TEXT UNIQUE NOT NULL,
                hashed_password TEXT NOT NULL,
                created_at DATETIME DEFAULT CURRENT_TIMESTAMP NOT NULL
            )
        """)
        conn.commit()
        conn.close()

    def save_user(self, user: UserInDB):
        with sqlite3.connect(self.db_path) as connection:
            cursor = connection.cursor()
            cursor.execute(
                """
                INSERT INTO users (username, hashed_password)
                VALUES (?, ?)
                """,
                (user.username, user.hashed_password),
            )
            connection.commit()

    def get_user(self, username: str) -> Optional[UserInDB]:
        with sqlite3.connect(self.db_path) as connection:
            cursor = connection.cursor()

            cursor.execute("SELECT * FROM users WHERE username=?", (username,))
            user = cursor.fetchone()

        if user:
            return UserInDB(username=user[1], hashed_password=user[2])
        else:
            return None
