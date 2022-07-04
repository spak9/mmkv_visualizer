from io import BytesIO

from mmkv_parser import MMKVParser
from pathlib import Path
from pb_utilities import pb_reader

if __name__ == "__main__":

    mmkv_parser = MMKVParser()
    data_path = Path(__file__).parent.parent / 'data' / 'create_basic_data'
    mmkv_parser.initialize(mmkv_file_name=str(data_path))
    map = mmkv_parser.decode_into_map()

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

    print(mmkv_parser.decode_as_uint32(map.get('string_key')[0]))
    print(mmkv_parser.decode_as_bytes(map.get('bytes_key')[0]))

    print(mmkv_parser.decode_as_float(map.get('float_key')[0]))

    pb_reader.decode_varint(BytesIO(bytes.fromhex('ff')))





