import unittest
from unittest import TestCase
from dev.sample_text_splitter import identify_changed_snippets, identify_removed_snippets


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
        result = identify_changed_snippets(original, new)
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
        result = identify_changed_snippets(original, new)
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
        result = identify_changed_snippets(original, new)
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
        result = identify_changed_snippets(original, new)
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
        result = identify_changed_snippets(original, new)
        self.assertEqual(result, ['file2.txt'])

    def test_identify_changed_snippets_empty_input(self):
        # Test when both original and new are empty dictionaries
        original = {}
        new = {}
        result = identify_changed_snippets(original, new)
        self.assertEqual(result, [])


class TestIdentifyRemovedSnippets(TestCase):
    def test_identify_changed_snippets_removed_files(self):
        # Test when files are removed in the new dictionary
        original = {
            'file1.txt': ['hash1', 'hash2'],
            'file2.txt': ['hash3'],
            'file3.txt': ['hash4']
        }
        new = {
            'file1.txt': ['hash1', 'hash2'],
            'file3.txt': ['hash4']  # 'file2.txt' is removed
        }
        result = identify_removed_snippets(original, new)
        self.assertEqual(['file2.txt'], result)

    def test_identify_removed_snippets_no_removed_files(self):
        # Test when there are no removed files
        original = {
            'file1.txt': ['hash1', 'hash2'],
            'file2.txt': ['hash3']
        }
        new = {
            'file1.txt': ['hash1', 'hash2'],
            'file2.txt': ['hash3']
        }
        result = identify_removed_snippets(original, new)
        self.assertEqual(result, [])

    def test_identify_removed_snippets_some_removed_files(self):
        # Test when some files are removed
        original = {
            'file1.txt': ['hash1', 'hash2'],
            'file2.txt': ['hash3'],
            'file3.txt': ['hash4']
        }
        new = {
            'file1.txt': ['hash1', 'hash2'],
            'file3.txt': ['hash4']
        }
        result = identify_removed_snippets(original, new)
        self.assertEqual(result, ['file2.txt'])

    def test_identify_removed_snippets_all_removed_files(self):
        # Test when all files are removed
        original = {
            'file1.txt': ['hash1', 'hash2'],
            'file2.txt': ['hash3']
        }
        new = {}
        result = identify_removed_snippets(original, new)
        self.assertEqual(result, ['file1.txt', 'file2.txt'])

    def test_identify_removed_snippets_empty_input(self):
        # Test when both original and new are empty dictionaries
        original = {}
        new = {}
        result = identify_removed_snippets(original, new)
        self.assertEqual(result, [])

    def test_identify_removed_snippets_hashes_changed(self):
        # Test when the original and new dictionaries have the same files, but only the hashes have changed
        original = {
            'file1.txt': ['hash1', 'hash2'],
            'file2.txt': ['hash3', 'hash4'],
            'file3.txt': ['hash5']
        }
        new = {
            'file1.txt': ['hash6', 'hash7'],  # Hashes changed for file1.txt
            'file2.txt': ['hash8', 'hash4'],  # Hashes changed for file2.txt
            'file3.txt': ['hash5']  # No change for file3.txt
        }
        result = identify_removed_snippets(original, new)
        self.assertEqual(result, [])


if __name__ == '__main__':
    unittest.main()
