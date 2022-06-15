from mmkv_parser import MMKVParser


if __name__ == "__main__":

    mmkv_parser = MMKVParser()
    # mmkv_parser.initialize(mmkv_file_name='test_data')
    mmkv_parser.initialize(mmkv_file_name='test_varint')
    mmkv_parser._decode_into_map()