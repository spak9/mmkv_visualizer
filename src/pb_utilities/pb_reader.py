from io import BufferedReader
from typing import Tuple


def decode_varint(buffered_reader: BufferedReader, pos: int) -> Tuple[int, int]:
    """Read a varint from `stream`"""
    shift = 0
    result = 0
    while True:
        i = int.from_bytes(buffered_reader.read(1), 'little')
        pos += 1
        result |= (i & 0x7f) << shift
        shift += 7
        if not (i & 0x80):
            break

    return result, pos
