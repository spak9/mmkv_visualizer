from mmkv_parser import MMKVParser


if __name__ == "__main__":

    mmkv_parser = MMKVParser()
    mmkv_parser.initialize(mmkv_file_name='test_all_types')
    mmkv_parser._decode_into_map()