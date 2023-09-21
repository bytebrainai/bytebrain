from typing import List


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
