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

import unittest
import tempfile
import json
import os
from datetime import datetime, timedelta
from langchain.schema import Document
from core.docs.stored_docs import DocumentMetadataService  # Replace 'your_module' with the actual module name


class TestStoredDocsService(unittest.TestCase):
    def setUp(self):
        # Create a temporary database file for testing
        self.temp_db_file = tempfile.mktemp()
        self.service = DocumentMetadataService(self.temp_db_file)

    def tearDown(self):
        # Clean up the temporary database file
        if os.path.exists(self.temp_db_file):
            os.remove(self.temp_db_file)

    def test_insert_and_fetch_last_item(self):
        # Test inserting data and fetching the last item
        doc_uuid = "test_uuid"
        doc_source_id = "test_source_id"
        doc_source_type = "test_source_type"
        created_at = datetime.now()
        metadata = {"key": "value"}

        # Insert data
        self.service.insert_data(doc_uuid, doc_source_id, doc_source_type, created_at, metadata)

        # Fetch the last item
        result = self.service.fetch_last_item(doc_source_id)

        # Assert that the fetched item matches the inserted data
        self.assertEqual(result[0], doc_uuid)
        self.assertEqual(result[1], doc_source_id)
        self.assertEqual(result[2], doc_source_type)
        self.assertEqual(result[4], json.dumps(metadata))

    def test_fetch_last_item_in_discord_channel(self):
        # Test fetching the last item in a Discord channel
        doc_uuid = "test_uuid"
        doc_source_id = "test_source_id"
        channel_id = "test_channel_id"
        created_at = datetime.now() - timedelta(days=1)
        metadata = {"channel_id": channel_id}

        # Insert data
        self.service.insert_data(doc_uuid, doc_source_id, "discord", created_at, metadata)

        # Fetch the last item in the specified channel
        result = self.service.fetch_last_item_in_discord_channel(doc_source_id, channel_id)

        # Assert that the fetched item matches the inserted data
        self.assertEqual(result[0], doc_uuid)
        self.assertEqual(result[1], doc_source_id)
        self.assertEqual(result[2], "discord")
        self.assertEqual(result[4], json.dumps(metadata))

    def test_save_docs_metadata(self):
        # Test saving documents' metadata
        documents = [
            Document(page_content="content_1",
                     metadata={"doc_uuid": "1", "doc_source_id": "source_1", "doc_source_type": "type_1"}),
            Document(page_content="content_2",
                     metadata={"doc_uuid": "2", "doc_source_id": "source_2", "doc_source_type": "type_2"})
        ]

        # Save documents' metadata
        self.service.save_docs_metadata(documents)

        # Fetch the last item for each source
        result_1 = self.service.fetch_last_item("source_1")
        result_2 = self.service.fetch_last_item("source_2")

        # Assert that the fetched items match the saved metadata
        self.assertEqual(result_1[0], "1")
        self.assertEqual(result_2[0], "2")


if __name__ == '__main__':
    unittest.main()
