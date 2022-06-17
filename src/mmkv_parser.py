from io import BufferedReader, BytesIO
from pathlib import Path
from typing import Optional, Dict, List
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

    def _decode_into_map(self):
        """
        A best-effort approach on linearly parsing the `mmkv_file` BufferedReader
        and build up our `decoded_map`
        :return:
        """

        # Skip first 8-bytes of the metadata
        self.mmkv_file.read(8)
        self.pos += 8

        # Loop and read key-value pairs into `decoded_map`
        while self.mmkv_file.peek():
            # parse key
            key_length, self.pos = pb_reader.decode_varint(self.mmkv_file, self.pos, mask=32)
            key = self.mmkv_file.read(key_length).decode(encoding='utf-8')

            # parse value
            value_length, self.pos = pb_reader.decode_varint(self.mmkv_file, self.pos, mask=32)
            value = self.mmkv_file.read(value_length)   # interpretable

            # update map
            self.decoded_map[key].append(value)



