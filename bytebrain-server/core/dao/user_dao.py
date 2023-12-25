import sqlite3
from typing import Optional

from pydantic import BaseModel

import config


class User(BaseModel):
    id: str
    email: str
    full_name: Optional[str] = None
    enabled: bool | None = None


class UserInDB(User):
    hashed_password: Optional[str]


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
                id TEXT PRIMARY KEY,
                email TEXT UNIQUE NOT NULL,
                full_name TEXT,
                hashed_password TEXT,
                created_at DATETIME DEFAULT CURRENT_TIMESTAMP NOT NULL,
                enabled BOOLEAN DEFAULT FALSE NOT NULL
            )
        """)
        conn.commit()
        conn.close()

    def save_user(self, user: UserInDB):
        with sqlite3.connect(self.db_path) as connection:
            cursor = connection.cursor()
            cursor.execute(
                """
                INSERT INTO users (id, email, full_name, enabled, hashed_password)
                VALUES (?, ?, ?, ?, ?)
                """,
                (user.id, user.email, user.full_name, user.enabled, user.hashed_password),
            )
            connection.commit()

    def get_user_with_password(self, email: str) -> Optional[UserInDB]:
        with sqlite3.connect(self.db_path) as connection:
            cursor = connection.cursor()

            cursor.execute("SELECT * FROM users WHERE email=?", (email,))
            user = cursor.fetchone()

        if user:
            return UserInDB(id=user[0], email=user[1], full_name=user[2], hashed_password=user[3])
        else:
            return None

    def get_user(self, email: str) -> Optional[User]:
        with sqlite3.connect(self.db_path) as connection:
            cursor = connection.cursor()

            cursor.execute("SELECT * FROM users WHERE email=?", (email,))
            user = cursor.fetchone()

        if user:
            return User(id=user[0], email=user[1], full_name=user[2])
        else:
            return None

    def set_enabled(self, id: str, value: bool):
        with sqlite3.connect(self.db_path) as connection:
            cursor = connection.cursor()

            cursor.execute("UPDATE users SET enabled=? WHERE id=?", (value, id))
            connection.commit()
