from pathlib import Path

import mmkv
import sys

"""
Small script to create basic test data, in attempt to visual and analyze all the basic 
types within MMKV (the protobuf wire types). 
"""

def create_data_all_types():
    """
    Create basic test data with all types.
    No removes.

    :return:
    """

    # Check if test data exist, if so, delete, so we don't append
    test_data_file = Path('data_all_types')
    if test_data_file.exists():
        test_data_file.unlink()
    test_data_file = Path('data_all_types.crc')
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


def create_int32_keypair():
    # Check if test data exist, if so, delete, so we don't append
    test_data_file = Path('data_int32_keypair')
    if test_data_file.exists():
        test_data_file.unlink()
    test_data_file = Path('data_int32_keypair.crc')
    if test_data_file.exists():
        test_data_file.unlink()

    kv = mmkv.MMKV('data_int32_keypair')
    kv.set(4444, 'key')
    print(kv.getInt('key'))


def create_int32_keypair_with_remove():
    # Check if test data exist, if so, delete, so we don't append
    test_data_file = Path('data_int32_keypair_with_remove')
    if test_data_file.exists():
        test_data_file.unlink()
    test_data_file = Path('data_int32_keypair_with_remove.crc')
    if test_data_file.exists():
        test_data_file.unlink()

    kv = mmkv.MMKV('data_int32_keypair_with_remove')
    kv.set(4444, 'key')
    kv.remove('key')
    print(kv.getInt('key'))


def create_string_keypair():
    # Check if test data exist, if so, delete, so we don't append
    test_data_file = Path('data_string_keypair')
    if test_data_file.exists():
        test_data_file.unlink()
    test_data_file = Path('data_string_keypair.crc')
    if test_data_file.exists():
        test_data_file.unlink()

    kv = mmkv.MMKV('data_string_keypair')
    kv.set('happy', 'key')
    print(kv.getString('key'))


# Testing update operations
def create_int32_keypair_with_updates():
    # Check if test data exist, if so, delete, so we don't append
    test_data_file = Path('data_int32_keypair_with_updates')
    if test_data_file.exists():
        test_data_file.unlink()
    test_data_file = Path('data_int32_keypair_with_updates.crc')
    if test_data_file.exists():
        test_data_file.unlink()

    kv = mmkv.MMKV('data_int32_keypair_with_updates')
    kv.set(1, 'int_key')
    kv.set(10, 'int_key')
    kv.set(100, 'int_key')
    kv.set(1000, 'int_key')

def create_string_keypair_with_updates():
    # Check if test data exist, if so, delete, so we don't append
    test_data_file = Path('data_string_keypair_with_updates')
    if test_data_file.exists():
        test_data_file.unlink()
    test_data_file = Path('data_string_keypair_with_updates.crc')
    if test_data_file.exists():
        test_data_file.unlink()

    kv = mmkv.MMKV('data_string_keypair_with_updates')
    kv.set('steven', 'string_key')
    kv.set('Ø', 'string_key')
    kv.set('𠜎', 'string_key')
    kv.set('😁', 'string_key')

def create_float_keypair_with_updates():
    # Check if test data exist, if so, delete, so we don't append
    test_data_file = Path('data_float_keypair_with_updates')
    if test_data_file.exists():
        test_data_file.unlink()
    test_data_file = Path('data_float_keypair_with_updates.crc')
    if test_data_file.exists():
        test_data_file.unlink()

    kv = mmkv.MMKV('data_float_keypair_with_updates')
    kv.set(3.14, 'float_key')
    kv.set(3.141, 'float_key')
    kv.set(3.1414, 'float_key')
    kv.set(3.14141, 'float_key')


# Testing complex remove operations
def create_string_keypair_with_remove():
    # Check if test data exist, if so, delete, so we don't append
    test_data_file = Path('data_string_keypair_with_remove')
    if test_data_file.exists():
        test_data_file.unlink()
    test_data_file = Path('data_string_keypair_with_remove.crc')
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


def create_data_encrypt():
    # Check if test data exist, if so, delete, so we don't append
    test_data_file = Path('data_encrypt')
    if test_data_file.exists():
        test_data_file.unlink()
    test_data_file = Path('data_encrypt.crc')
    if test_data_file.exists():
        test_data_file.unlink()

    kv = mmkv.MMKV('data_encrypt', mmkv.MMKVMode.SingleProcess, "kindalongsecretkey")
    kv.set(True, 'bool_key')
    kv.set('steven', 'name')
    kv.set(3.14, 'float_key')
    kv.set(42, 'int_key')


if __name__ == "__main__":


    # Create our MMKV files inside whatever directory the user wants
    # eg. "version_1_2_13"
    
    if len(sys.argv) != 2:
        print('Please enter a directory to pipe the files to.\neg: python create_test_data.py version_1_1\n')
        sys.exit(1)

    else:
        dir_name = sys.argv[1]
        print(f'Creating test data in "{dir_name}"')

    mmkv.MMKV.initializeMMKV(f'{dir_name}')

    create_data_all_types()

    create_int32_keypair()

    create_int32_keypair_with_remove()

    create_string_keypair()

    create_string_keypair_with_remove()

    create_int32_keypair_with_updates()

    create_string_keypair_with_updates()

    create_float_keypair_with_updates()

    create_data_encrypt()

