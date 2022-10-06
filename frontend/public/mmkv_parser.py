from io import BufferedIOBase, BytesIO
from pathlib import Path
from typing import Optional, List, Union, Tuple, DefaultDict
from collections import defaultdict

import sys
import struct
import ctypes

"""
Global helper functions used for decoding 8-bit varints used within Google protocol buffers.
These helper functions will be the underlying infrastructure for the the `MMKVParser` public API
for decoding various bytes.  
"""


def decode_unsigned_varint(buffered_base: BufferedIOBase, mask: int = 32) -> Tuple[int, int]:
    """
    Reads a base-128 varint from `buffered_base` and returns the unsigned result of the
    varint.
    This assumes a `mask` of 32-bits for decoding typical "int32" types. If you need to
    decode an "int64" type, use a 64-bit mask.
    Note: this should always be used for reading varints denoting lengths

    :param buffered_base: A file-like object that will incremently read byte-by-byte
    :param mask: an int that denotes either a 32 or 64-bit type.
    :return: A Tuple[int, int] of (varint_result, bytes_read) or (-1, -1) for invalid reading
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
                # Result is casted via a "uint"
                result = ctypes.c_uint64(result).value
            else:
                result = ctypes.c_uint32(result).value
            break

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

    :param buffered_base: A file-like object that will incremently read byte-by-byte
    :param mask: an int that denotes either a 32 or 64-bit type.
    :return: A Tuple[int, int] of (varint_result, bytes_read) or (-1, -1) for invalid reading
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
                # Result is casted via a "uint"
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

    def __init__(self, mmkv_file_data: Union[str, BufferedIOBase], crc_file_data: Union[str, BufferedIOBase, None] = None):
        """
        Initializes an `MMKVParser` instance with the required `mmkv_file_data`, which must be a `str` type used
        for Pyodide-based Public API (a hexstring), or a Python `BufferedIOBase`, which should represent a natively 
        prepared stream of data.

        :param mmkv_file_data: A hexstring of mmkv data from Pyodide-based viewer, or native Python BufferedIOBase
        :param crc_file_data: Same as mmkv_file_data, but defaults to None because the CRC check will be optional
        """

        # Handle cases with `mmkv_file_data`:
        # 1. mmkv_file_data is str
        if isinstance(mmkv_file_data, str):

            # Check that it's a valid hexstring
            int(mmkv_file_data, 16)

            # Convert hexstring into a BufferedIOBase 
            mmkv_file_data = BytesIO(bytes.fromhex(mmkv_file_data))

        # 2. mmkv_file_data is BufferedIOBase
        elif isinstance(mmkv_file_data, BufferedIOBase):
            pass

        # 3. mmkv_file_data is neither
        else:
            raise TypeError(f'mmkv_file_data is of type {type(mmkv_file_data)} - should be either hex str or bytes.')

        # Handle cases with `crc_file_data`:
        # 1. crc_file_data is str
        if isinstance(crc_file_data, str):

            # Check that it's a valid hexstring
            int(crc_file_data, 16)

            # Convert hexstring into a BufferedIOBase 
            crc_file_data = BytesIO(bytes.fromhex(crc_file_data))

        # 2. crc_file_data is BufferedIOBase
        elif isinstance(crc_file_data, BufferedIOBase):
            pass

        # 3. crc_file_data is None
        else:
            pass


        # Initialize our files
        self.mmkv_file: BufferedIOBase = mmkv_file_data
        self.crc_file: Optional[BufferedIOBase] = crc_file_data
        self.pos: int = 0
        self.decoded_map: DefaultDict[str, List[bytes]] = defaultdict(list)

        # Read in first 4 header bytes - [0:4] is total size
        self.header_bytes: bytes = self.mmkv_file.read(4)
        if len(self.header_bytes) != 4:
            raise ValueError('[+] Error while reading mmkv_file. Header bytes was not 4 bytes.')
        self.pos += 4
 
        # TODO: find out the purpose of the varint in [4:x] position
        # [4:X] is garbage bytes basically (0xffffff07) or is another varint
        x, bytes_read = decode_unsigned_varint(self.mmkv_file)
        if (x, bytes_read) == (-1, -1):
            raise ValueError('[+] Error while decoding the [4:X] bytes of the mmkv_file.')

        self.pos += bytes_read


    def get_db_size(self) -> int:
        """
        Returns the actual size known to the MMKV API for querying data. This includes older
        logged data that the actual MMKV API does not have the ability to query. 
        Note: It is possible the size may be 0, however it's not known as to why MMKV does this.
        Will account for this wherever used. 

        :return: int size
        """

        # Length is stored as a little-endian int32
        size = struct.unpack('<I', self.header_bytes[0:4])[0]
        if isinstance(size, int):
            print(f'[+] get_db_size() - DB size is {size}.')
            return size
        else:
            raise TypeError(f'[+] Error while unpacking header bytes. Received {type(size)}')


    def decode_into_map(self) -> DefaultDict[str, List[bytes]]:
        """
        A best-effort approach on linearly parsing the `mmkv_file` stream and building up 
        dictionary of keys mapped to a list of bytes values, with the most recent value being at the lowest index.

        :return: a built up defaultdict, which is also an instance variable
        """

        # Get size of database
        db_size = self.get_db_size()

        # Iterate through the database and build-up our dictionary
        while self.pos < db_size:

            # Parse the key length 
            key_length, bytes_read = decode_unsigned_varint(self.mmkv_file, mask=32)

            # Check if parsing key length failed
            if (key_length, bytes_read) == (-1, -1):
                print('[+] decode_into_map() - cannot parse key length, breaking.')
                break
            if key_length == 0:
                print('[+] decode_into_map() - key length is 0, breaking')
                break

            self.pos += bytes_read

            try:
                # Read the key (always UTF-8 String)
                key_bytes = self.mmkv_file.read(key_length)
                key = key_bytes.decode(encoding='utf-8')
                self.pos += key_length

            except UnicodeDecodeError:
                print(f'[+] decode_into_map() - Error trying to decode {key_bytes!r}. breaking')
                break

            # Parse the value length
            value_length, bytes_read = decode_unsigned_varint(self.mmkv_file, mask=32)
            self.pos += bytes_read

            # Check if parsing value length failed
            if (value_length, bytes_read) == (-1, -1):
                print('[+] decode_into_map() - cannot parse value length, breaking.')
                break

            # IMPORTANT - a key-value pair that was removed via the MMKV API will have a 
            # valid key, but will be followed by a null byte, signifying that the key-value pair 
            # was removed.
            # eg. <key length> | <key> | \x00
            if value_length == 0:
                print('[+] decode_into_map() - value length is 0, KV pair was removed. Continuing')
                self.pos += bytes_read
                continue

            # Parse the value (bytes which will then be iterpretable, since there's type tied to data)
            value_bytes = self.mmkv_file.read(value_length)
            self.pos += value_length

            # Update our decoded_map
            self.decoded_map[key].insert(0, value_bytes)

        return self.decoded_map


    def decode_as_bool(self, value: Union[str, bytes]) -> Optional[bool]:
        """
        Attempts to decode `value` as a boolean.

        :param value: hexstring for Pyodide-based API or protobuf-encoded bytes value
        :return: Returns the boolean result if possible, or None if not
        """
        if isinstance(value, str):
            value = bytes.fromhex(value)
        if value == b'\x01':
            return True
        elif value == b'\x00':
            return False
        else:
            print(f'[+] Could not bool decode {value!r}')
            return None

    def decode_as_int32(self, value: Union[str, bytes]) -> int:
        """
        Decodes `value` as a signed 32-bit int.

        :param value: hexstring for Pyodide-based API or protobuf-encoded bytes value
        :return: Returns the signed 32-bit int result
        """
        if isinstance(value, str):
            value = bytes.fromhex(value)
        return decode_signed_varint(BytesIO(value), mask=32)[0]

    def decode_as_int64(self, value: Union[str, bytes]) -> int:
        """
        Decodes `value` as a signed 64-bit int.

        :param value: hexstring for Pyodide-based API or protobuf-encoded bytes value
        :return: Returns the signed 64-bit int result
        """
        if isinstance(value, str):
            value = bytes.fromhex(value)
        return decode_signed_varint(BytesIO(value), mask=64)[0]

    def decode_as_uint32(self, value: Union[str, bytes]) -> int:
        """
        Decodes `value` as an unsigned 32-bit int.

        :param value: hexstring for Pyodide-based API or protobuf-encoded bytes value
        :return: Returns the unsigned 32-bit int result
        """
        if isinstance(value, str):
            value = bytes.fromhex(value)
        return decode_unsigned_varint(BytesIO(value), mask=32)[0]

    def decode_as_uint64(self, value: Union[str, bytes]) -> int:
        """
        Decodes `value` as an unsigned 64-bit int.

        :param value: hexstring for Pyodide-based API or protobuf-encoded bytes value
        :return: Returns the unsigned 64-bit int result
        """
        if isinstance(value, str):
            value = bytes.fromhex(value)
        return decode_unsigned_varint(BytesIO(value), mask=64)[0]

    def decode_as_string(self, value: Union[str, bytes]) -> Optional[str]:
        """
        Attempts to decodes `value` as a UTF-8 string.
        Note: This assumes that `value` has the "erroneous" varint length wrapper

        :param value: hexstring for Pyodide-based API or protobuf-encoded bytes value
        :return: Returns the UTF-8 decoded string, or None if not possible
        """
        if isinstance(value, str):
            value = bytes.fromhex(value)

        # Strip off the varint length delimiter bytes
        wrapper_bytes, wrapper_bytes_len = decode_unsigned_varint(BytesIO(value), mask=32)

        try:
            if wrapper_bytes_len >= len(value):
                raise ValueError('[+] Wrapper bytes length when decoding string is longer than `value`.')
            value = value[wrapper_bytes_len:]
            return value.decode('utf-8')
        except:
            print(f'[+] Could not UTF-8 decode {value!r}')
            return None

    def decode_as_bytes(self, value: Union[str, bytes]) -> bytes:
        """
        Decodes `value` as bytes.
        Note: This assumes that `value` has the "erroneous" varint length wrapper

        :param value: hexstring for Pyodide-based API or protobuf-encoded bytes value
        :return: Returns the bytes
        """
        if isinstance(value, str):
            value = bytes.fromhex(value)

        # Strip off the varint length delimiter bytes
        wrapper_bytes, wrapper_bytes_len = decode_unsigned_varint(BytesIO(value), mask=32)
        value = value[wrapper_bytes_len:]
        return value

    def decode_as_float(self, value: Union[str, bytes]) -> Optional[float]:
        """
        Decodes `value` as a double (8-bytes), which is a float type in Python.

        :param value: hexstring for Pyodide-based API or protobuf-encoded bytes value
        :return: Returns the float result, or None on surely invalid `value`
        """
        if isinstance(value, str):
            value = bytes.fromhex(value)

        if len(value) != 8:
            print(f'[+] Could not float decode {value} due to length')

        return struct.unpack('<d', value)[0]

    # def reset(self) -> None:
    #     """
    #     Resets the instance variables all back to original __init__ state

    #     :return: None
    #     """
    #     self.mmkv_file: Optional[BufferedIOBase] = None
    #     self.crc_file: Optional[BufferedIOBase] = None
    #     self.file_size: Optional[int] = None
    #     self.header_bytes: Optional[bytes] = None  # Should be 8 bytes after initialization
    #     self.decoded_map: defaultdict[str, List[bytes]] = defaultdict(list)
    #     self.pos = 0
    #     return None
