from mmkv_parser import MMKVParser
from pathlib import Path


if __name__ == "__main__":

    mmkv_parser = MMKVParser()
    # data_path = Path(__file__).parents[1].resolve() / 'data' / 'create_basic_data'
    data_path = Path(__file__).resolve().parent.parent / 'data' / 'create_basic_data'
    print(data_path)
    mmkv_parser.initialize(mmkv_file=str(data_path))
    map = mmkv_parser.decode_into_map()

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

    print(mmkv_parser.decode_as_float(map.get('float_key')[0]))

    values = map.values()
    for value in values:
        print(str(value[0]))

    value = mmkv_parser.decode_as_string(bytes.fromhex('FFFFFFFF07'))
    print(value)





