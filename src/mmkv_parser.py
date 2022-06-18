from io import BufferedReader, BytesIO
from pathlib import Path
from typing import Optional, List
from collections import defaultdict
from pb_utilities import pb_reader

import sys


class MMKVParser:
    """

    """

    def __init__(self):
        self.mmkv_file: Optional[BufferedReader] = None
        self.crc_file: Optional[BufferedReader] = None
        self.decoded_map: defaultdict[str, List[bytes]] = defaultdict(list)
        self.pos = 0

    def initialize(self, mmkv_file_name: str, crc_file_name: str = ''):
        """
        Sets up the mmkv data file and optionally the CRC32 file.
        If crc filename is not given, will attempt to use append ".crc"

        :param mmkv_file_name: filename string
        :param crc_file_name: filename string
        :return: None
        """

        # Check if files exists w.r.t the "data" directory
        mmkv_file_path = Path.cwd() / 'data' / mmkv_file_name
        if not mmkv_file_path.exists():
            print(f'[+] The following directory does not exist - {mmkv_file_name}')
            sys.exit(-1)

        # TODO - CRC32 check

        # Set up the MMKV File object
        self.mmkv_file = open(mmkv_file_path, 'rb')

    def decode_into_map(self) -> defaultdict:
        """
        A best-effort approach on linearly parsing the `mmkv_file` BufferedReader
        and build up our `decoded_map`.
        :return: our built-up `decoded_map`
        """

        # Skip first 8-bytes of the metadata
        self.mmkv_file.read(8)
        self.pos += 8

        # Loop and read key-value pairs into `decoded_map`
        while self.mmkv_file.peek():
            # parse key
            key_length, self.pos = pb_reader.decode_varint(self.mmkv_file, self.pos, mask=32)
            key = self.mmkv_file.read(key_length).decode(encoding='utf-8')

            if key == '' and key_length == 0:
                break

            # parse value
            value_length, self.pos = pb_reader.decode_varint(self.mmkv_file, self.pos, mask=32)
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
        return pb_reader.decode_signed_varint(BytesIO(value), 0, mask=32)[0]

    def decode_as_int64(self, value: bytes) -> int:
        """
        Decodes `value` as a signed 64-bit int.

        :param value: protobuf-encoded bytes value
        :return: Returns the signed 64-bit int result
        """
        return pb_reader.decode_signed_varint(BytesIO(value), 0, mask=64)[0]

    def decode_as_uint32(self, value: bytes) -> int:
        """
        Decodes `value` as an unsigned 32-bit int.

        :param value: protobuf-encoded bytes value
        :return: Returns the unsigned 32-bit int result
        """
        return pb_reader.decode_varint(BytesIO(value), 0, mask=32)[0]

    def decode_as_uint64(self, value: bytes) -> int:
        """
        Decodes `value` as an unsigned 64-bit int.

        :param value: protobuf-encoded bytes value
        :return: Returns the unsigned 64-bit int result
        """
        return pb_reader.decode_varint(BytesIO(value), 0, mask=64)[0]

    def decode_as_string(self, value: bytes) -> Optional[str]:
        """
        Attempts to decodes `value` as a UTF-8 string.
        Note: This assumes that `value` has the "erroneous" varint length wrapper

        :param value: protobuf-encoded bytes value
        :return: Returns the UTF-8 decoded string, or None if not possible
        """
        # Strip off the varint length delimiter bytes
        wrapper_bytes, wrapper_bytes_len = pb_reader.decode_varint(BytesIO(value), 0, mask=32)
        value = value[wrapper_bytes_len:]
        try:
            return value.decode('utf-8')
        except:
            print(f'Could not UTF-8 decode [{value}]')
            return None

    def decode_as_bytes(self, value: bytes) -> bytes:
        """
        Decodes `value` as bytes.
        Note: This assumes that `value` has the "erroneous" varint length wrapper

        :param value: protobuf-encoded bytes value
        :return: Returns the bytes
        """
        # Strip off the varint length delimiter bytes
        wrapper_bytes, wrapper_bytes_len = pb_reader.decode_varint(BytesIO(value), 0, mask=32)
        value = value[wrapper_bytes_len:]
        return value

    # TODO - floats

