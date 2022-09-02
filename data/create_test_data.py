from pathlib import Path

import mmkv

"""
Small script to create basic test data, in attempt to visual and analyze all the basic 
types within MMKV (the protobuf wire types). 
"""

def create_basic_data():
    """
    Create basic test data with all types.

    :return:
    """
    # Check if test data exist, if so, delete, so we don't append
    test_data_file = Path('create_basic_data')
    if test_data_file.exists():
        test_data_file.unlink()

    # Create data within an MMKV file called "test_all_types")
    kv = mmkv.MMKV('create_basic_data')

    # 1. int32 - positive
    kv.set((1 << 31) - 1, 'int32_positive_key')

    # 2. int32 - negative (10-bytes needed)
    kv.set(-1 * (1 << 31), 'int32_negative_key')

    # 3. int64 - positive
    kv.set((1 << 63) - 1, 'int64_positive_key')

    # 4. int64 - negative (10-bytes needed)
    kv.set(-1 * (1 << 63), 'int64_negative_key')

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


def create_overwritten_kv_data():
    """
    Create test data with "overwritten" key-value pair

    :return:
    """
    # Check if test data exist, if so, delete, so we don't append
    test_data_file = Path('create_overwritten_kv_data')
    if test_data_file.exists():
        test_data_file.unlink()

    kv = mmkv.MMKV('create_overwritten_kv_data')

    for i in range(30):
        for y in range(12):
            kv.set(f'value_{y}', f'key_{i}')


def create_encrypted_data():
    """
    Create encrypted test data with `my_key` enc key.

    :return:
    """
    # Check if test data exist, if so, delete, so we don't append
    test_data_file = Path('create_encrypted_data')
    if test_data_file.exists():
        test_data_file.unlink()

    kv = mmkv.MMKV('create_encrypted_data', mmkv.MMKVMode.SingleProcess, 'my_key')
    kv.set('some_string', 'string_key')

def create_test_1():

    kv = mmkv.MMKV('create_blah')
    kv.set('some_string', 'string_key')
    print(f'set string_key to: {kv.getString("string_key")}')

    kv.remove('string_key')
    print(f'removed string_key: {kv.getString("string_key")}')

    



if __name__ == "__main__":
    try:

        mmkv.MMKV.initializeMMKV('.')

        create_basic_data()

        create_overwritten_kv_data()

        create_encrypted_data()

        create_test_1()

    except ModuleNotFoundError as e:
        print(f'[+] Please make sure to have the "mmkv" python package installed from '
                'Tencent MMKV Github Repo. Not available on pypi.')
