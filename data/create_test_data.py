import mmkv


if __name__ == "__main__":
    mmkv.MMKV.initializeMMKV('.')

    # 1. int32 (1234)
    kv = mmkv.MMKV('int32')
    kv.set(1234, 'test_key')