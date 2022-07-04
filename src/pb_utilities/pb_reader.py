import struct
import ctypes

from io import BufferedIOBase
from typing import Tuple


def decode_varint(buffered_base: BufferedIOBase, mask: int = 64) -> Tuple[int, int]:
    """
    Reads a base-128 varint from `buffered_base` and returns the positive result of the
    varint.
    This assumes a `mask` of 64-bits for decoding typical "int32" and "int64" values,
    but should pass in a mask of 32-bits when decoding varints that denote lengths.
    """
    shift = 0
    result = 0
    bytes_read = 0
    byte = buffered_base.read(1)
    bytes_read += 1

    # Check if `buffered_base` has valid bytes
    if not byte:
        print('[+] buffered_reader has no more bytes to read.')
        return -1, -1

    # Iterate through `buffered_base` and varint
    while True:
        i = struct.unpack('B', byte)[0]

        # Prepare the result by ANDing the lower 7-bits and shifting for every byte read
        result |= (i & 0x7f) << shift
        shift += 7
        if not (i & 0x80):
            # AND the value to keep it within `mask` range
            result &= ((1 << mask) - 1)
            break

        byte = buffered_base.read(1)
        bytes_read += 1

    return result, bytes_read


def decode_signed_varint(buffered_base: BufferedIOBase, mask: int = 64) -> Tuple[int, int]:
    """
    Reads a base-128 varint from `buffered_base` and returns the negative result of the
    varint.
    This assumes a `mask` of 64-bits for decoding typical "int32" and "int64" with negative values.
    """
    shift = 0
    result = 0
    bytes_read = 0
    byte = buffered_base.read(1)
    bytes_read += 1

    # Check if `buffered_base` has valid bytes
    if not byte:
        print('[+] buffered_reader has no more bytes to read.')
        return -1, -1

    # Iterate through `buffered_base` and varint
    while True:
        i = struct.unpack('B', byte)[0]

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

        byte = buffered_base.read(1)
        bytes_read += 1

    return result, bytes_read
