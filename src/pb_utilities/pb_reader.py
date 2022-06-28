import struct
import ctypes

from io import BufferedIOBase
from typing import Tuple


def decode_varint(buffered_reader: BufferedIOBase, mask: int = 64) -> Tuple[int, int]:
    """
    Reads a base-128 varint from `buffered_reader` and returns the positive result of the
    varint.
    This assumes a `mask` of 64-bits for decoding typical "int32" and "int64" values,
    but should pass in a mask of 32-bits when decoding varints that denote lengths.
    """
    shift = 0
    result = 0
    bytes_read = 0
    while True:
        # Read 1-byte at a time and inspect the leading bit
        i = struct.unpack('B', buffered_reader.read(1))[0]
        bytes_read += 1

        # Prepare the result by ANDing the lower 7-bits and shifting for every byte read
        result |= (i & 0x7f) << shift
        shift += 7
        if not (i & 0x80):
            # AND the value to keep it within `mask` range
            result &= ((1 << mask) - 1)
            break

    return result, bytes_read


def decode_signed_varint(buffered_reader: BufferedIOBase, mask: int = 64) -> Tuple[int, int]:
    """
    Reads a base-128 varint from `buffered_reader` and returns the negative result of the
    varint.
    This assumes a `mask` of 64-bits for decoding typical "int32" and "int64" with negative values.
    """
    shift = 0
    result = 0
    bytes_read = 0
    while True:
        # Read 1-byte at a time and inspect the leading bit
        i = struct.unpack('B', buffered_reader.read(1))[0]
        bytes_read += 1

        # Prepare the result by ANDing the lower 7-bits and shifting for every byte read
        result |= (i & 0x7f) << shift
        shift += 7
        if not (i & 0x80):
            result &= (1 << mask) - 1
            if mask == 64:
                result = ctypes.c_int64(result).value
            else:
                result = ctypes.c_int32(result).value
            break

    return result, bytes_read
