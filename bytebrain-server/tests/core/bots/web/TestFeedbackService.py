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
import os
import sqlite3
import unittest
from datetime import datetime
from tempfile import NamedTemporaryFile

from core.bots.web.feedbacks import FeedbackService, FeedbackCreate


class TestFeedbackService(unittest.TestCase):
    def setUp(self):
        # Create a temporary database for testing
        self.temp_db_file = NamedTemporaryFile(delete=False)
        self.temp_db_filename = self.temp_db_file.name
        self.feedback_service = FeedbackService(self.temp_db_filename)

    def tearDown(self):
        os.unlink(self.temp_db_filename)

    def test_create_feedback_db(self):
        self.feedback_service.create_feedback_db()

        with sqlite3.connect(self.temp_db_filename) as conn:
            cursor = conn.cursor()
            cursor.execute("PRAGMA table_info(feedbacks)")
            columns = [column[1] for column in cursor.fetchall()]

            self.assertIn("id", columns)
            self.assertIn("chat_history", columns)
            self.assertIn("is_useful", columns)
            self.assertIn("created_at", columns)

    def test_add_feedback(self):
        feedback_data = FeedbackCreate(chat_history=["message1", "message2"], is_useful=True)
        self.test_create_feedback_db()
        self.feedback_service.add_feedback(feedback_data)

        with sqlite3.connect(self.temp_db_filename) as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM feedbacks")
            result = cursor.fetchone()

            self.assertIsNotNone(result)
            self.assertEqual(result[1], json.dumps(feedback_data.chat_history))
            self.assertEqual(result[2], feedback_data.is_useful)
            self.assertIsInstance(datetime.strptime(result[3], "%Y-%m-%d %H:%M:%S.%f"), datetime)

    def test_add_feedback_empty_chat_history(self):
        feedback_data = FeedbackCreate(chat_history=[], is_useful=True)

        with self.assertRaises(Exception):
            self.feedback_service.add_feedback(feedback_data)


if __name__ == '__main__':
    unittest.main()
