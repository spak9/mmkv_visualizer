<script>
	
</script>

<!-- HTML - Flex Child and Container -->
<div class="page-footer">
  <h2>Features</h2>
  <ul>
  	<li>Visualize the most recent key-value pairs, as well as older logged values not available via the native API.</li>
  	<li>Interpret the values in all possible ways, including strings, bytes, ints, floats, and NSCoding.</li>
  	<li>Decrypt MMKV files with the associated <i>.crc</i> file and an AES key</li>
		<li>Experiment with data and build up your own defined schema</li>
  </ul>
	<h2>Support Matrix</h2>
	<ul>
		<li>Only MMKV databases that use <a href="https://github.com/Tencent/MMKV/releases/tag/v1.2.16">v1.2.x</a> can successfully be visualized. I am currently working on parsers for the new versions.</li>
	</ul>
  <h2>Credits</h2>
  <ul>
  	<li><a href="https://qwtel.com/">Florian Klampfer</a>, inspiring me with <a href="https://sqliteviewer.app/"><i>SQLite Viewer</i></a></li>
  	<li><a href="https://pyodide.org/en/stable/">Pyodide</a> for allowing me to write the parser in my favorite language</li>
		<li><a href="https://carbon-components-svelte.onrender.com/">Carbon Components Svelte</a> for the beautiful UI components</li>
		<li>KW & Company for helping test this application</li>
  </ul>
  <p class="copyright">© Steven Pak 2026</p>
</div>

<!-- Styles -->
<style>
	li {
		margin: 16px auto;
		padding-left: 0;
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