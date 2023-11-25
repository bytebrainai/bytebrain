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
