from mmkv_parser import MMKVParser
from pathlib import Path


if __name__ == "__main__":

    mmkv_parser = MMKVParser()

    data_path = Path(__file__).resolve().parent.parent / 'tests' / 'data_all_types'
    print(data_path)
    mmkv_parser.initialize(mmkv_file=str(data_path))
    map = mmkv_parser.decode_into_map()
    print(map)






