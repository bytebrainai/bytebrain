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

from core.utils.utils import split_string_preserve_suprimum_number_of_lines


class TestSplitStringFunction(unittest.TestCase):
    def test_split_string_custom_chunk_size_5_with_one_newline(self):
        input_string = "123456789abcdefgh\nijkmnopq"
        chunk_size = 5
        expected_output = ['12345', '6789a', 'bcdef', 'gh', 'ijkmn', 'opq']
        result = split_string_preserve_suprimum_number_of_lines(input_string, chunk_size)
        self.assertEqual(expected_output, result)

    def test_split_string_custom_chunk_size_5_with_two_newline(self):
        input_string = "123456789abcdefgh\ni\njkmnopq"
        chunk_size = 5
        expected_output = ['12345', '6789a', 'bcdef', 'gh\ni', 'jkmno', 'pq']
        result = split_string_preserve_suprimum_number_of_lines(input_string, chunk_size)
        self.assertEqual(expected_output, result)

    def test_split_string_custom_chunk_size_20_with_multiple_newline_1(self):
        input_string = "1234\n567\n89abcdef\nghijk\nmnopq\nrstuvwzyz"
        chunk_size = 20
        expected_output = ['1234\n567\n89abcdef', 'ghijk\nmnopq', 'rstuvwzyz']
        result = split_string_preserve_suprimum_number_of_lines(input_string, chunk_size)
        self.assertEqual(expected_output, result)

    def test_split_string_custom_chunk_size_20_with_multiple_newline_2(self):
        input_string = "1234\n567\n89abcdef\nghijk\nmnopq\nrstuvwzy"
        chunk_size = 20
        expected_output = ['1234\n567\n89abcdef', 'ghijk\nmnopq\nrstuvwzy']
        result = split_string_preserve_suprimum_number_of_lines(input_string, chunk_size)
        self.assertEqual(expected_output, result)

    def test_split_string_custom_chunk_size_5_with_no_newline(self):
        input_string = "1234567890abcdefghij"
        expected_output = ['12345', '67890', 'abcde', 'fghij']
        result = split_string_preserve_suprimum_number_of_lines(input_string, chunk_size=5)
        self.assertEqual(result, expected_output)

    def test_split_string_custom_chunk_size_10_with_no_newline(self):
        input_string = "1234567890abcdefghij"
        expected_output = ['1234567890', 'abcdefghij']
        result = split_string_preserve_suprimum_number_of_lines(input_string, 10)
        self.assertEqual(result, expected_output)

    def test_split_string_empty_string(self):
        input_string = ""
        expected_output = []
        result = split_string_preserve_suprimum_number_of_lines(input_string, 10)
        self.assertEqual(result, expected_output)

    def test_split_string_short_string(self):
        input_string = "Short"
        expected_output = ['Short']
        result = split_string_preserve_suprimum_number_of_lines(input_string, 10)
        self.assertEqual(result, expected_output)


if __name__ == '__main__':
    unittest.main()
