<script>

	import { createEventDispatcher } from 'svelte';

	const dispatch = createEventDispatcher();

	export let hidden = true
	export let content
	export let subject
	let aesKey = ""

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

  function sendAesKey() {
  	console.log(`[+] AES Key: ${aesKey}`)
  	dispatch('sendAesKey', {
  		aesKey: aesKey
  	})

  }
  
</script>


<!-- HTML -->
<div class="modal" class:hidden={hidden}>
	<span class="subject">{subject}</span>
	<span class="material-icons md-18" on:click={copyContent}>content_copy</span>
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

<div class="overlay" class:hidden={hidden} on:click={() => hidden = true}>
	
</div>


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
	.subject {color: rgba(0, 0, 0, 0.5);}
</style>