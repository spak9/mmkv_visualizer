import sys
import unittest
from io import BytesIO
from collections import defaultdict
from pathlib import Path

from frontend.public.mmkv_parser import MMKVParser, decode_unsigned_varint, decode_signed_varint

# Global variables used for testing different MMKV files from different platform/version permutations
# e.g. <PLATFORM>_<VERSION>
BASE_DIR = Path(__file__).resolve().parent
PYTHON_V1_2_13_PATH = BASE_DIR / 'python' / 'v1_2_13'
ANDROID_V1_2_16_PATH = BASE_DIR / 'android' / 'v1_2_16'


class TestVarintDecoder(unittest.TestCase):
    """
    Test Class for testing the varint decoders.
    """
    def test_positive_int32(self):
        """ Typical int32 varint """
        value_1 = decode_unsigned_varint(BytesIO(b'\xff\xff\xff\xff\x07'))[0]
        value_2 = (1 << 31) - 1  # 2147483647
        self.assertEqual(value_1, value_2)

    def test_negative_int32(self):
        """ Negative int32 varint. Will be 10-bytes in size """
        value_1 = decode_signed_varint(BytesIO(b'\x80\x80\x80\x80\xf8\xff\xff\xff\xff\x01'))[0]
        value_2 = -1 * (1 << 31)  # -2147483648
        self.assertEqual(value_1, value_2)

    def test_positive_int64(self):
        """ Typical int64 varint """
        value_1 = decode_unsigned_varint(BytesIO(b'\xff\xff\xff\xff\xff\xff\xff\xff\x7f'), mask=64)[0]
        value_2 = (1 << 63) - 1  # 9223372036854775807
        self.assertEqual(value_1, value_2)

    def test_negative_int64(self):
        """ Negative int64 varint. Will be 10-bytes in size """
        value_1 = decode_signed_varint(BytesIO(b'\x80\x80\x80\x80\x80\x80\x80\x80\x80\x01'), mask=64)[0]
        value_2 = -1 * (1 << 63)  # -9223372036854775808
        self.assertEqual(value_1, value_2)


class TestMMKVParser_PythonVersion1_2_13(unittest.TestCase):
    """
    Test class for testing the MMKVParser against:
    v1.2.13 Python data
    """

    ######
    # Basic Initialization tests
    ######
    def test_mmkv_parser_init_with_str(self):
        with open(PYTHON_V1_2_13_PATH / 'data_all_types', 'rb') as f:
            mmkv_parser = MMKVParser(mmkv_file_data=f.read().hex())

    def test_mmkv_parser_init_with_bufferediobase(self):
        with open(PYTHON_V1_2_13_PATH / 'data_all_types', 'rb') as f:
            mmkv_parser = MMKVParser(mmkv_file_data=f)

    def test_mmkv_parser_init_with_buffer_empty(self):
        with self.assertRaises(ValueError):
            parser = MMKVParser(mmkv_file_data=BytesIO(b''))
            parser.decode_into_map()

    #####
    # Tests for holistically "raw map" checks - no type decoding
    #####
    def test_decode_map_simple_int_keypair(self):
        with open(PYTHON_V1_2_13_PATH / 'data_int32_keypair', 'rb') as f:
            mmkv_parser = MMKVParser(mmkv_file_data=f)
            mmkv_map = mmkv_parser.decode_into_map()
            m = {'key': [b'\xdc\x22']}
            self.assertEqual(mmkv_map, m)

    def test_decode_map_all_types(self):
        with open(PYTHON_V1_2_13_PATH / 'data_all_types', 'rb') as f:
            mmkv_parser = MMKVParser(mmkv_file_data=f)
            mmkv_map = mmkv_parser.decode_into_map()

            m = defaultdict(list, {
                'int32_pkey': [b'\xff\xff\xff\xff\x07'],
                'int32_nkey': [b'\x80\x80\x80\x80\xf8\xff\xff\xff\xff\x01'],
                'int64_pkey': [b'\xff\xff\xff\xff\xff\xff\xff\xff\x7f'],
                'int64_nkey': [b'\x80\x80\x80\x80\x80\x80\x80\x80\x80\x01'],
                'bool_true_key': [b'\x01'],
                'bool_false_key': [b'\x00'],
                'string_key': [b'\x0a\x73\x74\x65\x76\x65\x6e\x20\x70\x61\x6b'],
                'bytes_key': [b'\x0a\x73\x6f\x6d\x65\x20\x62\x79\x74\x65\x73'],
                'float_key': [b'\x1f\x85\xeb\x51\xb8\x1e\x09\x40']
            })
            self.assertEqual(mmkv_map, m)

    def test_decode_map_int_updates(self):
        with open(PYTHON_V1_2_13_PATH / 'data_int32_keypair_with_updates', 'rb') as f:
            mmkv_parser = MMKVParser(mmkv_file_data=f)
            mmkv_map = mmkv_parser.decode_into_map()

            m = defaultdict(list, {
                'int_key': [b'\xe8\x07', b'\x64', b'\x0a', b'\x01']
            })
            self.assertEqual(mmkv_map, m)

    def test_decode_map_string_updates(self):
        with open(PYTHON_V1_2_13_PATH / 'data_string_keypair_with_updates', 'rb') as f:
            mmkv_parser = MMKVParser(mmkv_file_data=f)
            mmkv_map = mmkv_parser.decode_into_map()

            m = defaultdict(list, {
                'string_key': [b'\x04\xf0\x9f\x98\x81',
                               b'\x04\xf0\xa0\x9c\x8e',
                               b'\x02\xc3\x98',
                               b'\x06\x73\x74\x65\x76\x65\x6e']
            })
            self.assertEqual(mmkv_map, m)

    def test_decode_map_float_updates(self):
        with open(PYTHON_V1_2_13_PATH / 'data_float_keypair_with_updates', 'rb') as f:
            mmkv_parser = MMKVParser(mmkv_file_data=f)
            mmkv_map = mmkv_parser.decode_into_map()
            l = [b'\x1f\x85\xeb\x51\xb8\x1e\x09\x40',
                 b'\x54\xe3\xa5\x9b\xc4\x20\x09\x40',
                 b'\x36\x3c\xbd\x52\x96\x21\x09\x40',
                 b'\x6f\x9e\xea\x90\x9b\x21\x09\x40']
            l.reverse()
            m = defaultdict(list, {
                'float_key': l
            })
            self.assertEqual(mmkv_map, m)

    def test_decode_map_string_removes(self):
        with open(PYTHON_V1_2_13_PATH / 'data_string_keypair_with_remove', 'rb') as f:
            mmkv_parser = MMKVParser(mmkv_file_data=f)
            mmkv_map = mmkv_parser.decode_into_map()

            m = defaultdict(list, {
                'key': [
                    b'\x07\x76\x61\x6c\x75\x65\x5f\x34',
                    b'\x07\x76\x61\x6c\x75\x65\x5f\x33'
                ]
            })
            self.assertEqual(mmkv_map, m)

    ######
    # Tests for various "decode_as_<type>()" functions
    ######
    def test_decode_bool(self):
        with open(PYTHON_V1_2_13_PATH / 'data_all_types', 'rb') as f:
            mmkv_parser = MMKVParser(mmkv_file_data=f)
            mmkv_map = mmkv_parser.decode_into_map()
            true_bool = mmkv_map.get('bool_true_key')[0]
            false_bool = mmkv_map.get('bool_false_key')[0]

            self.assertEqual(True, mmkv_parser.decode_as_bool(true_bool))
            self.assertEqual(False, mmkv_parser.decode_as_bool(false_bool))
            self.assertEqual(None, mmkv_parser.decode_as_bool(b'\x02'))

    def test_decode_string(self):
        with open(PYTHON_V1_2_13_PATH / 'data_all_types', 'rb') as f:
            mmkv_parser = MMKVParser(mmkv_file_data=f)
            mmkv_map = mmkv_parser.decode_into_map()
            string = mmkv_map.get('string_key')[0]

            self.assertEqual('steven pak', mmkv_parser.decode_as_string(string))

    def test_decode_string_2(self):
        with open(PYTHON_V1_2_13_PATH / 'data_all_types', 'rb') as f:
            mmkv_parser = MMKVParser(mmkv_file_data=f)
            mmkv_map = mmkv_parser.decode_into_map()
            hexstr = mmkv_map.get('string_key')[0].hex()
            self.assertEqual('steven pak', mmkv_parser.decode_as_string(hexstr))

    def test_decode_double_precision_float(self):
        with open(PYTHON_V1_2_13_PATH / 'data_all_types', 'rb') as f:
            mmkv_parser = MMKVParser(mmkv_file_data=f)
            mmkv_map = mmkv_parser.decode_into_map()
            hexstr = mmkv_map.get('float_key')[0].hex()
            self.assertEqual(3.14, mmkv_parser.decode_as_float(hexstr))

    # Tests for decrypted databases
    def test_decrypt_one(self):
        with open(PYTHON_V1_2_13_PATH / 'data_encrypt', 'rb') as f, open(PYTHON_V1_2_13_PATH / 'data_encrypt.crc', 'rb') as c:
            mmkv_parser = MMKVParser(mmkv_file_data=f, crc_file_data=c)
            mmkv_parser.decrypt_and_reconstruct(key=b'kindalongsecretkey'[:16])
            mmkv_map = mmkv_parser.decode_into_map()

            m = defaultdict(list, {
                'bool_key': [b'\x01'],
                'name': [b'\x06steven'],
                'float_key': [b'\x1f\x85\xebQ\xb8\x1e\t@'],
                'int_key': [b'*']
            })

            self.assertEqual(mmkv_map, m)

class TestMMKVParser_AndroidVersion1_2_16(unittest.TestCase):
    """
    Test class for testing the MMKVParser against:
    v1.2.16 Android
    """
    #####
    # Tests for holistically "raw map" checks - no type decoding
    #####
    def test_decode_map_all_types(self):
        with open(ANDROID_V1_2_16_PATH / 'data_all_types', 'rb') as f:
            mmkv_parser = MMKVParser(mmkv_file_data=f)
            mmkv_map = mmkv_parser.decode_into_map()

            m = defaultdict(list, {
                'int32_pkey': [b'\xff\xff\xff\xff\x07'],
                'int32_nkey': [b'\x80\x80\x80\x80\xf8\xff\xff\xff\xff\x01'],
                'int64_pkey': [b'\xff\xff\xff\xff\xff\xff\xff\xff\x7f'],
                'int64_nkey': [b'\x80\x80\x80\x80\x80\x80\x80\x80\x80\x01'],
                'bool_true_key': [b'\x01'],
                'bool_false_key': [b'\x00'],
                'string_key': [b'\x0a\x73\x74\x65\x76\x65\x6e\x20\x70\x61\x6b'],
                'bytes_key': [b'\x0a\x73\x6f\x6d\x65\x20\x62\x79\x74\x65\x73'],
                'float_key': [b'\xc3\xf5H@'],
                'double_key': [b'\xff\xff\xff\xff\xff\xff\xef\x7f']
            })
            self.assertEqual(mmkv_map, m)

    def test_decode_map_simple_int_keypair(self):
        with open(ANDROID_V1_2_16_PATH / 'data_int32_keypair', 'rb') as f:
            mmkv_parser = MMKVParser(mmkv_file_data=f)
            mmkv_map = mmkv_parser.decode_into_map()
            m = {'key': [b'\xdc\x22']}
            self.assertEqual(mmkv_map, m)

    def test_decode_map_int_removes(self):
        with open(ANDROID_V1_2_16_PATH / 'data_int32_keypair_with_remove', 'rb') as f:
            mmkv_parser = MMKVParser(mmkv_file_data=f)
            mmkv_map = mmkv_parser.decode_into_map()

            m = defaultdict(list, {
                'key': [b'\xdc"']
            })
            self.assertEqual(mmkv_map, m)

    def test_decode_map_int_updates(self):
        with open(ANDROID_V1_2_16_PATH / 'data_int32_keypair_with_updates', 'rb') as f:
            mmkv_parser = MMKVParser(mmkv_file_data=f)
            mmkv_map = mmkv_parser.decode_into_map()

            m = defaultdict(list, {
                'int_key': [b'\xe8\x07', b'\x64', b'\x0a', b'\x01']
            })
            self.assertEqual(mmkv_map, m)

    def test_decode_map_string_updates(self):
        with open(ANDROID_V1_2_16_PATH / 'data_string_keypair_with_updates', 'rb') as f:
            mmkv_parser = MMKVParser(mmkv_file_data=f)
            mmkv_map = mmkv_parser.decode_into_map()

            m = defaultdict(list, {
                'string_key': [b'\x04\xf0\x9f\x98\x81',
                               b'\x04\xf0\xa0\x9c\x8e',
                               b'\x02\xc3\x98',
                               b'\x06\x73\x74\x65\x76\x65\x6e']
            })
            self.assertEqual(mmkv_map, m)

    def test_decode_map_float_updates(self):
        with open(ANDROID_V1_2_16_PATH / 'data_float_keypair_with_updates', 'rb') as f:
            mmkv_parser = MMKVParser(mmkv_file_data=f)
            mmkv_map = mmkv_parser.decode_into_map()
            l = [b'\xdd\x0cI@', b'\xb3\x0cI@', b'%\x06I@', b'\xc3\xf5H@']
            m = defaultdict(list, {
                'float_key': l
            })
            self.assertEqual(mmkv_map, m)

    def test_decode_map_string_removes(self):
        with open(ANDROID_V1_2_16_PATH / 'data_string_keypair_with_remove', 'rb') as f:
            mmkv_parser = MMKVParser(mmkv_file_data=f)
            mmkv_map = mmkv_parser.decode_into_map()

            m = defaultdict(list, {
                'key': [
                    b'\x07\x76\x61\x6c\x75\x65\x5f\x34',
                    b'\x07\x76\x61\x6c\x75\x65\x5f\x33'
                ]
            })
            self.assertEqual(mmkv_map, m)

    ######
    # Tests for various "decode_as_<type>()" functions
    ######
    def test_decode_bool(self):
        with open(ANDROID_V1_2_16_PATH / 'data_all_types', 'rb') as f:
            mmkv_parser = MMKVParser(mmkv_file_data=f)
            mmkv_map = mmkv_parser.decode_into_map()
            true_bool = mmkv_map.get('bool_true_key')[0]
            false_bool = mmkv_map.get('bool_false_key')[0]

            self.assertEqual(True, mmkv_parser.decode_as_bool(true_bool))
            self.assertEqual(False, mmkv_parser.decode_as_bool(false_bool))
            self.assertEqual(None, mmkv_parser.decode_as_bool(b'\x02'))

    def test_decode_string(self):
        with open(ANDROID_V1_2_16_PATH / 'data_all_types', 'rb') as f:
            mmkv_parser = MMKVParser(mmkv_file_data=f)
            mmkv_map = mmkv_parser.decode_into_map()
            string = mmkv_map.get('string_key')[0]

            self.assertEqual('steven pak', mmkv_parser.decode_as_string(string))

    def test_decode_string_2(self):
        with open(ANDROID_V1_2_16_PATH / 'data_all_types', 'rb') as f:
            mmkv_parser = MMKVParser(mmkv_file_data=f)
            mmkv_map = mmkv_parser.decode_into_map()
            hexstr = mmkv_map.get('string_key')[0].hex()
            self.assertEqual('steven pak', mmkv_parser.decode_as_string(hexstr))

    def test_decode_string_set(self):
        with open(ANDROID_V1_2_16_PATH / 'data_string_set_with_updates_and_removes', 'rb') as f:
            mmkv_parser = MMKVParser(mmkv_file_data=f)
            mmkv_map = mmkv_parser.decode_into_map()

            first_encode = mmkv_map.get('string_set_key')[0].hex()
            second_encode = mmkv_map.get('string_set_key')[1].hex()

            self.assertEqual({"one", "two", "three", "four", "five"}, mmkv_parser.decode_as_string_set(second_encode))
            self.assertEqual({"one", "two", "three", "four", "five", "six?"}, mmkv_parser.decode_as_string_set(first_encode))

    def test_decode_all_floats(self):
        with open(ANDROID_V1_2_16_PATH / 'data_all_types', 'rb') as f:
            mmkv_parser = MMKVParser(mmkv_file_data=f)
            mmkv_map = mmkv_parser.decode_into_map()

            # Test both Android "float" (single-precision) and "double" (double-precision)
            float_data = mmkv_map.get('float_key')[0].hex()
            double_data = mmkv_map.get('double_key')[0].hex()
            self.assertEqual(3.140000104904175, mmkv_parser.decode_as_754_single_precision(float_data))
            self.assertEqual(sys.float_info.max, mmkv_parser.decode_as_754_double_precision(double_data))

    def test_decode_parcelable_intent(self):
        with open(ANDROID_V1_2_16_PATH / 'data_parcelable_with_updates_and_removes', 'rb') as f:
            mmkv_parser = MMKVParser(mmkv_file_data=f)
            mmkv_map = mmkv_parser.decode_into_map()

            encoded_parcelable = [
                b'\xa8\x02\xff\xff\xff\xff\x00\x00\x00\x00\t\x00\x00\x00text/html\x00\x00\x00\xff\xff\xff\xff\x00\x00\x00\x00\xff\xff\xff\xff\x17\x00\x00\x00c\x00o\x00m\x00.\x00e\x00x\x00a\x00m\x00p\x00l\x00e\x00.\x00m\x00m\x00k\x00v\x00t\x00e\x00s\x00t\x00a\x00p\x00p\x00\x00\x00$\x00\x00\x00c\x00o\x00m\x00.\x00e\x00x\x00a\x00m\x00p\x00l\x00e\x00.\x00m\x00m\x00k\x00v\x00t\x00e\x00s\x00t\x00a\x00p\x00p\x00.\x00M\x00a\x00i\x00n\x00A\x00c\x00t\x00i\x00v\x00i\x00t\x00y\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\xfe\xff\xff\xffd\x00\x00\x00BNDL\x03\x00\x00\x00\x03\x00\x00\x00a\x00g\x00e\x00\x00\x00\x01\x00\x00\x00\x1b\x00\x00\x00\x04\x00\x00\x00n\x00a\x00m\x00e\x00\x00\x00\x00\x00\x00\x00\x00\x00\n\x00\x00\x00S\x00t\x00e\x00v\x00e\x00n\x00 \x00P\x00a\x00k\x00\x00\x00\x00\x00\x05\x00\x00\x00s\x00k\x00i\x00l\x00l\x00\x00\x00\x08\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00',
                b'\x8c\x02\xff\xff\xff\xff\x00\x00\x00\x00\t\x00\x00\x00text/html\x00\x00\x00\xff\xff\xff\xff\x00\x00\x00\x00\xff\xff\xff\xff\x17\x00\x00\x00c\x00o\x00m\x00.\x00e\x00x\x00a\x00m\x00p\x00l\x00e\x00.\x00m\x00m\x00k\x00v\x00t\x00e\x00s\x00t\x00a\x00p\x00p\x00\x00\x00$\x00\x00\x00c\x00o\x00m\x00.\x00e\x00x\x00a\x00m\x00p\x00l\x00e\x00.\x00m\x00m\x00k\x00v\x00t\x00e\x00s\x00t\x00a\x00p\x00p\x00.\x00M\x00a\x00i\x00n\x00A\x00c\x00t\x00i\x00v\x00i\x00t\x00y\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\xfe\xff\xff\xffH\x00\x00\x00BNDL\x02\x00\x00\x00\x03\x00\x00\x00a\x00g\x00e\x00\x00\x00\x01\x00\x00\x00\x1b\x00\x00\x00\x04\x00\x00\x00n\x00a\x00m\x00e\x00\x00\x00\x00\x00\x00\x00\x00\x00\n\x00\x00\x00S\x00t\x00e\x00v\x00e\x00n\x00 \x00P\x00a\x00k\x00\x00\x00\x00\x00']
            
            self.assertEqual(mmkv_map.get('parcelable_key'), encoded_parcelable)

    # Tests for decrypted databases
    def test_decrypt_one(self):
        with open(ANDROID_V1_2_16_PATH / 'data_encrypt', 'rb') as f, open(ANDROID_V1_2_16_PATH / 'data_encrypt.crc',
                                                                         'rb') as c:
            mmkv_parser = MMKVParser(mmkv_file_data=f, crc_file_data=c)
            mmkv_parser.decrypt_and_reconstruct(key=b'kindalongsecretkey')
            mmkv_map = mmkv_parser.decode_into_map()

            m = defaultdict(list, {
                'bool_key': [b'\x01'],
                'name': [b'\x06steven'],
                'float_key': [b'\xc3\xf5H@'],
                'int_key': [b'*']
            })

            self.assertEqual(mmkv_map, m)

if __name__ == "__main__":
    unittest.main()