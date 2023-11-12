import json
from datetime import datetime
from typing import Any, List
import sqlite3

from pydantic.main import BaseModel

from config import load_config

config = load_config()


class FeedbackCreate(BaseModel):
    chat_history: List[Any]
    is_useful: bool


def add_feedback(feedback: FeedbackCreate):
    conn = sqlite3.connect(config.feedbacks_db)
    cursor = conn.cursor()
    created_at = datetime.utcnow()

    cursor.execute('''
        INSERT INTO feedbacks (chat_history, is_useful, created_at) 
        VALUES (?, ?, ?)
    ''', (json.dumps(feedback.chat_history), feedback.is_useful, created_at))

    conn.commit()
    conn.close()


def create_feedback_db():
    conn = sqlite3.connect(config.feedbacks_db)
    cursor = conn.cursor()

    cursor.execute('''
        CREATE TABLE IF NOT EXISTS feedbacks (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            chat_history JSON,
            is_useful BOOLEAN,
            created_at DATETIME
        )
    ''')

    conn.commit()
    conn.close()
