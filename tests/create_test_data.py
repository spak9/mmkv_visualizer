from pathlib import Path

import mmkv

"""
Small script to create basic test data, in attempt to visual and analyze all the basic 
types within MMKV (the protobuf wire types). 
"""

def create_data_all_types():
    """
    Create basic test data with all types.

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
        print('remove')
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


def create_string_keypair_with_remove():
    # Check if test data exist, if so, delete, so we don't append
    test_data_file = Path('data_string_keypair_with_remove')
    if test_data_file.exists():
        test_data_file.unlink()
    test_data_file = Path('data_string_keypair_with_remove.crc')
    if test_data_file.exists():
        test_data_file.unlink()

    kv = mmkv.MMKV('data_string_keypair_with_remove')
    kv.set('happy', 'key')
    kv.remove('key')
    print(kv.getString('key'))

if __name__ == "__main__":


    # Create our MMKV files inside this `data` directory
    mmkv.MMKV.initializeMMKV('.')

    create_data_all_types()

    create_int32_keypair()

    create_int32_keypair_with_remove()

    create_string_keypair()

    create_string_keypair_with_remove()

