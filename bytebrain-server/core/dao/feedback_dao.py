# Copyright 2023-2024 ByteBrain AI
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

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
