from io import BufferedIOBase, BytesIO
from pathlib import Path
from typing import Optional, List, Union, Tuple
from collections import defaultdict

import sys
import struct
import ctypes


"""
Global helper functions used for decoding 8-bit varints used within Google protocol buffers.
"""

def decode_unsigned_varint(buffered_base: BufferedIOBase, mask: int = 32) -> Tuple[int, int]:
    """
    Reads a base-128 varint from `buffered_base` and returns the unsigned result of the
    varint.
    This assumes a `mask` of 32-bits for decoding typical "int32" types. If you need to
    decode an "int64" type, use a 64-bit mask

    :param buffered_base: A file-like object that will incremently read byte-by-byte
    :param mask: an int that denotes either a 32 or 64-bit type.
    :return: A Tuple[int, int] of (varint_result, bytes_read) or (-1, -1) or 
    """
    shift = 0
    result = 0
    byte = buffered_base.read(1)
    bytes_read = 1

    # Check if `buffered_base` has valid bytes
    if not byte:
        print('[+] buffered_reader has no more bytes to read. Most likely trying to decode'
              ' data that is not a varint.')
        return -1, -1

    # Iterate through `buffered_base` and varint
    while True:
        i = struct.unpack('B', byte)[0]

        # Prepare the result by ANDing the lower 7-bits and shifting for every byte read
        result |= (i & 0x7f) << shift
        shift += 7
        if not (i & 0x80):
            if mask == 64:
                result = ctypes.c_uint64(result).value
            else:
                result = ctypes.c_uint32(result).value
        byte = buffered_base.read(1)
        bytes_read += 1
        if not byte:
            print('[+] buffered_reader has no more bytes to read. Most likely trying to decode'
                  ' data that is not a varint.')
            return -1, -1

    return result, bytes_read


def decode_signed_varint(buffered_base: BufferedIOBase, mask: int = 32) -> Tuple[int, int]:
    """
    Reads a base-128 varint from `buffered_base` and returns the signed result of the
    varint.
    This assumes a `mask` of 32-bits for decoding typical "int32" with negative values.
    If you need to decode an "int64" value, use a 64-bit mask.
    """
    shift = 0
    result = 0
    bytes_read = 0
    byte = buffered_base.read(1)
    bytes_read += 1

    # Check if `buffered_base` has valid bytes
    if not byte:
        print('[+] buffered_reader has no more bytes to read. Most likely trying to decode'
              ' data that is not a varint.')
        return -1, -1

    # Iterate through `buffered_base`
    while True:
        i = struct.unpack('B', byte)[0]

        # Prepare the result by ANDing the lower 7-bits and shifting for every byte read
        result |= (i & 0x7f) << shift
        shift += 7
        if not (i & 0x80):
            if mask == 64:
                result = ctypes.c_int64(result).value
            else:
                result = ctypes.c_int32(result).value
            break

        byte = buffered_base.read(1)
        bytes_read += 1
        if not byte:
            print('[+] buffered_reader has no more bytes to read. Most likely trying to decode'
                  ' data that is not a varint.')
            return -1, -1

    return result, bytes_read


class MMKVParser:
    """
    MMKVParser is a class that will read in an MMKV file and optionally a CRC32 file and will
    parse the database file into an in-memory dictionary. 
    The dictionary will be a simple key-value store, with UTF-8 keys and list values.

    The true power of this class comes from its type decoding API, enabling the 
    user to decode arbitrary bytes into a protobuf type.
    """

    def __init__(self):
        self.mmkv_file: Optional[BufferedIOBase] = None
        self.crc_file: Optional[BufferedIOBase] = None
        self.file_size: Optional[int] = None
        self.header_bytes: Optional[bytes] = None           # Should be 8 bytes after initialization
        self.decoded_map: defaultdict[str, List[bytes]] = defaultdict(list)
        self.pos = 0

    def initialize(self, mmkv_file: Union[str, bytes], crc_file: Union[str, bytes] = '') -> None:
        """
        Initializes the MMKV data file and optionally the CRC32 file.
        If either parameter is a string, then treat it as a file path, else if its bytes,
        treat it as the actual binary MMKV data.

        :param mmkv_file: absolute path filename string or bytes data
        :param crc_file: absolute path filename string or bytes data
        :return: None
        """

        # 1. `mmkv_file` is str
        if isinstance(mmkv_file, str):

            # Check if files exists w.r.t the "data" directory
            mmkv_file_path: Path = Path(mmkv_file)
            if not mmkv_file_path.exists():
                print(f'[+] The following directory does not exist - {mmkv_file}')
                sys.exit(-1)

            # Set up the MMKV File object
            self.mmkv_file = open(mmkv_file_path, 'rb')

        # 2. `mmkv_file` is bytes
        elif isinstance(mmkv_file, bytes):

            # Set up the MMKV File object
            self.mmkv_file = BytesIO(mmkv_file)

        # 3. `mmkv_file` is not correct type
        else:
            raise TypeError(f'mmkv_file is of type {type(mmkv_file)} - should be either str or bytes.')

        # Check file total size
        # self.file_size = mmkv_file_path.stat().st_size
        # print(f'[+] {mmkv_file_path.name} is {self.file_size} bytes')

        # Read in first 4 header bytes - [0:4] is total size
        self.header_bytes = self.mmkv_file.read(4)
        self.pos += 4

        # [4:X] is garbage bytes basically (0xffffff07)
        x, bytes_read = pb_reader.decode_varint(self.mmkv_file)
        self.pos += bytes_read

        return None

    def get_db_size(self) -> Optional[int]:
        """
        Returns the actual size of the MMKV database, that is, the size that the database knows about.

        :return: int size or None on error
        """
        if not self.header_bytes:
            raise TypeError('Header bytes is None. Please make sure to successfully initialize() db.')

        return struct.unpack('<I', self.header_bytes[0:4])[0]

    def decode_into_map(self) -> Optional[defaultdict]:
        """
        A best-effort approach on linearly parsing the `mmkv_file` BufferedReader
        and build up our `decoded_map`.

        :return: our built-up `decoded_map` or None on error
        """

        # Loop and read key-value pairs into `decoded_map`
        db_size = self.get_db_size()
        if db_size == 0:
            print('[+] MMKV datastore size is 0 - making db_size 256KB.')
            db_size = 256000


        while self.pos < db_size:

            # parse key
            key_length, bytes_read = pb_reader.decode_varint(self.mmkv_file, mask=32)
            if (key_length, bytes_read) == (-1, -1):
                print('[+] Ran out of bytes while decoding data into map - stopped parsing')
                break

            self.pos += bytes_read

            try:
                key_bytes = self.mmkv_file.read(key_length)
                key = key_bytes.decode(encoding='utf-8')

            except UnicodeDecodeError:
                print(f'[+] Error trying to UTF-8 decode {key_bytes} - returning decoded_map.')
                return self.decoded_map

            if key == '' and key_length == 0:
                break

            # parse value
            value_length, bytes_read = pb_reader.decode_varint(self.mmkv_file, mask=32)

            if (value_length, bytes_read) == (-1, -1):
                print('[+] Ran out of bytes while decoding data into map - stopped parsing')
                break

            # key-value pair was removed - value_length is 0
            elif (value_length, bytes_read) == (0, 1):
                print('[+] Value read was a null byte, therefore key-value pair was removed - no update and continuing')
                self.pos += bytes_read
                continue

            self.pos += bytes_read
            value = self.mmkv_file.read(value_length)  # interpretable

            # update map
            self.decoded_map[key].append(value)

        return self.decoded_map

    # Imitating the MMKV "get<Type>" API.
    # Assumes that the `value` bytes come directly from `decoded_map`

    def decode_as_bool(self, value: bytes) -> Optional[bool]:
        """
        Attempts to decode `value` as a boolean.

        :param value: protobuf-encoded bytes value
        :return: Returns the boolean result if possible, or None if not
        """
        if value == b'\x01':
            return True
        elif value == b'\x00':
            return False
        else:
            return None

    def decode_as_int32(self, value: bytes) -> int:
        """
        Decodes `value` as a signed 32-bit int.

        :param value: protobuf-encoded bytes value
        :return: Returns the signed 32-bit int result
        """
        return pb_reader.decode_signed_varint(BytesIO(value), mask=32)[0]

    def decode_as_int64(self, value: bytes) -> int:
        """
        Decodes `value` as a signed 64-bit int.

        :param value: protobuf-encoded bytes value
        :return: Returns the signed 64-bit int result
        """
        return pb_reader.decode_signed_varint(BytesIO(value), mask=64)[0]

    def decode_as_uint32(self, value: bytes) -> int:
        """
        Decodes `value` as an unsigned 32-bit int.

        :param value: protobuf-encoded bytes value
        :return: Returns the unsigned 32-bit int result
        """
        return pb_reader.decode_varint(BytesIO(value), mask=32)[0]

    def decode_as_uint64(self, value: bytes) -> int:
        """
        Decodes `value` as an unsigned 64-bit int.

        :param value: protobuf-encoded bytes value
        :return: Returns the unsigned 64-bit int result
        """
        return pb_reader.decode_varint(BytesIO(value), mask=64)[0]

    def decode_as_string(self, value: bytes) -> Optional[str]:
        """
        Attempts to decodes `value` as a UTF-8 string.
        Note: This assumes that `value` has the "erroneous" varint length wrapper

        :param value: protobuf-encoded bytes value
        :return: Returns the UTF-8 decoded string, or None if not possible
        """
        # Strip off the varint length delimiter bytes
        wrapper_bytes, wrapper_bytes_len = pb_reader.decode_varint(BytesIO(value), mask=32)

        try:
            if wrapper_bytes_len >= len(value):
                raise ValueError('[+] Wrapper bytes length when decoding string is longer than `value`.')
            value = value[wrapper_bytes_len:]
            return value.decode('utf-8')
        except:
            print(f'[+] Could not UTF-8 decode [{value}]')
            return None

    def decode_as_bytes(self, value: bytes) -> bytes:
        """
        Decodes `value` as bytes.
        Note: This assumes that `value` has the "erroneous" varint length wrapper

        :param value: protobuf-encoded bytes value
        :return: Returns the bytes
        """
        # Strip off the varint length delimiter bytes
        wrapper_bytes, wrapper_bytes_len = pb_reader.decode_varint(BytesIO(value), mask=32)
        value = value[wrapper_bytes_len:]
        return value

    def decode_as_float(self, value: bytes) -> float:
        """
        Decodes `value` as a double (8-bytes), which is a float type in Python.

        :param value: protobuf-encoded bytes value
        :return: Returns the float result
        """
        return struct.unpack('<d', value)[0]

    def reset(self) -> None:
        """
        Resets the instance variabls all back to original __init__ state

        :return: None
        """
        self.mmkv_file: Optional[BufferedIOBase] = None
        self.crc_file: Optional[BufferedIOBase] = None
        self.file_size: Optional[int] = None
        self.header_bytes: Optional[bytes] = None           # Should be 8 bytes after initialization
        self.decoded_map: defaultdict[str, List[bytes]] = defaultdict(list)
        self.pos = 0
        return None

