//
// Written by Steven Pak
//


//
// Mutable Application State and Helper Functions
//

// Global "singleton" MMKVParser, which facilitates the actual parsing of MMKV data
let mmkvParser = null;

// Global JavaScript Map[String: Array[Uint8Array]] once parsing is finished
let mmkvMap = null;

// Constant interpretable type (protobuf-based) classes in which <td> data cells 
// can take. Only one of these can be a class of a <td> at a time.
const interpretableTypes = [
    'hexstring-type', 
    'string-type', 
    'int32-type', 
    'signed-int32-type',
    'int64-type', 
    'signed-int64-type', 
    'bytes-type',
    'float-type',
    'bool-type'
    ]

// Set up our hex conversation function - creates an array of incrementing hex values
const byteToHex = [];
for (let n = 0; n <= 0xff; ++n)
{
    const hexOctet = n.toString(16).padStart(2, "0");
    byteToHex.push(hexOctet);
}

/**
 * Converts `arrayBuffer` into a hexlified string.
 * @param {ArrayBuffer} arrayBuffer The ArrayBuffer to convert to a hexlified string
 */
function toHexString(arrayBuffer)
{
    const buff = new Uint8Array(arrayBuffer);
    const hexOctets = []; // new Array(buff.length) is even faster (preallocates necessary array size), then use hexOctets[i] instead of .push()

    for (let i = 0; i < buff.length; ++i)
        hexOctets.push(byteToHex[buff[i]]);

    return hexOctets.join("").toUpperCase();
}

/**
 * Asynchronously creates an `MMKVParser` instance in python and returns it as 
 * a `PyProxy` instance in JavaScript, now able to have functions called upon it.
 */
async function getMMKVParser() {
    let pyodide = await loadPyodide();
    console.log('[+] Finished setting up Pyodide')

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
              self.mmkv_file = BytesIO(bytes.fromhex(mmkv_file))

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

          # Read in first 4 header bytes - [0:4] is total size.
          self.header_bytes = self.mmkv_file.read(4)
          self.pos += 4
          # [4:X] is unknown
          x, bytes_read = decode_varint(self.mmkv_file)
          self.pos += bytes_read

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
          if db_size == 0:
              print('[+] MMKV datastore size is 0 - making db_size 256KB.')
              db_size = 256000

          while self.pos < db_size:
              # parse key
              key_length, bytes_read = decode_varint(self.mmkv_file, mask=32)
              if (key_length, bytes_read) == (-1, -1):
                  print('[+] Ran out of bytes while decoding data into map - stopped parsing')
                  break

              self.pos += bytes_read
              try:
                key_bytes = self.mmkv_file.read(key_length)
                key = key_bytes.decode(encoding='utf-8')

              except UnicodeDecodeError:
                print(f'[+] Error trying to UTF-8 decode {key_bytes} - returning decoded_map.')
                return self.decoded_map


              if key == '' and key_length == 0:
                  break

              # parse value
              value_length, bytes_read = decode_varint(self.mmkv_file, mask=32)
              if (value_length, bytes_read) == (-1, -1):
                  print('[+] Ran out of bytes while decoding data into map - stopped parsing')
                  break

              # key-value pair was removed - value_length is 0
              elif (value_length, bytes_read) == (0, 1):
                print('[+] Value read was a null byte, therefore key-value pair was removed - no update and continuing')
                self.pos += bytes_read
                continue

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

        def reset(self) -> None:
            """
            Resets the instance variabls all back to original __init__ state

            :return: None
            """
            self.mmkv_file: Optional[BufferedIOBase] = None
            self.crc_file: Optional[BufferedIOBase] = None
            self.file_size: Optional[int] = None
            self.header_bytes: Optional[bytes] = None           # Should be 8 bytes after initialization
            self.decoded_map: defaultdict[str, List[bytes]] = defaultdict(list)
            self.pos = 0
            return None

      mmkv_parser = MMKVParser()
      mmkv_parser
    `);

    // Convert our MMKVParser into a `PyProxy`
    return pyProxy.toJs()
}


//
// DOM Node References & updates
//
let $pageMain = document.querySelector('.page-main')
let $pageMainButtons = document.querySelector('.main-buttons')
let $mmkvInput = document.querySelector('#mmkv-input')

function highlight() {
   $pageMain.classList.add('highlight')
}

function unhighlight() {
   $pageMain.classList.remove('highlight')
}

/**
 * Creates a new <table> instance, updates it with data from `mmkvMap`, then inserts it as a child 
 * of `.page-main`. 
 * The default type/class of every <td> will be "hexstring-type".
 */
function createAndInsertDataTable(){
    // Removes the `table-wrapper` div from DOM if it exists 
    let oldTableWrapper = document.querySelector('.table-wrapper')
    if (oldTableWrapper != null) {
        console.log('removing old table wrapper div')
        oldTableWrapper.remove()
    }

    // TextDecoder for UTF-8 values, keys have already been UTF-8 decoded
    let textDecoder = new TextDecoder()

    // Create our .table-wrapper div and add our table and headers
    let tableWrapper = document.createElement('div')
    tableWrapper.classList.add('table-wrapper')
    let table = document.createElement('table')
    tableWrapper.append(table)
    let keyHeaderCell = document.createElement('th')
    keyHeaderCell.innerHTML = "Keys"
    let valueHeaderCell = document.createElement('th')
    valueHeaderCell.innerHTML = "Values"
    valueHeaderCell.setAttribute('colspan', '100%')
    table.append(keyHeaderCell)
    table.append(valueHeaderCell)

    // Iterate through `mmkvMap`, which is Map[String: Array[Uint8Array]].
    // Create rows per iteration
    for (const [stringKey, arrayValue] of mmkvMap.entries()) {
        let row = document.createElement('tr')

        // Create our key cell
        let key = document.createElement('td')
        key.innerHTML = stringKey

        row.append(key)

        // Iterate through Array of Uint8Array values and create data cells - begin with hexstring-type
        for (let i = 0; i < arrayValue.length; i++) {
            let valueCell = document.createElement('td')
            valueCell.className = interpretableTypes[0]
            valueCell.innerHTML = toHexString(arrayValue[i])
            row.append(valueCell)
        }
        table.append(row)
    }
    $pageMain.append(tableWrapper)
    table.addEventListener('click', onDataCellClick)
}


//
// Event Listener Callbacks
//

/**
 * Callback for when dragging over the `page-main` element.
 * Should only preventDefault behavior.
 */
function onDragover(event) {
    console.log('[+] onDragover called')
    event.preventDefault()
}

/**
 * Callback for when user fully drops a file upon a valid drop zone. 
 * Encodes `File` into a hex string, which is then used to `initialize()` the `mmkvParser` instance.
 * 
 * Returns native JavaScript "Map[String: Array[Uint8Array]]"
 */
async function onDrop(event){
    console.log('[+] onDrop called')
    event.preventDefault()

    if (event.dataTransfer.files) {

        // TODO: Will need to update this to handle CRC check, taking 2 files in.
        // Get the first file (mmkv file)
        let mmkvFile = event.dataTransfer.files[0]
        await fileToMMKVMap(mmkvFile)
        console.log(mmkvMap)
    }
}

/**
 * Callback for when user successfully chooses a single file from their filesystem. 
 * Encodes `File` into a hex string, which is then used to `initialize()` the `mmkvParser` instance.
 * 
 * Returns native JavaScript "Map[String: Array[Uint8Array]]"
 */
async function onChange(event) {
    console.log('[+] onChange called')

    // TODO: Will need to update this to handle CRC check, taking 2 files in.
    // Get the first file (mmkv file)
    let mmkvFile = $mmkvInput.files[0]
    await fileToMMKVMap(mmkvFile)
    console.log(mmkvMap)
}

/**
 * Callback for when user clicks on a <td> data cell to rotate the interpretable type/class.
 * This utilizes event delegation, therefore this is added to the <table>, not the individual <td>s.
 * @param {event} Event The Event object that carries on the "click" event.
 */
function onDataCellClick(event) {
    let td = event.target

    if (td.tagName != "TD") {
        return;
    }

    // Rotate the element class by finding index of current class - NOT efficient and should update
    let currClassIndex = interpretableTypes.indexOf(td.className)
    let nextClassIndex = (currClassIndex + 1) % interpretableTypes.length
    td.className = interpretableTypes[nextClassIndex]

}

/**
 * Turns `mmkvFile` into a native JavaScript "Map[String: Array[Uint8Array]]"
 * @param {mmkvFile} mmkvFile The File to convert to a Map
 * 
 * Returns native JavaScript "Map[String: Array[Uint8Array]]"
 */
async function fileToMMKVMap(mmkvFile) {
    // File --> ArrayBuffer --> Uint8Array --> Hex String
    let data = await mmkvFile.arrayBuffer()

    let hexString = toHexString(data)

    // Reset and initialize our mmkvParser with hex string
    mmkvParser.reset()
    mmkvParser.initialize(hexString)

    // Decode the data into a PyProxty (`dict[list[bytes]]`)
    let mapProxy = mmkvParser.decode_into_map()

    // Convert the `PyProxy` to its native JavaScript type and update our global ``
    mmkvMap = mapProxy.toJs()

    // Have the main buttons disappear for table data display
    createAndInsertDataTable()
}

$mmkvInput.addEventListener('change', onChange)
$pageMain.addEventListener('drop', onDrop)
$pageMain.addEventListener('dragover', onDragover)


;['dragenter', 'dragover'].forEach(function(eventName) {
   $pageMain.addEventListener(eventName, highlight)
})
;['dragleave', 'drop'].forEach(function(eventName) {
   $pageMain.addEventListener(eventName, unhighlight)
})


/**
 * 
 * The start of this script - asynchronously call "getMMKVParser" and update our global 
 * `mmkvParser` instance when Promise is completed.
 * 
 */
getMMKVParser()
    .then(parser => {
        mmkvParser = parser
        console.log(`[+] Assigned MMKVParser - mmkvParser is ${mmkvParser}`)

    })
    .catch(err => {
        console.log('[+] Error in assigning mmkvParser')
    })

console.log(`[+] Script has loaded up - mmkvParser is ${mmkvParser}`)


