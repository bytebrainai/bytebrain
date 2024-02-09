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

import hashlib
import tempfile
import time
from datetime import datetime
from functools import wraps
from typing import Dict, List, TypeVar, Tuple

from git import Repo

T = TypeVar('T')


def calculate_md5_checksum(text):
    data = text.encode('utf-8')
    md5_hash = hashlib.md5()
    md5_hash.update(data)
    md5_checksum = md5_hash.hexdigest()
    return md5_checksum


def identify_removed_snippets(
        old: Dict[str, List[str]],
        new: Dict[str, List[str]]
) -> List[str]:
    removed_files: List[str] = []
    for key, values in old.items():
        if key not in new:
            removed_files.append(key)
    return removed_files


def identify_changed_files(
        original: Dict[str, List[str]],
        new: Dict[str, List[str]]) -> List[str]:
    changed_files: List[str] = []
    for file_path, hashes in new.items():
        if file_path not in original:
            changed_files.append(file_path)
        else:
            original_hashes = original[file_path]
            if len(hashes) != len(original_hashes):
                changed_files.append(file_path)
            elif set(hashes) != set(original_hashes):
                changed_files.append(file_path)
    return changed_files


def create_dict_from_keys_and_values(keys: List[str], values: List[T]) -> Dict[str, List[T]]:
    assert (len(keys) == len(values))

    key_value = {}

    if len(keys) == 0:
        return key_value

    for i, value in enumerate(keys):
        if value in key_value:
            key_value[value].append(values[i])
        else:
            key_value[value] = [values[i]]
    return key_value


def split_string_preserve_suprimum_number_of_lines(input_string: str, chunk_size: int) -> List[str]:
    """
    Split an input string into smaller chunks while preserving as many lines as possible in each chunk.

    This function takes an input string and a chunk size as arguments and splits the string into smaller chunks
    such that the number of lines in each chunk is maximized while ensuring that the total characters in each
    chunk do not exceed the specified chunk size.
    """

    def loop(lines: List[str], chunks: List[str], chunk_size: int):
        if len(lines) == 0:
            return chunks

        current_line = lines[0]

        if len(lines[1:]) == 0:
            if len(current_line) < chunk_size:
                chunks.append(current_line)
                return loop(lines=[], chunks=chunks, chunk_size=chunk_size)
            else:
                new_chunk = current_line[0:chunk_size]
                remaining_chunked_line = current_line[chunk_size:]
                chunks.append(new_chunk)
                return loop([remaining_chunked_line] if len(remaining_chunked_line) != 0 else [], chunks,
                            chunk_size)
        for i in range(len(lines[1:])):
            next_line = lines[i + 1]
            remaining_lines = lines[i + 1:]
            if len(current_line) > chunk_size:
                new_chunks = current_line[0:chunk_size]
                remaining_chunked_line = current_line[chunk_size:]
                chunks.append(new_chunks)
                return loop([remaining_chunked_line] + remaining_lines, chunks, chunk_size)
            if len(current_line) + len(next_line) + 1 <= chunk_size:
                new_chunk = current_line + '\n' + next_line
                return loop([new_chunk] + lines[2:], chunks, chunk_size)
            if len(current_line) + len(next_line) + 1 > chunk_size:
                new_chunk = current_line
                chunks.append(new_chunk)
                return loop(remaining_lines, chunks, chunk_size)
            else:
                return chunks

        return chunks

    return loop(input_string.splitlines(), [], chunk_size)


def annotate_history_with_turns(history: List[str]) -> List[str]:
    """
    Annotate a conversation history with sender turns ("User" or "Bot").

    This function takes a list of messages representing a conversation history and
    annotates each message with metadata indicating whether it was sent by the "User"
    or the "Bot." It returns a list of messages with turn annotations.

    Args:
        history (List[str]): A list of strings representing the conversation history.

    Returns:
        List[str]: A list of strings with turn annotations.

    Example:
        >>> history = ["Hello", "How can I assist you?", "I have a question."]
        >>> result = annotate_history_with_turns(history)
        >>> print(result)
        ['1. User: Hello', '2. Bot: How can I assist you?', '3. User: I have a question.']
    """

    def turn_generator():
        while True:
            yield "User"
            yield "Bot"

    turn_gen = turn_generator()
    history_with_metadata = []

    for i, msg in enumerate(history, start=1):
        turn = next(turn_gen)
        history_with_metadata.append(f"{i}. {turn}: {msg}")

    return history_with_metadata


def annotate_history_with_turns_v2(history: List[Tuple[str, str]]) -> List[str]:
    history_with_metadata = []

    for i, msg in enumerate(history, start=1):
        history_with_metadata.append(f"{i}. {msg[0]}: {msg[1]}")

    return history_with_metadata


def measure_execution_time(func):
    def wrapper(*args, **kwargs):
        start_time = time.time()
        result = func(*args, **kwargs)
        end_time = time.time()
        duration = end_time - start_time
        print(f"{func.__name__} took {duration:.6f} seconds to run.")
        return result

    return wrapper


def async_measure_execution_time(func):
    @wraps(func)
    async def wrapper(*args, **kwargs):
        start_time = time.time()
        result = await func(*args, **kwargs)
        end_time = time.time()
        duration = end_time - start_time
        print(f"{func.__name__} took {duration:.6f} seconds to run.")
        return result

    return wrapper


def clone_repo(repo_url, depth=1) -> str:
    temp_folder: str = tempfile.mkdtemp()
    Repo.clone_from(repo_url, temp_folder, depth=depth)
    return temp_folder


def serialize_datetime(obj):
    """
    Serialize a datetime object into an ISO 8601 formatted string.

    Example:
        >>> dt = datetime(2023, 9, 12, 15, 30)
        >>> serialize_datetime(dt)
        '2023-09-12T15:30:00'
    """
    if isinstance(obj, datetime):
        return obj.isoformat()
    raise TypeError(f"Object of type {type(obj)} is not JSON serializable")
