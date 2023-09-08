<script>
    import { get } from 'svelte/store';

// @ts-nocheck

	import { hex } from './Util.mjs'
	import { DataTable } from 'carbon-components-svelte'
  import { mmkvParserStore } from './MMKVParserStore.mjs';

  // Native JavaScript Map of "Map[str, Array[UInt8Array]]"
	export let mmkvMap	

  // MMKVParser
  let mmkvParser = get(mmkvParserStore);

  // props for <DataTable>
  // Note: Every object in `row_props` must fit the following schema
  // {
  //    id: <key>
  //    key: <key>
  //    type: <mmkv_type>   --> will help decide CSS classing and MMKV data interpretation
  //    type_idx: <int>     --> index into `dataTypes` array
  //    value<x>: <value>   --> Raw MMKV bytes that will be interpreted via the `type` property
  //    hexvalue<x>: <hexvalue>   --> Raw MMKV bytes that will be interpreted via the `type` property in hex form
  // }
  let rows_prop = []; 
  let headers_prop = [];
  let max_columns = 0;

  // MMKV Datatypes you can interpret the data in
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
  const dataTransformationCallbacks = [
    noop,
    mmkvParser.decode_as_string, 
    mmkvParser.decode_as_int32,
    mmkvParser.decode_as_uint32,
    mmkvParser.decode_as_int64, 
    mmkvParser.decode_as_uint64, 
    mmkvParser.decode_as_bytes, 
    mmkvParser.decode_as_float, 
    mmkvParser.decode_as_bool, 
    mmkvParser.decode_as_data
  ]

  // Create "rows" prop for <DataTable>
  for (const [key, valueArr] of mmkvMap.entries()) {
    // 1. Grab longest length array for num of columns
    if (valueArr.length > max_columns) {
      max_columns = valueArr.length;
    }

    // 2. Create a row for every UInt8Array in `valueArr`
    let newRow = valueArr.reduce(function(row, current, idx) {
      row[`value${idx + 1}`] = hex(current);
      return row;
    }, {});

    newRow["id"] = key;
    newRow["key"] = key;
    // On initialization, make sure hexstring is the first type
    newRow["type_idx"] = 0;
    newRow["type"] = dataTypes[newRow["type_idx"]];
    rows_prop.push(newRow);
  }

	// Create "headers" prop for <DataTable> beforehand based on longest logged array
  // Note: Starting loop index at 1, not 0
	headers_prop.push({key: "key", value: "Key"});
	for (let i = 1; i <= max_columns; i++) {
    let header_key = `value${i}`;
		let header_value = `Value ${i}`;
    // eg: [{key: "keys", value: "Keys"}, {key: "value1", value: "Value 1"}]
		headers_prop.push({ key: header_key, value: header_value});
	}

  console.log('[+] all rows');
  console.log(rows_prop);
  console.log(headers_prop)

  /**
   * A callback function in response to the "on:click:row" event.
   * It updates a row's type AND data to display that new interpretation.
   * @param event
   */
  function updateRowTypeAndData(event) {
    let row_data = event.detail;

    // 1. Update the type_idx, type, and value<int>
    row_data["type_idx"] = (row_data["type_idx"] + 1) % dataTypes.length;
    row_data["type"] = dataTypes[row_data["type_idx"]];

    // for (const [key, value] of Object.entries(row_data)) {
    //   if (key.startsWith("value")) {
    //     // Update interpretation
    //     let value = dataTransformationCallbacks[idx](row_data[`hex${key}`]) ?? "N/A";
    //     row_data[key] = value;
    //     console.log(`[+] updating the key ${key} with value ${value}`)
    //   }
    // }
    console.log(`inside updateRowTypeAndData - ${JSON.stringify(row_data)}`);
    rows_prop = rows_prop;
  }

  /**
   * A no-op function.. 
   * TODO - get rid of this haha
   * @param hexstring
   */
  function noop(hexstring) {
    console.log("here");
    return hexstring;
  }

</script>


<!-- HTML -->
<!-- need to pass "style" as a $$restProp as I need make size 100% to fill up parent -->
<!-- See https://carbon-components-svelte.onrender.com/components/DataTable#rest-props -->
<DataTable
  style="width: 100%; height: 100%; overflow: auto;"
  headers={headers_prop}
  rows={rows_prop}
  on:click:row={updateRowTypeAndData}
>
  <span class={row["type"]} slot="cell" let:cell let:row>
    {#if cell.value === undefined }
      {""}
    {:else if cell.value === row["key"]}
      {cell.value}
    {:else}
      {dataTransformationCallbacks[row.type_idx](cell.value) || "N/A"}
    {/if}
  </span>
  
</DataTable>


<!-- Styles -->
<style>
  span {
    text-decoration: underline;
    text-decoration-thickness: 3px;
    text-decoration-color: pink;
    text-underline-offset: 4px;
  }
  .hexstring-type { text-decoration-color: #e5e5e5}
  .string-type { text-decoration-color: #a2faa3; }
  .int32-type { text-decoration-color: #92C9B1; }
  .uint32-type { text-decoration-color: #F5B700; }
  .int64-type { text-decoration-color: #A599B5; }
  .uint64-type { text-decoration-color: #ce96a6; }
  .bytes-type { text-decoration-color: #D7FDF0; }
  .float-type { text-decoration-color: #B2FFD6; }
  .bool-type { text-decoration-color: #CC5803; }
  .nsdata_parcelable-type { text-decoration-color: #A7CAB1; }
	/* .table-wrapper {
	  flex: 1 1 80%;
	  width:  100%;
	  overflow: auto;
	  padding: 16px; 
	}
	#keys-header {
		width: 20%;
	}
	#values-header {
		width: 80%;
	} */
</style>