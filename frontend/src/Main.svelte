<script>

	import { mmkvParserStore } from './MMKVParserStore.mjs'
	import MMKVTable from "./MMKVTable.svelte"
	import { hex } from './Util.mjs'

	let active = false				// A bool for whether ".page_main" should be highlighted
	let pyodide
	let mmkvMap
	let mmkvFileName					// A string filename of the file user passes in
	let mmkvParser
	let mmkvParserPythonCode

	// Prepare functionality for converting [ArrayBuffer] to hex string
	const byteToHex = [];
	for (let n = 0; n <= 0xff; ++n)
	{
	    const hexOctet = n.toString(16).padStart(2, "0");
	    byteToHex.push(hexOctet);
	}

	/* Functions */

	// Called when initialization of the component - will load in and set up the
	// global "pyodide" object and prepares the `mmkv_parser.py` code via text.
	// We prepare the code prior because the __init__ requires data. 
	async function setupPyodideAndCode () {
		pyodide = await loadPyodide()
		mmkvParserPythonCode = await (await fetch("/mmkv_parser.py")).text()
	}

	async function loadFileIntoMMKVParser(mmkvFile) {
		// Reset prior MMKV values, if any
		mmkvParser = undefined
		mmkvMap = undefined
		let mmkvHexString = hex(await mmkvFile.arrayBuffer())

		let init = `mmkv_parser = MMKVParser("${mmkvHexString}")`
		let code = `
${mmkvParserPythonCode}
${init}
mmkv_parser`

		mmkvParser = pyodide.runPython(code)
		mmkvParserStore.set(mmkvParser)
		mmkvMap = mmkvParser.decode_into_map().toJs()
		mmkvFileName = mmkvFile.name
		console.log(mmkvMap)
	}

	// Callback when the user drops a file 
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

	async function onClickSampleData(e) {
		// let mmkvFile = await (await fetch('/data_all_types')).arrayBuffer()
		// await loadFileIntoMMKVParser(mmkf)
		window.location.assign('/data_all_types')
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
	    <p>Drag & drop or select an MMKV file to visualize</p>
	    <div class="main-buttons">
	      <label for="mmkv-input">Open File</label>
      	<button >Open Sample Data</button>
	    </div>
	  </div>
	  {#if mmkvFileName}
	  	<h4>Parsing "{mmkvFileName}"</h4>
	  {/if}
	  <MMKVTable mmkvMap={mmkvMap}/>
	{/await}
</div>


<!-- Styles -->
<style>
	.page-main {
	  /* Flex Container */
	  display: flex;
	  flex-direction: column;
	  justify-content: center;
	  align-items: center;
	  border-style: dashed;
	  border-width: 2px;
	  border-radius: 16px;
	  height: 80%;            /* Used to make sure table doesn't make div taller */
	  margin: 16px;

	  /* Flex Items */
	  flex: 0 0 80%;
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
