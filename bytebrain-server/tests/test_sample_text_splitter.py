import unittest
from unittest import TestCase

from dev.sample_text_splitter import identify_changed_files, identify_removed_snippets, map_ids_to_paths, \
    create_dict_from_keys_and_values


class TestIdentifyChanges(TestCase):
    def test_identify_changed_snippets_no_changes(self):
        # Test when there are no changes between the original and new dictionaries
        original = {
            'file1.txt': ['hash1', 'hash2'],
            'file2.txt': ['hash3']
        }
        new = {
            'file1.txt': ['hash1', 'hash2'],
            'file2.txt': ['hash3']
        }
        result = identify_changed_files(original, new)
        self.assertEqual(result, [])

    def test_identify_changed_snippets_added_files(self):
        # Test when new files are added
        original = {
            'file1.txt': ['hash1', 'hash2']
        }
        new = {
            'file1.txt': ['hash1', 'hash2'],
            'file2.txt': ['hash3']
        }
        result = identify_changed_files(original, new)
        self.assertEqual(result, ['file2.txt'])

    def test_identify_changed_snippets_changed_hashes(self):
        # Test when hashes in existing files are changed
        original = {
            'file1.txt': ['hash1', 'hash2'],
            'file2.txt': ['hash3']
        }
        new = {
            'file1.txt': ['hash1', 'hash4'],  # hash2 changed to hash4
            'file2.txt': ['hash3']
        }
        result = identify_changed_files(original, new)
        self.assertEqual(result, ['file1.txt'])

    def test_identify_changed_snippets_reduced_num_of_hashes(self):
        # Test when hashes in existing files are changed
        original = {
            'file1.txt': ['hash1', 'hash2', "hash3"],
            'file2.txt': ['hash3']
        }
        new = {
            'file1.txt': ['hash1', 'hash2'],  # hash3 removed
            'file2.txt': ['hash3']
        }
        result = identify_changed_files(original, new)
        self.assertEqual(result, ['file1.txt'])

    def test_identify_changed_snippets_different_file_counts(self):
        # Test when the number of files differs between original and new
        original = {
            'file1.txt': ['hash1', 'hash2']
        }
        new = {
            'file1.txt': ['hash1', 'hash2'],
            'file2.txt': ['hash3']
        }
        result = identify_changed_files(original, new)
        self.assertEqual(result, ['file2.txt'])

    def test_identify_changed_snippets_empty_input(self):
        # Test when both original and new are empty dictionaries
        original = {}
        new = {}
        result = identify_changed_files(original, new)
        self.assertEqual(result, [])


class TestIdentifyRemovedSnippets(TestCase):
    def test_identify_changed_snippets_removed_files(self):
        # Test when files are removed in the new dictionary
        old = {
            'file1.txt': ['hash1', 'hash2'],
            'file2.txt': ['hash3'],
            'file3.txt': ['hash4']
        }
        new = {
            'file1.txt': ['hash1', 'hash2'],
            'file3.txt': ['hash4']  # 'file2.txt' is removed
        }
        result = identify_removed_snippets(old, new)
        self.assertEqual(['file2.txt'], result)

    def test_identify_removed_snippets_no_removed_files(self):
        # Test when there are no removed files
        old = {
            'file1.txt': ['hash1', 'hash2'],
            'file2.txt': ['hash3']
        }
        new = {
            'file1.txt': ['hash1', 'hash2'],
            'file2.txt': ['hash3']
        }
        result = identify_removed_snippets(old, new)
        self.assertEqual(result, [])

    def test_identify_removed_snippets_some_removed_files(self):
        # Test when some files are removed
        old = {
            'file1.txt': ['hash1', 'hash2'],
            'file2.txt': ['hash3'],
            'file3.txt': ['hash4']
        }
        new = {
            'file1.txt': ['hash1', 'hash2'],
            'file3.txt': ['hash4']
        }
        result = identify_removed_snippets(old, new)
        self.assertEqual(result, ['file2.txt'])

    def test_identify_removed_snippets_all_removed_files(self):
        # Test when all files are removed
        old = {
            'file1.txt': ['hash1', 'hash2'],
            'file2.txt': ['hash3']
        }
        new = {}
        result = identify_removed_snippets(old, new)
        self.assertEqual(result, ['file1.txt', 'file2.txt'])

    def test_identify_removed_snippets_empty_input(self):
        # Test when both original and new are empty dictionaries
        old = {}
        new = {}
        result = identify_removed_snippets(old, new)
        self.assertEqual(result, [])

    def test_identify_removed_snippets_hashes_changed(self):
        # Test when the original and new dictionaries have the same files, but only the hashes have changed
        old = {
            'file1.txt': ['hash1', 'hash2'],
            'file2.txt': ['hash3', 'hash4'],
            'file3.txt': ['hash5']
        }
        new = {
            'file1.txt': ['hash6', 'hash7'],  # Hashes changed for file1.txt
            'file2.txt': ['hash8', 'hash4'],  # Hashes changed for file2.txt
            'file3.txt': ['hash5']  # No change for file3.txt
        }
        result = identify_removed_snippets(old, new)
        self.assertEqual(result, [])


class TestMapIdsToPaths(unittest.TestCase):

    def test_empty_list(self):
        # Test when the input list is empty
        ids = []
        result = map_ids_to_paths(ids)
        self.assertEqual(result, [])

    def test_single_id(self):
        # Test when there is a single ID in the list
        ids = [
            "source_code:github.com/zio/zio:benchmarks/src/main/scala-2.12/zio/GenBenchmarks.scala:fbb107a47a17202f1b5f3a39f3345c09"
        ]
        result = map_ids_to_paths(ids)
        self.assertEqual(result,
                         ["benchmarks/src/main/scala-2.12/zio/GenBenchmarks.scala"])

    def test_multiple_ids(self):
        # Test when there are multiple IDs in the list
        ids = [
            "source_code:github.com/zio/zio:benchmarks/src/main/scala-2.12/zio/GenBenchmarks.scala",
            "source_code:github.com/zio/zio:benchmarks/src/main/scala/zio/ArrayFillBenchmark.scala",
            "source_code:github.com/zio/zio:benchmarks/src/main/scala/zio/AsyncConcurrentBenchmarks.scala"
        ]
        result = map_ids_to_paths(ids)
        expected = [
            "benchmarks/src/main/scala-2.12/zio/GenBenchmarks.scala",
            "benchmarks/src/main/scala/zio/ArrayFillBenchmark.scala",
            "benchmarks/src/main/scala/zio/AsyncConcurrentBenchmarks.scala"
        ]
        self.assertEqual(result, expected)


class TestCreateDictFromKeysAndValues(unittest.TestCase):

    def test_empty_lists(self):
        paths = []
        docs = []
        result = create_dict_from_keys_and_values(paths, docs)
        self.assertEqual(result, {})

    def test_single_element(self):
        paths = ['file1.txt']
        docs = ['document1']
        result = create_dict_from_keys_and_values(paths, docs)
        expected = {'file1.txt': ['document1']}
        self.assertEqual(result, expected)

    def test_multiple_elements(self):
        paths = ['file1.txt', 'file2.txt', 'file1.txt']
        docs = ['document1', 'document2', 'document3']
        result = create_dict_from_keys_and_values(paths, docs)
        expected = {
            'file1.txt': ['document1', 'document3'],
            'file2.txt': ['document2']
        }
        self.assertEqual(result, expected)

    def test_length_mismatch(self):
        paths = ['file1.txt', 'file2.txt']
        docs = ['document1']
        with self.assertRaises(AssertionError):
            create_dict_from_keys_and_values(paths, docs)


if __name__ == '__main__':
    unittest.main()
