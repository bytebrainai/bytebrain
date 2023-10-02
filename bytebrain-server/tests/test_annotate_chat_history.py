import unittest

from core.utils import annotate_history_with_turns
from core.utils import annotate_history_with_turns_v2


class TestAnnotateHistoryWithTurns(unittest.TestCase):

    def test_empty_history(self):
        history = []
        result = annotate_history_with_turns(history)
        self.assertEqual(result, [])

    def test_single_message(self):
        history = ["Hello"]
        result = annotate_history_with_turns(history)
        self.assertEqual(result, ['1. User: Hello'])

    def test_alternating_turns(self):
        history = ["Hello", "How can I assist you?", "I have a question."]
        result = annotate_history_with_turns(history)
        expected = ['1. User: Hello', '2. Bot: How can I assist you?', '3. User: I have a question.']
        self.assertEqual(result, expected)

    def test_longer_history(self):
        history = ["User message 1", "Bot response 1", "User message 2", "Bot response 2"]
        result = annotate_history_with_turns(history)
        expected = ['1. User: User message 1', '2. Bot: Bot response 1', '3. User: User message 2',
                    '4. Bot: Bot response 2']
        self.assertEqual(result, expected)


class TestAnnotateHistoryWithTurnsV2(unittest.TestCase):

    def test_empty_history(self):
        history = []
        result = annotate_history_with_turns_v2(history)
        self.assertEqual(result, [])

    def test_single_message(self):
        history = [("Alice", "Hello")]
        result = annotate_history_with_turns_v2(history)
        self.assertEqual(result, ["1. Alice: Hello"])

    def test_multiple_messages(self):
        history = [("Alice", "Hello"), ("Bob", "Hi"), ("Alice", "How are you?")]
        result = annotate_history_with_turns_v2(history)
        expected = [
            "1. Alice: Hello",
            "2. Bob: Hi",
            "3. Alice: How are you?"
        ]
        self.assertEqual(result, expected)


if __name__ == '__main__':
    unittest.main()
