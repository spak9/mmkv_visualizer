<svelte:head>
  <script src="https://cdn.jsdelivr.net/pyodide/v0.20.0/full/pyodide.js"></script>
  <script type="text/javascript" src="/parse.js"></script>
</svelte:head>


<script>


</script>


<!-- Header -->
<div class="page-header">
  <div class="nav-intro">
    <h1>
      MMKV Visualizer
    </h1>
    <p>View MMKV databases online - completely transparent & private.</p>
  </div>
  <div class="nav-links">
    <a class="github-link" href="https://github.com/spak9/mmkv_visualizer">
      <svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 438.5 438.5"><path d="M409.1 114.6c-19.6-33.6-46.2-60.2-79.8-79.8C295.7 15.2 259.1 5.4 219.3 5.4c-39.8 0-76.5 9.8-110.1 29.4 -33.6 19.6-60.2 46.2-79.8 79.8C9.8 148.2 0 184.9 0 224.6c0 47.8 13.9 90.7 41.8 128.9 27.9 38.2 63.9 64.6 108.1 79.2 5.1 1 8.9 0.3 11.4-2 2.5-2.3 3.7-5.1 3.7-8.6 0-0.6 0-5.7-0.1-15.4 -0.1-9.7-0.1-18.2-0.1-25.4l-6.6 1.1c-4.2 0.8-9.5 1.1-15.8 1 -6.4-0.1-13-0.8-19.8-2 -6.9-1.2-13.2-4.1-19.1-8.6 -5.9-4.5-10.1-10.3-12.6-17.6l-2.9-6.6c-1.9-4.4-4.9-9.2-9-14.6 -4.1-5.3-8.2-8.9-12.4-10.8l-2-1.4c-1.3-1-2.6-2.1-3.7-3.4 -1.1-1.3-2-2.7-2.6-4 -0.6-1.3-0.1-2.4 1.4-3.3 1.5-0.9 4.3-1.3 8.3-1.3l5.7 0.9c3.8 0.8 8.5 3 14.1 6.9 5.6 3.8 10.2 8.8 13.8 14.8 4.4 7.8 9.7 13.8 15.8 17.8 6.2 4.1 12.4 6.1 18.7 6.1 6.3 0 11.7-0.5 16.3-1.4 4.6-1 8.8-2.4 12.8-4.3 1.7-12.8 6.4-22.6 14-29.4 -10.8-1.1-20.6-2.9-29.3-5.1 -8.7-2.3-17.6-6-26.8-11.1 -9.2-5.1-16.9-11.5-23-19.1 -6.1-7.6-11.1-17.6-15-30 -3.9-12.4-5.9-26.6-5.9-42.8 0-23 7.5-42.6 22.6-58.8 -7-17.3-6.4-36.7 2-58.2 5.5-1.7 13.7-0.4 24.6 3.9 10.9 4.3 18.8 8 23.8 11 5 3 9.1 5.6 12.1 7.7 17.7-4.9 36-7.4 54.8-7.4s37.1 2.5 54.8 7.4l10.8-6.8c7.4-4.6 16.2-8.8 26.3-12.6 10.1-3.8 17.8-4.9 23.1-3.1 8.6 21.5 9.3 40.9 2.3 58.2 15 16.2 22.6 35.8 22.6 58.8 0 16.2-2 30.5-5.9 43 -3.9 12.5-8.9 22.5-15.1 30 -6.2 7.5-13.9 13.9-23.1 19 -9.2 5.1-18.2 8.9-26.8 11.1 -8.7 2.3-18.4 4-29.3 5.1 9.9 8.6 14.8 22.1 14.8 40.5v60.2c0 3.4 1.2 6.3 3.6 8.6 2.4 2.3 6.1 3 11.3 2 44.2-14.7 80.2-41.1 108.1-79.2 27.9-38.2 41.8-81.1 41.8-128.9C438.5 184.9 428.7 148.2 409.1 114.6z"/>
      </svg>
    </a>
  </div>
</div>

<!-- Main -->
<div class="page-main">
  <div class="instructions">
    <p>Drag & drop or select an MMKV file to visualize</p>
    <div class="main-buttons">
      <label for="mmkv-input">Open File</label>
      <input type="file" id="mmkv-input" hidden>
      <button>Open Sample Data</button>
    </div>
  </div>
</div>

<!-- Footer -->
<div class="page-footer">
  <h1>Features</h1>
  <p class="text">- Visualize the most recent key-value pairs, as well as older logged values not available via the API.</p>
  <p class="text">- Interpret the values in all possible ways, including strings, bytes, ints, floats, and bools.</p>
</div>


<style>
  .logo {
    height: 6em;
    padding: 1.5em;
    will-change: filter;
  }
  .logo:hover {
    filter: drop-shadow(0 0 2em #646cffaa);
  }
  .logo.svelte:hover {
    filter: drop-shadow(0 0 2em #ff3e00aa);
  }
  .read-the-docs {
    color: #888;
  }
</style>
