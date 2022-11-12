<script>

	export let hidden = true
	export let content
	export let subject

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
</script>


<!-- HTML -->
<div class="modal" class:hidden={hidden}>
	<span class="subject">{subject}</span>
	<span class="material-icons md-18" on:click={copyContent}>content_copy</span>
	<hr>
	<span>{content}</span>
</div>

<div class="overlay" class:hidden={hidden} on:click={() => hidden = true}>
	
</div>


<!-- Styling -->
<style>
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