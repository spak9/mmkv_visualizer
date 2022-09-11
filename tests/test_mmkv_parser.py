import sys
import unittest

sys.path.append('..')  # Used for the `src` relative import

from io import BytesIO
from src.mmkv_parser import MMKVParser, decode_unsigned_varint, decode_signed_varint


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
			MMKVParser(mmkv_file_data=BytesIO(b''))


	# Tests for get_db_size()
	def test_get_db_size_simple_int_keypair(self):
		with open('data_int32_keypair', 'rb') as f:
			mmkv_parser = MMKVParser(mmkv_file_data=f)
		self.assertEqual(mmkv_parser.get_db_size(), 11)

	def test_get_db_size_simple_int_keypair_with_remove(self):
		with open('data_int32_keypair_with_remove', 'rb') as f:
			mmkv_parser = MMKVParser(mmkv_file_data=f)
		self.assertEqual(mmkv_parser.get_db_size(), 16)


	# Tests for decode_into_map()
	def test_decode_map_simple_int_keypair(self):
		with open('data_int32_keypair', 'rb') as f:
			mmkv_parser = MMKVParser(mmkv_file_data=f)
			mmkv_map = mmkv_parser.decode_into_map()
			m = {'key':[b'\xdc\x22']}
			self.assertEqual(mmkv_map, m)

	# def test_decode_map_all_types(self):
	# 	with open('data_all_types', 'rb') as f:
	# 		mmkv_parser = MMKVParser(mmkv_file_data=f)
	# 		mmkv_map = mmkv_parser.decode_into_map()
	# 		print(mmkv_map)



if __name__ == "__main__":
	unittest.main()
