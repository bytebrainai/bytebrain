import sqlite3
import unittest
from datetime import datetime, timedelta

from core.docs.stored_docs import fetch_last_item_in_discord_channel, insert_batch_data, fetch_last_item


class TestStoredDocsOperations(unittest.TestCase):

    def setUp(self):
        self.conn = sqlite3.connect(':memory:')
        self.create_test_table()

    def create_test_table(self):
        self.conn.execute('''
            CREATE TABLE IF NOT EXISTS stored_docs (
                uuid TEXT PRIMARY KEY,
                source_identifier TEXT,
                created_at DATETIME,
                metadata JSON
            )
        ''')

    def tearDown(self):
        self.conn.close()

    def test_fetch_last_item_in_discord_channel_with_multiple_items(self):
        self.insert_test_multiple_data()
        result = fetch_last_item_in_discord_channel(self.conn, 'test_source', 'test_channel')
        self.assert_last_item(result, 'uuid1')

    def test_fetch_last_item_in_discord_channel(self):
        self.insert_test_data()
        result = fetch_last_item_in_discord_channel(self.conn, 'test_source', 'test_channel')
        self.assert_last_item(result, 'test_uuid')

    def test_insert_batch_data(self):
        data_list = [
            ('uuid1', 'source1', datetime.now(), {'key1': 'value1'}),
            ('uuid2', 'source2', datetime.now(), {'key2': 'value2'}),
            ('uuid3', 'source3', datetime.now(), {'key3': 'value3'}),
        ]
        insert_batch_data(self.conn, data_list)
        self.assert_data_inserted(data_list)

    def test_insert_batch_data_empty_list(self):
        data_list = []
        insert_batch_data(self.conn, data_list)
        self.assert_data_inserted([])

    def test_insert_batch_data_with_duplicate_uuid(self):
        data_list = [
            ('uuid1', 'source1', datetime.now(), {'key1': 'value1'}),
            ('uuid1', 'source2', datetime.now(), {'key2': 'value2'}),
        ]
        insert_batch_data(self.conn, data_list)
        # TODO: Check if we need to update values
        self.assert_data_inserted([('uuid1', 'source1', datetime, {'key1': 'value1'})])

    def test_fetch_last_item_with_data(self):
        source_identifier = 'test_source'
        self.insert_test_data_with_source_identifier(source_identifier)
        result = fetch_last_item(self.conn, source_identifier)
        self.assertIsNotNone(result)

    def test_fetch_last_item_empty_result(self):
        source_identifier = 'nonexistent_source'
        result = fetch_last_item(self.conn, source_identifier)
        self.assertIsNone(result)

    def insert_test_data(self):
        self.conn.execute('''
            INSERT INTO stored_docs (uuid, source_identifier, created_at, metadata)
            VALUES (?, ?, ?, ?)
        ''', ('test_uuid', 'test_source', datetime.now(), '{"channel_id": "test_channel"}'))

    def insert_test_multiple_data(self):
        records = [
            ('uuid1', 'test_source', datetime.now(), '{"channel_id": "test_channel", "foo": "bar"}'),
            ('uuid2', 'test_source', datetime.now() - timedelta(days=1), '{"channel_id": "test_channel"}'),
            ('uuid3', 'test_source', datetime.now() - timedelta(days=2), '{"channel_id": "test_channel"}'),
        ]
        self.conn.executemany('''
            INSERT INTO stored_docs (uuid, source_identifier, created_at, metadata)
            VALUES (?, ?, ?, ?)
        ''', records)

    def insert_test_data_with_source_identifier(self, source_identifier):
        self.conn.execute('''
            INSERT INTO stored_docs (uuid, source_identifier, created_at, metadata)
            VALUES (?, ?, ?, ?)
        ''', ('test_uuid', source_identifier, datetime.now(), '{"channel_id": "test_channel"}'))

    def assert_last_item(self, result, expected_uuid):
        self.assertIsNotNone(result)
        self.assertEqual(result[0], expected_uuid)

    def assert_data_inserted(self, expected_data):
        cursor = self.conn.cursor()
        cursor.execute("SELECT COUNT(*) FROM stored_docs")
        count = cursor.fetchone()[0]
        self.assertEqual(count, len(expected_data))


if __name__ == '__main__':
    unittest.main()
