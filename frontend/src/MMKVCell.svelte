<script>

  import { mmkvParserStore } from './MMKVParserStore.mjs'
  import { get } from 'svelte/store'

	export let hexstring 		// Hex string representing the ray 
	let dataTypeIndex	= 0		// data type index for rotating on click 

	const dataTypes = [
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

  function interpretHexData(index) {
    let mmkvParser = get(mmkvParserStore)
    if (index % dataTypes.length == 0) {
      return hexstring
    }
    else if (index % dataTypes.length == 1) {
      return mmkvParser.decode_as_string(hexstring)
    }
    else if (index % dataTypes.length == 2) {
      return mmkvParser.decode_as_int32(hexstring)
    }
    else if (index % dataTypes.length == 3) {
      return mmkvParser.decode_as_uint32(hexstring)
    }
    else if (index % dataTypes.length == 4) {
      return mmkvParser.decode_as_int64(hexstring)
    }
    else if (index % dataTypes.length == 5) {
      return mmkvParser.decode_as_uint64(hexstring)
    }
    else if (index % dataTypes.length == 6) {
      return mmkvParser.decode_as_bytes(hexstring)
    }
    else if (index % dataTypes.length == 7) {
      return mmkvParser.decode_as_float(hexstring)
    }
    else if (index % dataTypes.length == 8) {
      return mmkvParser.decode_as_bool(hexstring)
    }
  }

</script>


<!-- HTML -->
<td on:click={() => dataTypeIndex += 1}>{interpretHexData(dataTypeIndex)}</td>


<!-- Styles -->
<style>

</style>