<script>
    import { Copy } from 'carbon-icons-svelte';

	/**
	 * Imports
	 */
	import { createEventDispatcher } from 'svelte';

	/**
	 * State
	 */
	export let hidden = true
	export let content = ''
	export let subject = ''
	let aesKey = ""
	const dispatch = createEventDispatcher();

	/**
	 *  Functions 
	 */
	
	// Will copy the `content` state string into the browser clipboard
	async function copyContent(e) {
    e.stopPropagation()
    console.log("[+] Copy Content")
    navigator.clipboard.writeText(content).then(
      () => {
        console.log('[+] Copied content')
      },
      () => {
        console.log('[+] Copy failed')
      })
  }

  // Will dispatch a custom event called "sendAesKey", which will
  // hold the `aesKey` hexstring from the user.
  function sendAesKey() {
  	console.log(`[+] AES Key: ${aesKey}`)
  	dispatch('sendAesKey', {
  		aesKey: aesKey
  	})
  }

  // Will reset all the props to default.
  function exit() {
  	console.log('[+] Reset props from MMKVCellModal')
  	hidden = true
  }
  
</script>


<!-- HTML -->
<div class="modal" class:hidden>
	<span class="subject">{subject}</span>
  <span on:click={copyContent}>
    <Copy class="carbon-icons"/>
  </span>
	<hr>
	<span>{content}</span>

	{#if subject == "Encrypted MMKV Database"}
		<br><br>
		<label for="aes-key">Please enter your AES key in the form of a hexstring:</label>
		<input bind:value={aesKey} type="text" id="aes-key" name="aes-key">
		<br>
		<button on:click={sendAesKey}>Decrypt</button>
	{/if}
</div>

<div class="overlay" class:hidden on:click={exit}></div>


<!-- Styling -->
<style>
	span { white-space: pre-line; }
	.modal {
		padding: 16px;
		width: 60vw;
		height: 70vh;
		background-color: white;
  	border: 1px solid #ddd;
  	border-radius: 15px;
  	position: absolute;
  	top: 20%;
  	right: 20%;
  	z-index: 2;
  	overflow-y: auto;
    overflow-wrap: break-word;
	}
	.overlay {
	  position: fixed;
	  top: 0;
	  bottom: 0;
	  left: 0;
	  right: 0;
	  width: 100%;
	  height: 100%;
	  background: rgba(0, 0, 0, 0.5);
	  backdrop-filter: blur(3px);
	  z-index: 1;
	}
	.hidden {
		display: none;
	}
	.subject {
		margin-right: 8px;
		color: rgba(0, 0, 0, 0.5);
	}
</style>