from pathlib import Path

import mmkv

"""
Small script to create basic test data, in attempt to visual and analyze all the basic 
types within MMKV (the protobuf wire types). 
"""

def create_test_data():
    # Check if test data exist, if so, delete, so we don't append
    test_data_file = Path('test_all_types')
    if test_data_file.exists():
        test_data_file.unlink()

    # Create data within an MMKV file called "test_all_types")
    kv = mmkv.MMKV('test_all_types')

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


def create_test_updated_kv_pair():
    # Check if test data exist, if so, delete, so we don't append
    test_data_file = Path('test_updated_kv_pair')
    if test_data_file.exists():
        test_data_file.unlink()

    kv = mmkv.MMKV('test_updated_kv_pair')

    kv.set('value_1', 'some_key')
    kv.set('value_2', 'some_key')


if __name__ == "__main__":
    mmkv.MMKV.initializeMMKV('.')

    # Basic test data
    create_test_data()

    # testing updates of the same key, checking which value it gets
    create_test_updated_kv_pair()

