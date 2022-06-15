from io import BufferedReader
from pathlib import Path
from typing import Optional


class MMKVParser:
    """

    """

    def __init__(self):
        self.mmkv_file: Optional[BufferedReader] = None
        self.crc_file: Optional[BufferedReader] = None
        self.decoded_data: Optional[BufferedReader] = None

    def initialize(self, mmkv_file_name: str, crc_file_name: str = ''):
        """
        Sets up the mmkv data file and optionally the CRC32 file.
        If crc filename is not given, will attempt to use append ".crc"

        :param mmkv_file_name: filename string
        :param crc_file_name: filename string
        :return: None
        """
        # Check if files exists
        mmkv_file_path = Path.cwd() / 'data' / mmkv_file_name
        if not mmkv_file_path.exists():
            print(f'[+] The following directory does not exist - {mmkv_file_name}')
            exit(1)

        # TODO - CRC32 check

        # Set up the MMKV File object
        self.mmkv_file = open(mmkv_file_path, 'rb')


    def decode_mmkv_data(self):
        """
        A best-effort approach on
        :return:
        """



