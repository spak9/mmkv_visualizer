<script>
	
</script>

<!-- HTML - Flex Child and Container -->
<div class="page-footer">
  <h2>Features</h2>
  <ul>
  	<li>Visualize the most recent key-value pairs, as well as older logged values not available via the native API.</li>
  	<li>Interpret the values in all possible ways, including strings, bytes, ints, floats, and bools.</li>
  	<li>Decrypt MMKV files with the associated <i>.crc</i> file and an AES key</li>
  </ul>
  <h2>Credits</h2>
  <ul>
  	<li><a href="https://qwtel.com/">Florian Klampfer</a>, inspiring me with <a href="https://sqliteviewer.app/"><i>SQLite Viewer</i></a></li>
  	<li><a href="https://pyodide.org/en/stable/">Pyodide</a> for allowing me to write the parser in my favorite language</li>
		<li><a href="https://carbon-components-svelte.onrender.com/">Carbon Components Svelte</a> for the beautiful UI components</li>
		<li>KW & Company for helping me test this application</li>
  </ul>
  <p class="copyright">© Steven Pak 2023</p>
</div>

<!-- Styles -->
<style>
	li {
		margin: 16px auto;
		padding-left: px;
	}
	p {
		align-self: center;
	}
	.page-footer{
	  flex: 0 0 auto;
	  display: flex;
	  align-self: center;
	  flex-direction: column;
	}
	.copyright {
		margin: 16px;
	}
</style>