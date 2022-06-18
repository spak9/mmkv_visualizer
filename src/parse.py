from mmkv_parser import MMKVParser

if __name__ == "__main__":

    mmkv_parser = MMKVParser()
    mmkv_parser.initialize(mmkv_file_name='test_all_types')
    map = mmkv_parser._decode_into_map()

    for key, value in map.items():
        print(f'key: {key} - value: {value}')


    print(mmkv_parser.decode_as_int32(map.get('int32_positive_key')[0]))
    print(mmkv_parser.decode_as_uint32(map.get('int32_positive_key')[0]))

    print(mmkv_parser.decode_as_int32(map.get('int32_negative_key')[0]))
    print(mmkv_parser.decode_as_uint32(map.get('int32_negative_key')[0]))

    print(mmkv_parser.decode_as_int64(map.get('int64_positive_key')[0]))
    print(mmkv_parser.decode_as_uint64(map.get('int64_positive_key')[0]))

    print(mmkv_parser.decode_as_int64(map.get('int64_negative_key')[0]))
    print(mmkv_parser.decode_as_uint64(map.get('int64_negative_key')[0]))

    print(mmkv_parser.decode_as_bool(map.get('bool_true_key')[0]))
    print(mmkv_parser.decode_as_bool(map.get('bool_false_key')[0]))

    print(mmkv_parser.decode_as_string(map.get('string_key')[0]))
    print(mmkv_parser.decode_as_bytes(map.get('bytes_key')[0]))


