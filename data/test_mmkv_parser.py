import sys
import unittest
sys.path.append('..')	# Used for the `src` relative import

from src.mmkv_parser import MMKVParser, decode_unsigned_varint, decode_signed_varint



class TestVarintDecoder(unittest.TestCase):
	"""
	Test Class for testing the varint decoders
	"""


if __name__ == "__main__":
	unittest.main()