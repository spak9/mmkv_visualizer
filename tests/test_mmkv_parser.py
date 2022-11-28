import sys
import unittest

sys.path.append('../frontend/public')  # Used for the `src` relative import

from io import BytesIO
from collections import defaultdict
from mmkv_parser import MMKVParser, decode_unsigned_varint, decode_signed_varint


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


class TestMMKVParser(unittest.TestCase):
	"""
	Test Class for testing the MMKVParser class
	"""


	# Tests for __init__()
	def test_mmkv_parser_init_with_str(self):
		with open('data_all_types', 'rb') as f:
			mmkv_parser = MMKVParser(mmkv_file_data=f.read().hex())

	def test_mmkv_parser_init_with_bufferediobase(self):
		with open('data_all_types', 'rb') as f:
			mmkv_parser = MMKVParser(mmkv_file_data=f)

	def test_mmkv_parser_init_with_buffer_empty(self):
		with self.assertRaises(ValueError):
			parser = MMKVParser(mmkv_file_data=BytesIO(b''))
			parser.decode_into_map()

	# Tests for decode_into_map()
	def test_decode_map_simple_int_keypair(self):
		with open('data_int32_keypair', 'rb') as f:
			mmkv_parser = MMKVParser(mmkv_file_data=f)
			mmkv_map = mmkv_parser.decode_into_map()
			m = {'key':[b'\xdc\x22']}
			self.assertEqual(mmkv_map, m)

	def test_decode_map_all_types(self):
		with open('data_all_types', 'rb') as f:
			mmkv_parser = MMKVParser(mmkv_file_data=f)
			mmkv_map = mmkv_parser.decode_into_map()
			
			m = defaultdict(list, {
				'int32_pkey': [b'\xff\xff\xff\xff\x07'],
				'int32_nkey': [b'\x80\x80\x80\x80\xf8\xff\xff\xff\xff\x01'],
				'int64_pkey': [b'\xff\xff\xff\xff\xff\xff\xff\xff\x7f'],
				'int64_nkey': [b'\x80\x80\x80\x80\x80\x80\x80\x80\x80\x01'],
				'bool_true_key':[b'\x01'],
				'bool_false_key':[b'\x00'],
				'string_key': [b'\x0a\x73\x74\x65\x76\x65\x6e\x20\x70\x61\x6b'],
				'bytes_key': [b'\x0a\x73\x6f\x6d\x65\x20\x62\x79\x74\x65\x73'],
				'float_key': [b'\x1f\x85\xeb\x51\xb8\x1e\x09\x40']
			})
			self.assertEqual(mmkv_map, m)

	def test_decode_map_int_updates(self):
		with open('data_int32_keypair_with_updates', 'rb') as f:
			mmkv_parser = MMKVParser(mmkv_file_data=f)
			mmkv_map = mmkv_parser.decode_into_map()
			
			m = defaultdict(list, {
				'int_key': [b'\xe8\x07', b'\x64', b'\x0a', b'\x01']
			})
			self.assertEqual(mmkv_map, m)

	def test_decode_map_string_updates(self):
		with open('data_string_keypair_with_updates', 'rb') as f:
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
		with open('data_float_keypair_with_updates', 'rb') as f:
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
		with open('data_string_keypair_with_remove', 'rb') as f:
			mmkv_parser = MMKVParser(mmkv_file_data=f)
			mmkv_map = mmkv_parser.decode_into_map()
			
			m = defaultdict(list, {
				'key': [
				b'\x07\x76\x61\x6c\x75\x65\x5f\x34',
				b'\x07\x76\x61\x6c\x75\x65\x5f\x33'
				]
			})
			self.assertEqual(mmkv_map, m)


	# Tests for various "decode_as_<type>()" functions
	def test_decode_bool(self):
		with open('data_all_types', 'rb') as f:
			mmkv_parser = MMKVParser(mmkv_file_data=f)
			mmkv_map = mmkv_parser.decode_into_map()
			true_bool = mmkv_map.get('bool_true_key')[0]
			false_bool = mmkv_map.get('bool_false_key')[0]

			self.assertEqual(True, mmkv_parser.decode_as_bool(true_bool))
			self.assertEqual(False, mmkv_parser.decode_as_bool(false_bool))
			self.assertEqual(None, mmkv_parser.decode_as_bool(b'\x02'))

	def test_decode_string(self):
		with open('data_all_types', 'rb') as f:
			mmkv_parser = MMKVParser(mmkv_file_data=f)
			mmkv_map = mmkv_parser.decode_into_map()
			string = mmkv_map.get('string_key')[0]

			self.assertEqual('steven pak', mmkv_parser.decode_as_string(string))

	def test_decode_string_2(self):
		with open('data_all_types', 'rb') as f:
			mmkv_parser = MMKVParser(mmkv_file_data=f)
			mmkv_map = mmkv_parser.decode_into_map()
			hexstr = mmkv_map.get('string_key')[0].hex()
			self.assertEqual('steven pak', mmkv_parser.decode_as_string(hexstr))


	# Tests for decrypted databases
	def test_decrypt_one(self):
		with open('data_encrypt', 'rb') as f, open('data_encrypt.crc', 'rb') as c:
			mmkv_parser = MMKVParser(mmkv_file_data=f, crc_file_data=c)
			mmkv_parser.decrypt_and_reconstruct(key=b'kindalongsecretkey'[:16])
			mmkv_map = mmkv_parser.decode_into_map()

			m = defaultdict(list, {
				'bool_key': [b'\x01'],
				'name': [b'\x06steven'],
				'float_key':[b'\x1f\x85\xebQ\xb8\x1e\t@'],
				'int_key': [b'*']
			})

			self.assertEqual(mmkv_map, m)


if __name__ == "__main__":
	unittest.main()
