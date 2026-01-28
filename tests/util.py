import argparse
import hashlib
import logging
from collections import defaultdict, namedtuple
from pathlib import Path
from typing import Dict, List, Set

import mmkv
import sys
from importlib.metadata import version, PackageNotFoundError


"""
Small script to create basic test data, in attempt to visual and analyze all the basic 
types within MMKV (the protobuf wire types). 
"""

FileMetadata = namedtuple('FileMetadata', ['sha1', 'version', 'platform'])

def _create_data_all_types(dir_name):
    """
    Create basic test data with all types.
    No removes.

    :return:
    """
    logging.info("")
    # Check if test data exist, if so, delete, so we don't append
    test_data_file = Path.cwd() / dir_name / 'data_all_types'
    if test_data_file.exists():
        test_data_file.unlink()
    test_data_file = Path(f'{str(test_data_file)}.crc')
    if test_data_file.exists():
        test_data_file.unlink()

    # Create data within an MMKV file called "data_all_types")
    kv = mmkv.MMKV('data_all_types')

    # 1. int32 - MAX Positive Number
    kv.set((1 << 31) - 1, 'int32_pkey')

    # 2. int32 - MAX Negative Number (10-bytes needed)
    kv.set(-1 * (1 << 31), 'int32_nkey')

    # 3. int64 - MAX Positive Number
    kv.set((1 << 63) - 1, 'int64_pkey')

    # 4. int64 - MAX Negative Number(10-bytes needed)
    kv.set(-1 * (1 << 63), 'int64_nkey')

    # 5. bool - true
    kv.set(True, 'bool_true_key')

    # 6. bool - false
    kv.set(False, 'bool_false_key')

    # 7. string
    kv.set('steven pak', 'string_key')

    # 8. bytes
    kv.set(b'some bytes', 'bytes_key')

    # 9. float
    kv.set(3.14, 'float_key')


def _create_int32_keypair(dir_name):
    # Check if test data exist, if so, delete, so we don't append
    test_data_file = Path.cwd() / dir_name / 'data_int32_keypair'
    if test_data_file.exists():
        test_data_file.unlink()
    test_data_file = Path(f'{str(test_data_file)}.crc')
    if test_data_file.exists():
        test_data_file.unlink()

    kv = mmkv.MMKV('data_int32_keypair')
    kv.set(4444, 'key')
    print(kv.getInt('key'))


def _create_int32_keypair_with_remove(dir_name):
    # Check if test data exist, if so, delete, so we don't append
    test_data_file = Path.cwd() / dir_name / 'data_int32_keypair_with_remove'
    if test_data_file.exists():
        test_data_file.unlink()
    test_data_file = Path(f'{str(test_data_file)}.crc')
    if test_data_file.exists():
        test_data_file.unlink()

    kv = mmkv.MMKV('data_int32_keypair_with_remove')
    kv.set(4444, 'key')
    kv.remove('key')
    print(kv.getInt('key'))


def _create_string_keypair(dir_name):
    # Check if test data exist, if so, delete, so we don't append
    test_data_file = Path.cwd() / dir_name / 'data_string_keypair'
    if test_data_file.exists():
        test_data_file.unlink()
    test_data_file = Path(f'{str(test_data_file)}.crc')
    if test_data_file.exists():
        test_data_file.unlink()

    kv = mmkv.MMKV('data_string_keypair')
    kv.set('happy', 'key')
    print(kv.getString('key'))


# Testing update operations
def _create_int32_keypair_with_updates(dir_name):
    # Check if test data exist, if so, delete, so we don't append
    test_data_file = Path.cwd() / dir_name / 'data_int32_keypair_with_updates'
    if test_data_file.exists():
        test_data_file.unlink()
    test_data_file = Path(f'{str(test_data_file)}.crc')
    if test_data_file.exists():
        test_data_file.unlink()

    kv = mmkv.MMKV('data_int32_keypair_with_updates')
    kv.set(1, 'int_key')
    kv.set(10, 'int_key')
    kv.set(100, 'int_key')
    kv.set(1000, 'int_key')

def _create_string_keypair_with_updates(dir_name):
    # Check if test data exist, if so, delete, so we don't append
    test_data_file = Path.cwd() / dir_name / 'data_string_keypair_with_updates'
    if test_data_file.exists():
        test_data_file.unlink()
    test_data_file = Path(f'{str(test_data_file)}.crc')
    if test_data_file.exists():
        test_data_file.unlink()

    kv = mmkv.MMKV('data_string_keypair_with_updates')
    kv.set('steven', 'string_key')
    kv.set('Ø', 'string_key')
    kv.set('𠜎', 'string_key')
    kv.set('😁', 'string_key')

def _create_float_keypair_with_updates(dir_name):
    # Check if test data exist, if so, delete, so we don't append
    test_data_file = Path.cwd() / dir_name / 'data_float_keypair_with_updates'
    if test_data_file.exists():
        test_data_file.unlink()
    test_data_file = Path(f'{str(test_data_file)}.crc')
    if test_data_file.exists():
        test_data_file.unlink()

    kv = mmkv.MMKV('data_float_keypair_with_updates')
    kv.set(3.14, 'float_key')
    kv.set(3.141, 'float_key')
    kv.set(3.1414, 'float_key')
    kv.set(3.14141, 'float_key')


# Testing complex remove operations
def _create_string_keypair_with_remove(dir_name):
    # Check if test data exist, if so, delete, so we don't append
    test_data_file = Path.cwd() / dir_name / 'data_string_keypair_with_remove'
    if test_data_file.exists():
        test_data_file.unlink()
    test_data_file = Path(f'{str(test_data_file)}.crc')
    if test_data_file.exists():
        test_data_file.unlink()

    kv = mmkv.MMKV('data_string_keypair_with_remove')
    kv.getString('key')
    kv.set('old_1', 'key')
    kv.set('old_2', 'key')
    kv.set('old_3', 'key')
    kv.set('old_4', 'key')
    kv.set('old_5', 'key')
    kv.set('old_6', 'key')
    kv.remove('key')
    kv.set('value_3', 'key')
    kv.set('value_4', 'key')


def _create_data_encrypt(dir_name):
    # Check if test data exist, if so, delete, so we don't append
    test_data_file = Path.cwd() / dir_name / 'data_encrypt'
    if test_data_file.exists():
        test_data_file.unlink()
    test_data_file = Path(f'{str(test_data_file)}.crc')
    if test_data_file.exists():
        test_data_file.unlink()

    kv = mmkv.MMKV('data_encrypt', mmkv.MMKVMode.SingleProcess, "kindalongsecretkey")
    kv.set(True, 'bool_key')
    kv.set('steven', 'name')
    kv.set(3.14, 'float_key')
    kv.set(42, 'int_key')

def _create_data_all_types_with_auto_expiration(dir_name):
    """
    Create basic test data with all types.
    No removes.

    :return:
    """

    # Check if test data exist, if so, delete, so we don't append
    test_data_file = Path.cwd() / dir_name / 'data_all_types_with_auto_expiration'
    if test_data_file.exists():
        test_data_file.unlink()
    test_data_file = Path(f'{str(test_data_file)}.crc')
    if test_data_file.exists():
        test_data_file.unlink()

    # Create data within an MMKV file called "data_all_types")
    kv = mmkv.MMKV('data_all_types_with_auto_expiration')

    # Adding auto expiration in seconds
    if not hasattr(kv, "enableAutoKeyExpire"):
        print("MMKV Library version is likely below v1.3")
        test_data_file = Path('data_all_types_with_auto_expiration')
        if test_data_file.exists():
            test_data_file.unlink()
        test_data_file = Path('data_all_types_with_auto_expiration.crc')
        if test_data_file.exists():
            test_data_file.unlink()
        return

    # autokey expiration for a day
    kv.enableAutoKeyExpire(60 * 60 * 24)

    # 1. int32 - MAX Positive Number
    kv.set((1 << 31) - 1, 'int32_pkey')

    # 2. int32 - MAX Negative Number (10-bytes needed)
    kv.set(-1 * (1 << 31), 'int32_nkey')

    # 3. int64 - MAX Positive Number
    kv.set((1 << 63) - 1, 'int64_pkey')

    # 4. int64 - MAX Negative Number(10-bytes needed)
    kv.set(-1 * (1 << 63), 'int64_nkey')

    # 5. bool - true
    kv.set(True, 'bool_true_key')

    # 6. bool - false
    kv.set(False, 'bool_false_key')

    # 7. string
    kv.set('steven pak', 'string_key')

    # 8. bytes
    kv.set(b'some bytes', 'bytes_key')

    # 9. float
    kv.set(3.14, 'float_key')

def get_version(pkg_name: str) -> str:
    try:
        return version(pkg_name)
    except PackageNotFoundError:
        return "not installed"

def create_test_data(args):
    """
    Creates MMKV test for a given MMKV version and pipes all data into the 'dir_path' folder.
    """
    dir_name = args.directory_name
    print(f"Creating MMKV test data for MMKV version: {get_version('mmkv')} inside {dir_name}")

    mmkv.MMKV.initializeMMKV(f'{Path.cwd() / dir_name}')

    _create_data_all_types(dir_name)
    _create_int32_keypair(dir_name)
    _create_int32_keypair_with_remove(dir_name)
    _create_string_keypair(dir_name)
    _create_string_keypair_with_remove(dir_name)
    _create_int32_keypair_with_updates(dir_name)
    _create_string_keypair_with_updates(dir_name)
    _create_float_keypair_with_updates(dir_name)
    _create_data_encrypt(dir_name)
    _create_data_all_types_with_auto_expiration(dir_name)

def compare_hashes(args):
    """
    Function that will compare the hashes of the files with the same name.
    """

    # Iterate through all MMKV files and create mapping to compare all filenames with same name
    # e.g. { "data_all_types" : [HashAndVersion, HashAndVersion] }
    file_map: Dict[str, List[FileMetadata]] = defaultdict(list)

    for data_file in Path.cwd().rglob("*"):
        if data_file.is_file() and data_file.suffix == "" and data_file.name.startswith("data_"):
            with open(data_file, 'rb') as f:

                # FileMetadata = SHA1, version, platform
                # e.g. /tests/android/v1_2_16/data_all_types
                sha1 = hashlib.sha1(f.read()).hexdigest()
                version = data_file.parent.name
                platform = data_file.parent.parent.name

                file_map[data_file.name].append(FileMetadata(sha1, version, platform))

    # Iterate dict and compare hashes
    for filename, records in file_map.items():

        # A set to check whether there is a change in serialization among ANY versions
        unique_hash = set()
        unique_versions = set()
        versions = set()

        for record in records:
            unique_hash.add(record.sha1)
            unique_versions.add(record.version)
            versions.add(record.platform)
            print(f"Filename '{filename}: {record}")

        if len(unique_hash) == 1:
            print(f"✅ - '{filename}' not changed among {unique_versions} or platforms {versions} \n")
        else:
            print(f"❌ - '{filename}' has changed among {unique_versions} or platforms {versions} \n")

if __name__ == "__main__":

    parser = argparse.ArgumentParser(
        prog="MMKV Visualizer Utility"
    )
    subparsers = parser.add_subparsers(dest="command", required=True)

    # subcommand - create-data
    test_data_parser = subparsers.add_parser("create-data", help="Create various test data for the given MMKV version (e.g. v1.3) and push it to user-supplied directory. This is useful for generating versions of MMKV of different versions so we can check the serialization differences.")
    test_data_parser.add_argument('directory_name', type=str, help="Directory folder name that the test data will be written to. For example., 'version_2_0_0'")
    test_data_parser.set_defaults(func=create_test_data)

    # subcommand - create-data
    test_data_parser = subparsers.add_parser("compare-hashes",
                                             help="Will hash all files and compare all same file names to do a quick sanity check whether something has changed in versions")
    test_data_parser.set_defaults(func=compare_hashes)

    args = parser.parse_args()
    args.func(args)