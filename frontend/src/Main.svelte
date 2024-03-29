<script>

	/**
	 * Imports
	 */
	import { mmkvParserStore } from './MMKVParserStore.mjs'
	import { hex } from './Util.mjs'
	import MMKVTable from "./MMKVTable.svelte"
	import MMKVCellModal from "./MMKVCellModal.svelte"
	import { FileUploaderButton, Button, Loading } from 'carbon-components-svelte';
	import { OverflowMenu, OverflowMenuItem } from "carbon-components-svelte";

	/**
	 * State
	 */

 	// A bool for whether ".page_main" should be highlighted
	let active = false				

	// The Pyodide Interface for running python code - singleton
	let pyodide = undefined;

	// A native JavaScript "Map[string, Array[UInt8Array]]" map that will hold
	// the result of decoding the MMKV File via `mmkv_parser.py`
	let mmkvMap = undefined;

	// An instance of the "MMKVTable" svelte component
	let mmkvTable = undefined;

	// A string filename of the mmkv file user passes in
	let mmkvFileName = undefined;

	// A string filename of the crc file user passes in
	let crcFileName = undefined;

	// The `MMKVParser` python instance; coupled with data and allows "decode" API
	let mmkvParser = undefined;

	// Long string of text representing our `mmkv_parser.py` python code - needs to be loaded
	// into the `mmkvParser` object
	let mmkvParserPythonCode = undefined;

	// Boolean for the MMKVCellModal
	let modalHidden = true;

	// String content that will be presented on the MMKVCellModal
	let modalContent = '';

	// String subject that will be presented on the MMKVCellModal
	let modalSubject = '';

	// String for the AES key in hex
	let aesKey = undefined;

	// String for the iV in hex
	let iv = undefined;


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
		iv = undefined

		let mmkvHexString = undefined
		let crcHexString = undefined
		let isEncrypted = undefined
		let constructorCode = undefined

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

		// Instantiate our MMKVParser instance with ALL the necessary data - ready to be used!
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

		// No Files passed in
		if (!dataFiles) {
			console.log("[+] User did not input any files")
			modalContent = 'User did not input any files'
		}

    // 3 or more files passed in
		else if (dataFiles.length > 2) {
			console.log(`[+] User inputted ${dataFiles.length} files`)
			modalContent  = `User inputted ${dataFiles.length} files. Please input either
											 the MMKV file alone, or both the MMKV file and the accompanying
											 .crc file.`
		}

    // 1 file passed in
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

    // 2 files passed in
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
												Please pass in either the MMKV file alone, or both the MMKV file and the accompanying .crc file.`
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
		aesKey = e.detail.aesKey
		try {
			mmkvParser.decrypt_and_reconstruct(aesKey)
			mmkvMap = mmkvParser.decode_into_map().toJs()
			modalHidden = true
		}
		catch (err) {
			modalSubject = 'Error'
			modalContent = `The following AES key "${aesKey}" did not work. Is it a hexstring?`
			modalHidden = false
		}	
	}

	// A callback when the user drops a file(s) on the dropzone
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

	/**
	 * Event handler function for "change" event for <input type=file>
	 * 
	 * @param e the CustomEvent object in which detail contains the array of Files.
	 */
	async function onChange(e) {
    console.log(e.detail);
		// Perform input validation on the files the user inputs in
		const [mmkvFile, crcFile] = await inputValidation(e.detail)

		// If a concrete MMKV file is returned, load it into the MMKVParser, else pop error Modal up
		if (mmkvFile) {
			await loadFilesIntoMMKVParser(mmkvFile, crcFile)
		}
		else {
			modalHidden = false
		}
	}
	
	/**
	 * Event handler when the user clicks on the OverflowMenuItem for "View metadata"
	 * 
	 * @param e PointerEvent object
	 */
	function viewMetadata(e) {
		console.log("[+] viewMetadata")

		// Update modal content display metadata regarding the decoding 
		let db_size = mmkvParser._get_db_size() ?? "0 - using best effort parsing!";
		modalSubject = 'MMKV Metadata';
		modalContent = `MMKV Filename: ${mmkvFileName}\n \
										MMKV Database Size: ${db_size}\n \
										CRC Filename: ${crcFileName ?? "N/A"}\n \
										AES Key (hex): ${aesKey ?? "N/A"}\n \
										IV (hex): ${iv ?? "N/A"}`;
		modalHidden = false;
	}

	/**
	 * Event handler when the user clicks on the OverflowMenuItem for "View schema"
	 * @param e
	 */
	function viewSchema(e) {
		console.log("[+] viewSchema");

		// Update modal content to display the schema
		modalSubject = 'MMKV User-defined Python Schema';
		modalContent = mmkvTable.getSchema();
		modalHidden = false;
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
		<div class="loading-box">
			<Loading description="Setting up MMKVParser" withOverlay={false} small/>
		</div>
	{:then}
	  <div class="instructions">
	  	{#if mmkvMap?.size === undefined} 
	  		<p>Drag & drop or select an MMKV file to visualize.<br>
          Encrypted files must be accompanied with their <i>.crc</i> file.</p>
	    {/if}
			<div class="main-buttons">
				<FileUploaderButton multiple size="field" kind="tertiary" labelText="Open File(s)" disableLabelChanges={true}
					on:change={onChange} />
				<Button size="field" kind="tertiary" href="/data_all_types">Download Sample Data</Button>
				{#if mmkvMap}
					<OverflowMenu>
						<OverflowMenuItem text="View metadata" on:click={viewMetadata}/>
						<OverflowMenuItem text="View schema" on:click={viewSchema}/>
					</OverflowMenu>
				{/if}
	    </div>
	  </div>
	  {#if mmkvMap?.size} 
	  	<MMKVTable mmkvMap={mmkvMap} bind:this={mmkvTable}/>
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
	.page-main {
	  /* Flex Container */
	  display: flex;
	  flex-direction: column;
	  justify-content: center;
	  align-items: center;
	  border-style: dashed;
	  border-width: 1.5px;
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
    width: 50%;
		text-align: center;
    flex: 0 0 auto;
    margin: 16px;   
	}

	.main-buttons{
    margin: 16px;
    display: flex;
    flex-wrap: wrap;
    justify-content: space-evenly;
	}
	.loading-box {
		margin: 16px;
	}

</style>
