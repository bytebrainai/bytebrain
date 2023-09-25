import unittest
from unittest import TestCase

from dev.sample_text_splitter import identify_changed_files, identify_removed_snippets
from core.utils import create_dict_from_keys_and_values
from core.db import map_ids_to_paths


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
