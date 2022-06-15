from io import BufferedReader
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
        self.decoded_map: Dict[str, defaultdict[List[bytes]]] = {}
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

        pb_reader.decode_varint(self.mmkv_file, self.pos)

