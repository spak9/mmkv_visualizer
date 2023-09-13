<script>

  import MMKVCellModal from './MMKVCellModal.svelte'
  import { mmkvParserStore } from './MMKVParserStore.mjs'
  import { get } from 'svelte/store'
  import Copy from "carbon-icons-svelte/lib/Copy.svelte";
  import FitToHeight from "carbon-icons-svelte/lib/FitToHeight.svelte";

	export let hexstring 		// Hex string representing the data 

  const dataTypes = [
    'hexstring-type', 
    'string-type', 
    'int32-type', 
    'uint32-type',
    'int64-type', 
    'uint64-type', 
    'bytes-type',
    'float-type',
    'bool-type',
    'nsdata_parcelable-type'
    ]

  let expand_hidden = true  // bool for expanding the MMKVCellModal
	let dataTypeIndex	= 0		  // data type index for rotating on click 
  $: dataType = dataTypes[dataTypeIndex % dataTypes.length]

  function interpretHexData(index) {
    let mmkvParser = get(mmkvParserStore)
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
    else if (index % dataTypes.length == 9) {
      return mmkvParser.decode_as_data(hexstring)
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
    expand_hidden = false
  }

  /**
   * A public method on "MMKVCell" that returns the current datatype this cell is being
   * interpreted as.
   * See "dataTypes" constant for all possible values.
   */
  export function getDataType() {
    return dataType;
  }
</script>


<!-- HTML -->
<td class={dataType} on:click={() => dataTypeIndex += 1}>
  <span class="data-type">({dataType.split('-')[0]})</span>
  <span class="data">{interpretHexData(dataTypeIndex) || "N/A"}</span>
  <span on:click={copyContent}><Copy class="carbon-icons"/></span>
  <span on:click={expandContent}><FitToHeight class="carbon-icons" /></span>
</td>

<MMKVCellModal 
  bind:hidden={expand_hidden} 
  content={interpretHexData(dataTypeIndex)} 
  subject={dataType.split('-')[0]}/>


<!-- Styles -->
<style>
  td {
    cursor: pointer;
    white-space: nowrap;
  }
  .data {
    display: inline-block;
    max-width: 400px;
    white-space: nowrap;
    overflow: hidden;
    text-overflow: ellipsis;
    vertical-align: middle;
    margin-right: 4px;
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
  .nsdata_parcelable-type {background-color: #A7CAB1;}
</style>