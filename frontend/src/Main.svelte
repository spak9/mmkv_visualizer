<script>

	/* Functions */
	async function onDrop(e) {
		e.preventDefault()
		let data = await e.dataTransfer.files[0].arrayBuffer()
		console.log(data)
	}

	function onDragOver(e) {
		e.preventDefault()
	}
	
</script>

<!-- HTML - Flex Child and Container -->
<div class="page-main" on:drop={onDrop} on:dragover={onDragOver}>
  <div class="instructions">
    <p>Drag & drop or select an MMKV file to visualize</p>
    <div class="main-buttons">
      <label for="mmkv-input">Open File</label>
      <input type="file" id="mmkv-input" hidden>
      <button>Open Sample Data</button>
    </div>
  </div>
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

	.table-wrapper {
	  flex: 1 0 80%;
	  width:  100%;
	  overflow: auto;
	  padding: 16px; 
	}

	table {
  border-collapse: collapse;
  border: 2px solid rgb(200,200,200);
  letter-spacing: 1px;
  font-size: 0.8rem;
  empty-cells: hide;
  align-self: flex-start;
  width: 100%;
}

	td, th {
	  border: 1px solid rgb(190,190,190);
	  padding: 10px 20px;
	}

	th {
	  background-color: rgb(235,235,235);
	}

	td {
	  text-align: left;
	}

	tr:nth-child(even) td {
	  background-color: rgb(250,250,250);
	}

	tr:nth-child(odd) td {
	  background-color: rgb(245,245,245);
	}
</style>
