<script>

  import MMKVCellModal from './MMKVCellModal.svelte'
  import { mmkvParserStore } from './MMKVParserStore.mjs'
  import { get } from 'svelte/store'

	export let hexstring 		// Hex string representing the ray 

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

  let hidden = true
	let dataTypeIndex	= 0		// data type index for rotating on click 
  let dataType = dataTypes[dataTypeIndex]
  $: dataType = dataTypes[dataTypeIndex % dataTypes.length]

  function interpretHexData(index) {
    let mmkvParser = get(mmkvParserStore)
    // dataType = dataTypes[index % dataTypes.length]
    console.log(dataType)
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

  async function copyContent(e) {
    e.stopPropagation()
    console.log("[+] Copy Content")
    let data = interpretHexData(dataTypeIndex)
    navigator.clipboard.writeText(data).then(
      () => {
        console.log('[+] Copied data')
      },
      () => {
        console.log('[+] Copy failed')
      })
  }

  function expandContent(e) {
    e.stopPropagation()
    console.log('[+] Expand Content')
    hidden = false
  }
</script>


<!-- HTML -->
<td class={dataType} on:click={() => dataTypeIndex += 1}>
  <span class="data-type">({dataType.split('-')[0]})</span>
  <span class="data">{interpretHexData(dataTypeIndex)}</span>
  <span class="material-icons md-18" on:click={expandContent}>expand</span>
  <span class="material-icons md-18" on:click={copyContent}>content_copy</span>
</td>

<MMKVCellModal 
  bind:hidden={hidden} 
  data={interpretHexData(dataTypeIndex)} 
  dataType={dataType.split('-')[0]}/>


<!-- Styles -->
<style>
  .md-18 {
    padding: 2px;
    margin-left: 2px;
    font-size: .8rem;
    border: 1px solid black;
    border-radius: 5px;
    vertical-align: middle;
  }
  .data {
    display: inline-block;
    max-width: 400px;
    white-space: nowrap;
    overflow: hidden;
    text-overflow: ellipsis;
    vertical-align: middle;
  }
  .data-type {color: rgba(0, 0, 0, 0.5);}
  .hexstring-type {}
  .string-type {background-color: #a2faa3;}
  .int32-type {background-color: #92C9B1;}
  .uint32-type {background-color: #F5B700;}
  .int64-type {background-color: #A599B5;}
  .uint64-type {background-color: #ce96a6;}
  .bytes-type {background-color: #D7FDF0;}
  .float-type {background-color: #B2FFD6;}
  .bool-type {background-color: #CC5803;}
  td {
    white-space: nowrap;
  }
</style>