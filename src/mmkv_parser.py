from io import BufferedIOBase, BytesIO
from pathlib import Path
from typing import Optional, List
from collections import defaultdict
from pb_utilities import pb_reader

import sys
import struct


class MMKVParser:
    """

    """

    def __init__(self):
        self.mmkv_file: Optional[BufferedIOBase] = None
        self.crc_file: Optional[BufferedIOBase] = None
        self.file_size: Optional[int] = None
        self.header_bytes: Optional[bytes] = None
        self.decoded_map: defaultdict[str, List[bytes]] = defaultdict(list)
        self.pos = 0

    def initialize(self, mmkv_abs_path_name: str, crc_abs_path_name: str = '') -> None:
        """
        Sets up the mmkv data file and optionally the CRC32 file.
        If crc filename is not given, will attempt to use append ".crc"

        :param mmkv_abs_path_name: absolute path filename string
        :param crc_abs_path_name: absolute path filename string
        :return: None
        """

        # Check if files exists w.r.t the "data" directory
        # mmkv_file_path = Path.cwd() / 'data' / mmkv_file_name
        mmkv_file_path: Path = Path(mmkv_abs_path_name)
        if not mmkv_file_path.exists():
            print(f'[+] The following directory does not exist - {mmkv_abs_path_name}')
            sys.exit(-1)

        # TODO - CRC32 check

        # Set up the MMKV File object
        self.mmkv_file = open(mmkv_file_path, 'rb')

        # Check file total size
        self.file_size = mmkv_file_path.stat().st_size
        print(f'[+] {mmkv_file_path.name} is {self.file_size} bytes')

        # Read in first 8 header bytes - [0:4] is total size, [4:8] is garbage bytes basically (0xffffff07)
        self.header_bytes = self.mmkv_file.read(8)
        self.pos += 8

        return None

    def get_db_size(self) -> int:
        """
        Returns the actual size of the MMKV database, that is, the size that the database knows about.

        :return: int size
        """
        return struct.unpack('<I', self.header_bytes[0:4])[0]

    def decode_into_map(self) -> defaultdict:
        """
        A best-effort approach on linearly parsing the `mmkv_file` BufferedReader
        and build up our `decoded_map`.

        :return: our built-up `decoded_map`
        """

        # Loop and read key-value pairs into `decoded_map`

        db_size = self.get_db_size()
        while self.pos < db_size:
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

