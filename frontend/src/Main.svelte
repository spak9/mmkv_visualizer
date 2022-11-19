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

	// String content that will be presented on the MMKVCellModal
	let modalContent = ''

	// String subject that will be presented on the MMKVCellModal
	let modalSubject = ''


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
		mmkvFileName = mmkvFile.name
		crcFileName = crcFile?.name

		let mmkvHexString = undefined
		let crcHexString = undefined
		let isEncrypted = undefined
		let constructorCode = undefined
		let iv = undefined

		// Convert File(s) data into a hexstring(s), preparing the `mmkvParser` decoding 
		mmkvHexString = hex(await mmkvFile.arrayBuffer())
		if (crcFile) {
			crcHexString = hex(await crcFile.arrayBuffer())

			// Check if CRC file has "iv" at bytes [12:28] - encrypted file
			iv = crcHexString.slice(24, 56)
			isEncrypted = parseInt(iv, 16)
		}

		// Prepare correct constructor
		if (crcHexString) {
			constructorCode = `mmkv_parser = MMKVParser("${mmkvHexString}", "${crcHexString}")`
		}
		else {
			constructorCode = `mmkv_parser = MMKVParser("${mmkvHexString}")`
		}
		let pythonCode = `
${mmkvParserPythonCode}
${constructorCode}
mmkv_parser`

		// Instantiate our MMKVParser instance with ALL the neccesary data - ready to be used!
		mmkvParser = pyodide.runPython(pythonCode)
		mmkvParserStore.set(mmkvParser)

		// Use MMKVParser to decode - if encrypted, prompt for key, else decode_into_map() immediately
		if (isEncrypted != 0 && !isNaN(isEncrypted))  {
			modalSubject = 'Encrypted MMKV Database'
			modalContent = `The following MMKV database "${mmkvFileName}" is encrypted with the following hexstring IV "${iv}".`
			modalHidden = false
		}
		else {
			mmkvMap = mmkvParser.decode_into_map().toJs()
			if (mmkvMap?.size == 0) {
				modalSubject = "Error"
				modalContent = `The MMKV Map size was 0 - most likely NOT an MMKV file or is an encrypted file.`
				modalHidden = false
			}
		}
	}

	// Validates and updates state on the mmkv and optional CRC files passed in
	// by the user in the form of an Array of File(s). 
	// Checks whether files were passed in, are "empty"
	// Returns a tuple of [mmkvFile, crcFile], either of which could be null.
	async function inputValidation(dataFiles) {

		// Prepare tuple of files and reset `modalContent` state for Modal
		let mmkvFile = null
		let crcFile = null
		modalContent = ''
		modalSubject = 'Error'

		// Check number of files passed in
		if (!dataFiles) {
			console.log("[+] User did not input any files")
			modalContent = 'User did not input any files'
		}
		else if (dataFiles.length > 2) {
			console.log(`[+] User inputted ${dataFiles.length} files`)
			modalContent  = `User inputted ${dataFiles.length} files. Please input either
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
				modalContent = `"${mmkvFile.name}" is an empty database`
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
						modalContent = `"${mmkvFile.name}" is an empty database.`
						mmkvFile = null
					}
				}
			}
			if (!crcFile) {
				console.log("[+] User passed in 2 files, but 1 is not .crc")
				modalContent = `User passed in 2 files, but 1 is not a .crc file. 
												Please pass in either the MMKV file alone, or both files including the accompanying .crc file.`
				mmkvFile = null
				crcFile = null
			}
		}

		return [mmkvFile, crcFile]
	}

	// A callback for the "sendAesKey" event from the `MMKVCellModal` component.
	// Will attempt to decrypt and reconstruct the encrypted mmkv file with the extracted key
	// and decode the file for visualization.
	// Will pop up the modal if there is a Pyodide "PythonError".
	function onSendAesKey(e) {
		console.log('[+] User inputted hexstring key -- attempt decryption with hexstring key')
		let key = e.detail.aesKey
		try {
			mmkvParser.decrypt_and_reconstruct(e.detail.aesKey)
			mmkvMap = mmkvParser.decode_into_map().toJs()
			modalHidden = true
		}
		catch (err) {
			modalSubject = 'Error'
			modalContent = `The following AES key "${key}" did not work. Is it a hexstring?`
			modalHidden = false
		}	
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
	  	{#if mmkvMap?.size}
	  		<p>Parsing "{mmkvFileName}" File</p>
	  	{:else} 
	  		<p>Drag & drop or select an MMKV file to visualize.<br>
	  				Encrypted files must be accompanied with their <i>.crc</i> file.</p>
	    {/if}
	    <div class="main-buttons">
	    	<input on:change={onChange} type="file" id="mmkv-input" multiple hidden>
	      <label for="mmkv-input">Open File</label>
    		<button><a href='/data_all_types' download>Download Sample Data</a></button>
	    </div>
	  </div>

	  {#if mmkvMap?.size} 
	  	<MMKVTable mmkvMap={mmkvMap}/>
	  {/if}
	{/await}
</div>

<MMKVCellModal 
	on:sendAesKey={onSendAesKey}
  bind:hidden={modalHidden} 
  bind:content={modalContent} 
  bind:subject={modalSubject}/>


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
