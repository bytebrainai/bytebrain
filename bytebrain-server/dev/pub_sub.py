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

import sqlite3
import threading
import time


class PubSub:
    def __init__(self, database_path):
        self.database_path = database_path
        self.conn = sqlite3.connect(database_path)
        self.create_table()

    def create_table(self):
        cursor = self.conn.cursor()
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS messages (
                id INTEGER PRIMARY KEY,
                content TEXT
            )
        ''')
        self.conn.commit()

    def publish_message(self, content):
        cursor = self.conn.cursor()
        cursor.execute('INSERT INTO messages (content) VALUES (?)', (content,))
        self.conn.commit()

    def subscribe_messages(self):
        cursor = self.conn.cursor()
        cursor.execute('SELECT * FROM messages ORDER BY id DESC LIMIT 1')
        result = cursor.fetchone()
        return result[1] if result else None


def subscriber(pubsub):
    while True:
        message = pubsub.subscribe_messages()
        if message:
            print(f"Received message: {message}")
        time.sleep(1)


if __name__ == "__main__":
    pubsub = PubSub("/tmp/pubsub_example.db")

    # Start subscriber in a separate thread
    subscriber_thread = threading.Thread(target=subscriber, args=(pubsub,), daemon=True)
    subscriber_thread.start()

    # Publish messages
    for i in range(5):
        pubsub.publish_message(f"Message {i}")
        time.sleep(2)
