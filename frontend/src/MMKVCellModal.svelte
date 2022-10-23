<script>
	export let hidden = true
</script>


<!-- HTML -->
<div class="modal" class:hidden={hidden}>
	<h2>Heyo</h2>
</div>

<div class="overlay" class:hidden={hidden} on:click={() => hidden = true}>
	
</div>


<!-- Styling -->
<style>
	.modal {
		width: 60vw;
		height: 60vh;
		background-color: white;
  	border: 1px solid #ddd;
  	border-radius: 15px;
  	position: absolute;
  	top: 20%;
  	right: 20%;
  	z-index: 2;
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
</style>