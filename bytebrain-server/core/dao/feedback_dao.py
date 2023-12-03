import json
import sqlite3
from datetime import datetime
from typing import Any, List

from pydantic.main import BaseModel


class Feedback(BaseModel):
    chat_history: List[Any]
    is_useful: bool


class FeedbackDao:
    def __init__(self, feedbacks_db):
        self.feedbacks_db = feedbacks_db
        self.create_feedback_db()

    def create_feedback_db(self):
        with sqlite3.connect(self.feedbacks_db) as conn:
            cursor = conn.cursor()
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS feedbacks (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    chat_history JSON,
                    is_useful BOOLEAN,
                    created_at DATETIME
                )
            ''')

    def add_feedback(self, feedback: Feedback):
        created_at = datetime.utcnow()
        chat_history_json = json.dumps(feedback.chat_history)

        with sqlite3.connect(self.feedbacks_db) as conn:
            cursor = conn.cursor()
            cursor.execute('''
                INSERT INTO feedbacks (chat_history, is_useful, created_at) 
                VALUES (?, ?, ?)
            ''', (chat_history_json, feedback.is_useful, created_at))
