
/*
    Sets up the global python environment and should be run upon page load.
    Returns our "pyodide" instance.
*/
async function setupPyodide() {
    let pyodide = await loadPyodide();
    console.log('[+] Finished setting up Pyodide')
    return pyodide
}


/*
    Processes
*/
async function processData(inputHexString){
    let pyodide = await pyodidePromise
    parseData(pyodide, inputHexString)
}

/*
    Processes an input hex string that represents the MMKV data, parses it according to the
    MMKV protocol, eventually receiving native JavaScript "Map" of type {str: Array[UInt8Array]}
*/
function parseData(pyodide, inputHexString) {

    // Run the MMKVParse python code and parse data, storing the "PyProxy" result in "pyProxy"
    let pyProxy = pyodide.runPython(`
      # 1. Imports
      from io import BufferedIOBase, BytesIO
      from pathlib import Path
      from typing import Optional, List, Tuple, Union
      from collections import defaultdict

      import sys
      import struct
      import ctypes

      # 2. Decode Varints
      def decode_varint(buffered_base: BufferedIOBase, mask: int = 64) -> Tuple[int, int]:
        """
        Reads a base-128 varint from 'buffered_base' and returns the positive result of the
        varint.
        This assumes a 'mask' of 64-bits for decoding typical "int32" and "int64" values,
        but should pass in a mask of 32-bits when decoding varints that denote lengths.
        """
        shift = 0
        result = 0
        bytes_read = 0
        byte = buffered_base.read(1)
        bytes_read += 1

        # Check if 'buffered_base' has valid bytes
        if not byte:
            print('[+] buffered_reader has no more bytes to read. Most likely trying to decode'
                  ' data that is not a varint.')
            return -1, -1

        # Iterate through 'buffered_base' and varint
        while True:
            i = struct.unpack('B', byte)[0]

            # Prepare the result by ANDing the lower 7-bits and shifting for every byte read
            result |= (i & 0x7f) << shift
            shift += 7
            if not (i & 0x80):
                # AND the value to keep it within 'mask' range
                result &= ((1 << mask) - 1)
                break

            byte = buffered_base.read(1)
            bytes_read += 1
            if not byte:
                print('[+] buffered_reader has no more bytes to read. Most likely trying to decode'
                      ' data that is not a varint.')
                return -1, -1

        return result, bytes_read

      def decode_signed_varint(buffered_base: BufferedIOBase, mask: int = 64) -> Tuple[int, int]:
          """
          Reads a base-128 varint from 'buffered_base' and returns the negative result of the
          varint.
          This assumes a 'mask' of 64-bits for decoding typical "int32" and "int64" with negative values.
          """
          shift = 0
          result = 0
          bytes_read = 0
          byte = buffered_base.read(1)
          bytes_read += 1

          # Check if 'buffered_base' has valid bytes
          if not byte:
              print('[+] buffered_reader has no more bytes to read. Most likely trying to decode'
                    ' data that is not a varint.')
              return -1, -1

          # Iterate through 'buffered_base'
          while True:
              i = struct.unpack('B', byte)[0]

              # Prepare the result by ANDing the lower 7-bits and shifting for every byte read
              result |= (i & 0x7f) << shift
              shift += 7
              if not (i & 0x80):
                  result &= (1 << mask) - 1
                  if mask == 64:
                      result = ctypes.c_int64(result).value
                  else:
                      result = ctypes.c_int32(result).value
                  break

              byte = buffered_base.read(1)
              bytes_read += 1

          return result, bytes_read

      class MMKVParser:
        def __init__(self):
            self.mmkv_file: Optional[BufferedIOBase] = None
            self.crc_file: Optional[BufferedIOBase] = None
            self.file_size: Optional[int] = None
            self.header_bytes: Optional[bytes] = None           # Should be 8 bytes after initialization
            self.decoded_map: defaultdict[str, List[bytes]] = defaultdict(list)
            self.pos = 0

        def initialize(self, mmkv_file: Union[str, bytes], crc_file: Union[str, bytes] = '') -> None:
          """
          Initializes the MMKV data file and optionally the CRC32 file.
          If either parameter is a string, then treat it as a file path, else if its bytes,
          treat it as the actual binary MMKV data.

          :param mmkv_file: absolute path filename string or bytes data
          :param crc_file: absolute path filename string or bytes data
          :return: None
          """

          # 1. 'mmkv_file' is str
          if isinstance(mmkv_file, str):

              # Check if files exists w.r.t the "data" directory
              mmkv_file_path: Path = Path(mmkv_file)
              if not mmkv_file_path.exists():
                  print(f'[+] The following directory does not exist - {mmkv_file}')
                  sys.exit(-1)

              # Set up the MMKV File object
              self.mmkv_file = open(mmkv_file_path, 'rb')

          # 2. 'mmkv_file' is bytes
          elif isinstance(mmkv_file, bytes):

              # Set up the MMKV File object
              self.mmkv_file = BytesIO(mmkv_file)

          # 3. 'mmkv_file' is not correct type
          else:
              raise TypeError(f'mmkv_file is of type {type(mmkv_file)} - should be either str or bytes.')

          # Check file total size
          # self.file_size = mmkv_file_path.stat().st_size
          # print(f'[+] {mmkv_file_path.name} is {self.file_size} bytes')

          # Read in first 8 header bytes - [0:4] is total size, [4:8] is garbage bytes basically (0xffffff07)
          self.header_bytes = self.mmkv_file.read(8)
          self.pos += 8

          print('finished')
          return None


        def get_db_size(self) -> Optional[int]:
          """
          Returns the actual size of the MMKV database, that is, the size that the database knows about.

          :return: int size or None on error
          """
          if not self.header_bytes:
              raise TypeError('Header bytes is None. Please make sure to successfully initialize() db.')

          return struct.unpack('<I', self.header_bytes[0:4])[0]


        def decode_into_map(self) -> Optional[defaultdict]:
          """
          A best-effort approach on linearly parsing the 'mmkv_file' BufferedReader
          and build up our 'decoded_map'.

          :return: our built-up 'decoded_map' or None on error
          """

          # Loop and read key-value pairs into 'decoded_map'
          db_size = self.get_db_size()
          if not db_size:
              raise ValueError('Cannot read MMKV datastore size - please make sure you successfully initialize().')

          while self.pos < db_size:
              # parse key
              key_length, bytes_read = decode_varint(self.mmkv_file, mask=32)
              if (key_length, bytes_read) == (-1, -1):
                  print('[+] Ran out of bytes while decoding data into map - stopped parsing')
                  break

              self.pos += bytes_read
              key = self.mmkv_file.read(key_length).decode(encoding='utf-8')

              if key == '' and key_length == 0:
                  break

              # parse value
              value_length, bytes_read = decode_varint(self.mmkv_file, mask=32)
              if (value_length, bytes_read) == (-1, -1):
                  print('[+] Ran out of bytes while decoding data into map - stopped parsing')
                  break

              self.pos += bytes_read
              value = self.mmkv_file.read(value_length)  # interpretable

              # update map
              self.decoded_map[key].append(value)

          return self.decoded_map


        def decode_as_bool(self, value: bytes) -> Optional[bool]:
          """
          Attempts to decode 'value' as a boolean.

          :param value: protobuf-encoded bytes value
          :return: Returns the boolean result if possible, or None if not
          """
          if value == bytes.fromhex('01'):
              return True
          elif value == bytes.fromhex('00'):
              return False
          else:
              return None

        def decode_as_int32(self, value: bytes) -> int:
            """
            Decodes 'value' as a signed 32-bit int.

            :param value: protobuf-encoded bytes value
            :return: Returns the signed 32-bit int result
            """
            return decode_signed_varint(BytesIO(value), mask=32)[0]

        def decode_as_int64(self, value: bytes) -> int:
            """
            Decodes 'value' as a signed 64-bit int.

            :param value: protobuf-encoded bytes value
            :return: Returns the signed 64-bit int result
            """
            return decode_signed_varint(BytesIO(value), mask=64)[0]

        def decode_as_uint32(self, value: bytes) -> int:
            """
            Decodes 'value' as an unsigned 32-bit int.

            :param value: protobuf-encoded bytes value
            :return: Returns the unsigned 32-bit int result
            """
            return decode_varint(BytesIO(value), mask=32)[0]

        def decode_as_uint64(self, value: bytes) -> int:
            """
            Decodes 'value' as an unsigned 64-bit int.

            :param value: protobuf-encoded bytes value
            :return: Returns the unsigned 64-bit int result
            """
            return decode_varint(BytesIO(value), mask=64)[0]

        def decode_as_string(self, value: bytes) -> Optional[str]:
            """
            Attempts to decodes 'value' as a UTF-8 string.
            Note: This assumes that 'value' has the "erroneous" varint length wrapper

            :param value: protobuf-encoded bytes value
            :return: Returns the UTF-8 decoded string, or None if not possible
            """
            # Strip off the varint length delimiter bytes
            wrapper_bytes, wrapper_bytes_len = decode_varint(BytesIO(value), mask=32)
            value = value[wrapper_bytes_len:]
            try:
                return value.decode('utf-8')
            except:
                print(f'Could not UTF-8 decode [{value}]')
                return None

        def decode_as_bytes(self, value: bytes) -> bytes:
            """
            Decodes 'value' as bytes.
            Note: This assumes that 'value' has the "erroneous" varint length wrapper

            :param value: protobuf-encoded bytes value
            :return: Returns the bytes
            """
            # Strip off the varint length delimiter bytes
            wrapper_bytes, wrapper_bytes_len = decode_varint(BytesIO(value), mask=32)
            value = value[wrapper_bytes_len:]
            return value

        def decode_as_float(self, value: bytes) -> float:
            """
            Decodes 'value' as a double (8-bytes), which is a float type in Python.

            :param value: protobuf-encoded bytes value
            :return: Returns the float result
            """
            return struct.unpack('<d', value)[0]

      mmkv_parser = MMKVParser()
      mmkv_parser.initialize(mmkv_file=bytes.fromhex('''d7000000ffffff0712696e7433325f706f7369746976655f6b657905ffffffff0712696e7433325f6e656761746976655f6b65790a80808080f8ffffffff0112696e7436345f706f7369746976655f6b657909ffffffffffffffff7f12696e7436345f6e656761746976655f6b65790a808080808080808080010d626f6f6c5f747275655f6b657901010e626f6f6c5f66616c73655f6b657901000a737472696e675f6b65790b0a73746576656e2070616b0962797465735f6b65790b0a736f6d6520627974657309666c6f61745f6b6579081f85eb51b81e0940'''))
      print(mmkv_parser.get_db_size())
      mmkv_parser.decode_into_map()
    `);

    // Convert our "PyProxy" object into a native JavaScript "Map"
    let mmkvMap = pyProxy.toJs()
    console.log(mmkvMap)
    console.log('[+] Converted PyProxy object to JavaScript "Map" type.')

    // Decode values at UTF-8
    let textDecoder = new TextDecoder()
    for (const [key, value] of mmkvMap.entries()) {
        console.log(value[0].constructor.name)
        console.log(`Key: ${key}; Value: ${textDecoder.decode(value[0]) }`)
    }

}

// Run script - setup global "loadPyodide" Promise, which then can be used in async functions
let pyodidePromise = setupPyodide()
