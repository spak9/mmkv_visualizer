<script>

	/**
	 * Imports
	 */
	import { mmkvParserStore } from './MMKVParserStore.mjs'
	import { hex } from './Util.mjs'
	import MMKVTable from "./MMKVTable.svelte"
	import MMKVCellModal from "./MMKVCellModal.svelte"

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

	// A string filename of the mmkv file user passes in
	let mmkvFileName

	// A string filename of the crc file user passes in
	let crcFileName

	// The `MMKVParser` python instance; coupled with data and allows "decode" API
	let mmkvParser

	// Long string of text representing our `mmkv_parser.py` python code
	let mmkvParserPythonCode

	// Boolean for the MMKVCellModal
	let modalHidden = true

	// A string error/warning message that will presented on the MMKVCellModal
	let errorMessage = ''



	/**
	 *  Functions 
	 */

	// Called during initialization of the component - will load in and set up the
	// global `pyodide` object and prepares the `mmkv_parser.py` code via text.
	// We prepare the code prior because the python __init__ requires data. 
	async function setupPyodideAndCode () {
		pyodide = await loadPyodide()
		await pyodide.loadPackage("cryptography")
		mmkvParserPythonCode = await (await fetch("/mmkv_parser.py")).text()
		console.log('[+] Pyodide and mmkv_parser.py all fetched')
	}

	// Called when user D&Ds or chooses a file(s) to parse. Will parse the file(s)
	// and update a lot of component state
	async function loadFilesIntoMMKVParser(mmkvFile, crcFile) {

		// Reset prior app state value
		mmkvParser = undefined
		mmkvMap = undefined

		let mmkvHexString = undefined
		let crcHexString = undefined

		// Convert File data into a hex string, preparing the `mmkvParser` decoding 
		mmkvHexString = hex(await mmkvFile.arrayBuffer())
		if (crcFile) {
			crcHexString = hex(await crcFile.arrayBuffer())

			// Check if CRC file has "iv" at bytes [12:28] - encrypted file
			console.log(`[+] CRC IV bytes: ${crcHexString.slice(24, 56)}`)

		}

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
		crcFileName = crcFile?.name

		console.log(mmkvMap)
	}

	// Validates and updates state on the mmkv and optional CRC files passed in
	// by the user in the form of an Array of File(s). 
	// Checks whether files were passed in, are "empty"
	// Returns a tuple of [mmkvFile, crcFile], either of which could be null.
	async function inputValidation(dataFiles) {

		// Prepare tuple of files and reset `errorMessage` state for Modal
		let mmkvFile = null
		let crcFile = null
		errorMessage = ''

		// Check number of files passed in
		if (!dataFiles) {
			console.log("[+] User did not input any files")
			errorMessage = 'User did not input any files'
		}
		else if (dataFiles.length > 2) {
			console.log(`[+] User inputted ${dataFiles.length} files`)
			errorMessage  = `User inputted ${dataFiles.length} files. Please input either
											 the MMKV file alone, or both the MMKV file and the accompanying
											 .crc file.`
		}
		else if (dataFiles.length == 1) {
			// MMKV File
			console.log('[+] User passed in 1 file')
			mmkvFile = dataFiles[0]

			// Check if the MMKV file is "empty", that is, null bytes
			let isEmpty = parseInt(hex(await mmkvFile.arrayBuffer()), 16)
			console.log(isEmpty)
			if (isEmpty == 0 || isNaN(isEmpty)) {
				errorMessage = `"${mmkvFile.name}" is an empty database`
				mmkvFile = null
			}
		}
		else if (dataFiles.length == 2) {
			// MMKV file and CRC file
			console.log('[+] User passed in 2 files')
			for (let file of dataFiles) {
				console.log(file.name)
				if (file.name.endsWith(".crc")) {
					console.log("[+] Found crc file")
					crcFile = file
				}
				else {
					mmkvFile = file
					let isEmpty = parseInt(hex(await mmkvFile.arrayBuffer()), 16)
					if (isEmpty == 0 || isNaN(isEmpty)) {
						errorMessage = `"${mmkvFile.name}" is an empty database.`
						mmkvFile = null
					}
				}
			}
			if (!crcFile) {
				console.log("[+] User passed in 2 files, but 1 is not .crc")
				errorMessage = `User passed in 2 files, but 1 is not a .crc file. 
												Please pass in either the MMKV file alone, or both files including the accompanying .crc file.`
				mmkvFile = null
				crcFile = null
			}
		}

		return [mmkvFile, crcFile]
	}

	async function onDrop(e) {
		e.preventDefault()

		// Perform input validation on the files the user inputs in
		const [mmkvFile, crcFile] = await inputValidation(e.dataTransfer.files)

		// If a concrete MMKV file is returned, load it into the MMKVParser, else pop error Modal up
		if (mmkvFile) {
			await loadFilesIntoMMKVParser(mmkvFile, crcFile)
			}
		else {
			modalHidden = false
		}

		// Turn off highlighting
		active = false
	}

	function onDragOver(e) {
		e.preventDefault()

		// Turn on highlighting
		active = true
	}

	async function onChange(e) {
		// Perform input validation on the files the user inputs in
		const [mmkvFile, crcFile] = await inputValidation(e.target.files)

		// If a concrete MMKV file is returned, load it into the MMKVParser, else pop error Modal up
		if (mmkvFile) {
			await loadFilesIntoMMKVParser(mmkvFile, crcFile)
		}
		else {
			modalHidden = false
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
	    	<input on:change={onChange} type="file" id="mmkv-input" multiple hidden>
	      <label for="mmkv-input">Open File</label>
    		<button><a href='/data_all_types' download>Download Sample Data</a></button>
	    </div>
	  </div>
	  <MMKVTable mmkvMap={mmkvMap}/>
	{/await}
</div>

<MMKVCellModal 
  bind:hidden={modalHidden} 
  content={errorMessage} 
  subject={"Error"}/>


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
		text-align: center;
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
