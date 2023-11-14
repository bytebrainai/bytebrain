import json
import sqlite3
from datetime import datetime
from typing import Any, List

from pydantic.main import BaseModel


class FeedbackCreate(BaseModel):
    chat_history: List[Any]
    is_useful: bool


class FeedbackService:
    def __init__(self, feedbacks_db):
        self.feedbacks_db = feedbacks_db

    def create_feedback_db(self):
        conn = sqlite3.connect(self.feedbacks_db)
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

    def add_feedback(self, feedback: FeedbackCreate):
        conn = sqlite3.connect(self.feedbacks_db)
        cursor = conn.cursor()
        created_at = datetime.utcnow()

        cursor.execute('''
            INSERT INTO feedbacks (chat_history, is_useful, created_at) 
            VALUES (?, ?, ?)
        ''', (json.dumps(feedback.chat_history), feedback.is_useful, created_at))

        conn.commit()
        conn.close()
