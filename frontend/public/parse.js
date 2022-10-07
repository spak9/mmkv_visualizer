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
    'uint32-type',
    'int64-type', 
    'uint64-type', 
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
 * Converts `hexString` into a 
function hexToBytes(hexString) {
    for (var bytes = [], c = 0; c < hexString.length; c += 2)
        bytes.push(parseInt(hexString.substr(c, 2), 16));
    return bytes;
}

/**
 * "Asynchronously" creates an `MMKVParser` instance in python and returns it as 
 * a `PyProxy` instance in JavaScript, now able to have functions called upon it.
 */
async function getMMKVParser() {
    let pyodide = await loadPyodide();
    console.log('[+] Finished setting up Pyodide')

    // Run the MMKVParse python code and parse data, storing the "PyProxy" result in "pyProxy"
    let pyProxy = pyodide.runPython(`print("Hello")`);
      

    // Convert our MMKVParser PyProxy into a `PyProxy`
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

        // Iterate through Array of Uint8Array values and create data cells - begin with hexstring-type.
        // Also add a "data-*" attribute that will be the hexstring-type data, always used for ingest into 
        // the MMKVParser API.
        for (let i = 0; i < arrayValue.length; i++) {

            // Create data cell with hexstring and add a data attribute 
            let valueCell = document.createElement('td')
            valueCell.className = interpretableTypes[0]
            let hexData = toHexString(arrayValue[i])
            valueCell.innerHTML = hexData
            valueCell.dataset.hexdata = hexData
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

    // Feed the data cell's dataset "hexdata" into the MMKVParser API based on new clicked-on class
    let newDataEncoding = null
    console.log(td.className)
    // const interpretableTypes = [
    // 'hexstring-type', 
    // 'string-type', 
    // 'int32-type', 
    // 'uint32-type',
    // 'int64-type', 
    // 'uint64-type', 
    // 'bytes-type',
    // 'float-type',
    // 'bool-type'
    // ]

    // hexstring-type --> String
    if (td.className === interpretableTypes[0]) {
        newDataEncoding = td.dataset.hexdata
    }

    // string-type --> String
    else if (td.className === interpretableTypes[1]) {
        newDataEncoding = mmkvParser.decode_as_string(td.dataset.hexdata)
    }

    // int-32-type --> Number
    else if (td.className === interpretableTypes[2]) {
        console.log(td.dataset.hexdata)
        newDataEncoding = mmkvParser.decode_as_int32(td.dataset.hexdata)
    }

    // uint-32-type --> Number
    else if (td.className === interpretableTypes[3]) {
        console.log(td.dataset.hexdata)
        newDataEncoding = mmkvParser.decode_as_uint32(td.dataset.hexdata)
    }

    // int-64-type --> Number
    else if (td.className === interpretableTypes[4]) {
        console.log(td.dataset.hexdata)
        newDataEncoding = mmkvParser.decode_as_int64(td.dataset.hexdata)
    }

    // uint64-type --> Number
    else if (td.className === interpretableTypes[5]) {
        console.log(td.dataset.hexdata)
        newDataEncoding = mmkvParser.decode_as_uint64(td.dataset.hexdata)
    }

    // bytes-type --> TypedArray
    else if (td.className === interpretableTypes[6]) {
        console.log(td.dataset.hexdata)
        newDataEncoding = mmkvParser.decode_as_bytes(td.dataset.hexdata)
    }

    // float-type --> Number
    else if (td.className === interpretableTypes[7]) {
        console.log(td.dataset.hexdata)
        newDataEncoding = mmkvParser.decode_as_float(td.dataset.hexdata)
    }

    // bool-type --> Bool
    else if (td.className === interpretableTypes[8]) {
        console.log(td.dataset.hexdata)
        newDataEncoding = mmkvParser.decode_as_bool(td.dataset.hexdata)
    }


    // Lastly, update our <td> instance inner HTML
    td.innerHTML = newDataEncoding
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

    // Decode the data into a PyProxy
    let mapProxy = mmkvParser.decode_into_map()

    // Convert the `PyProxy` to its native JavaScript type (Map[String: Array[Uint8Array]]) and update our global
    mmkvMap = mapProxy.toJs()

    // .main-buttons move up, create <table> full of data, and insert it into the DOM
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


