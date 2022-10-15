<script>

	/**
	 * Imports
	 */
	import { mmkvParserStore } from './MMKVParserStore.mjs'
	import { hex } from './Util.mjs'
	import MMKVTable from "./MMKVTable.svelte"

	/**
	 * State
	 */

 	// A bool for whether ".page_main" should be highlighted
	let active = false				

	// The Pyodide Interface for running python code - singleton
	let pyodide

	// A native JavaScript "Map[string, Array[UInt8Array]]" map that will hold
	// the result of decoding the MMKV File via `mmkv_parser.py`
	let mmkvMap

	// A string filename of the file user passes in
	let mmkvFileName

	// The `MMKVParser` python instance; coupled with data and allows "decode" API					
	let mmkvParser

	// Long string of text representing our `mmkv_parser.py` python code
	let mmkvParserPythonCode

	/**
	 *  Functions 
	 */

	// Called during initialization of the component - will load in and set up the
	// global `pyodide` object and prepares the `mmkv_parser.py` code via text.
	// We prepare the code prior because the python __init__ requires data. 
	async function setupPyodideAndCode () {
		pyodide = await loadPyodide()
		mmkvParserPythonCode = await (await fetch("/mmkv_parser.py")).text()
		console.log('[+] Pyodide and mmkv_parser.py all fetched')
	}

	// Called when user D&Ds or chooses a file to parse. Will parse the file
	// and update a lot of component state
	async function loadFileIntoMMKVParser(mmkvFile) {

		// Reset prior MMKV values, if any
		mmkvParser = undefined
		mmkvMap = undefined

		// Convert File data into a hex string, preparing the `mmkvParser` decoding 
		let mmkvHexString = hex(await mmkvFile.arrayBuffer())
		let init = `mmkv_parser = MMKVParser("${mmkvHexString}")`
		let code = `
${mmkvParserPythonCode}
${init}
mmkv_parser`

		// Run our prepared python code w/ hex data - update various pieces of state
		mmkvParser = pyodide.runPython(code)
		mmkvParserStore.set(mmkvParser)
		mmkvMap = mmkvParser.decode_into_map().toJs()
		mmkvFileName = mmkvFile.name
		console.log(mmkvMap)
	}

	async function onDrop(e) {
		e.preventDefault()
		if (e.dataTransfer.files) {
			let mmkvFile = event.dataTransfer.files[0]
			await loadFileIntoMMKVParser(mmkvFile)
		}
		active = false
	}

	function onDragOver(e) {
		e.preventDefault()
		active = true
	}

	async function onChange(e) {
		if (e.target.files) {
			let mmkvFile = e.target.files[0]
			await loadFileIntoMMKVParser(mmkvFile)
		}
	}
</script>


<!-- HTML - Flex Child and Container -->
<div class="page-main" class:highlight={active}
		on:dragenter={(e) => active = true}
		on:dragleave={(e) => active = false}
		on:drop={onDrop} 
		on:dragover={onDragOver}>
	{#await setupPyodideAndCode()}
		<h3>Loading MMKV Parser...</h3>
	{:then}
	  <div class="instructions">
	  	{#if mmkvFileName}
	  		<p>Parsing "{mmkvFileName}" File</p>
	  	{:else} 
	  		<p>Drag & drop or select an MMKV file to visualize</p>
	    {/if}
	    <div class="main-buttons">
	    	<input on:change={onChange} type="file" id="mmkv-input" hidden>
	      <label for="mmkv-input">Open File</label>
    		<button><a href='/data_all_types' download>Download Sample Data</a></button>
	    </div>
	  </div>
	  <MMKVTable mmkvMap={mmkvMap}/>
	{/await}
</div>


<!-- Styles -->
<style>
	button > a {
		all:  unset;
	}

	.page-main {
	  /* Flex Container */
	  display: flex;
	  flex-direction: column;
	  justify-content: center;
	  align-items: center;
	  border-style: dashed;
	  border-width: 2px;
	  border-radius: 16px;
	  height: 70%;            /* Used to make sure table doesn't make div taller */
	  margin: 16px;

	  /* Flex Items */
	  flex: 0 0 70%;
	}

	.page-main.highlight {
	  background-color: #E4E6C3;
	}

	.instructions {
	  flex: 0 0 auto;
	  margin: 16px;   
	}

	.main-buttons{
	  display: flex;
	  flex-wrap: wrap;
	  justify-content: space-evenly;
	}

	.main-buttons > * {
	  padding: 10px;
	  background: #ccc;
	  cursor: pointer;
	  border-radius: 5px;
	  border: 1px solid #ccc;
	  margin: 8px;
	  font-size: 1em;
	}

	.main-buttons > *:hover {
	  background: #ddd;
	}
</style>
