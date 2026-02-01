import unittest
from pathlib import Path

from frontend.public.mmkv_parser import MMKVParser
from test_parser import ANDROID_V1_2_16_PATH
import argparse

from tests.test_parser import PYTHON_V1_2_13_PATH

"""
A basic script to exercise the 'MMKVParser' class. The `MMKVParser` class lives within the `frontend/public/` package,
which houses assets publicly available to the Svelte-and-pyodide web app.

This script is used to exercise the MMKVParser completely within a Python context.
"""
if __name__ == "__main__":

    parser = argparse.ArgumentParser(description="Parse MMKV files")
    parser.add_argument("mmkv_file", help="absolute path to input MMKV file")
    parser.add_argument("--crc_file", help="absolute path to optional MMKV CRC file")

    args = parser.parse_args()

    mmkv_file_path = Path(args.mmkv_file)
    if args.crc_file:
        crc_file = Path(args.crc_file)

    # with open(mmkv_file_path, 'rb') as f:
    #     mmkv_parser = MMKVParser(mmkv_file_data=f)
    #     map = mmkv_parser.decode_into_map()
    #     MMKVParser.decode_as_bool(map['bool_false_key'][0])
    #     print(map)

    with open(ANDROID_V1_2_16_PATH / 'data_encrypt', 'rb') as f, open(PYTHON_V1_2_13_PATH / 'data_encrypt.crc',
                                                                      'rb') as c:
        mmkv_parser = MMKVParser(mmkv_file_data=f, crc_file_data=c)
        mmkv_parser.decrypt_and_reconstruct(key=b'kindalongsecretkey')
        mmkv_map = mmkv_parser.decode_into_map()

    unittest.main()