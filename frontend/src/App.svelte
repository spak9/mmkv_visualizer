<script>

  /**
   * Imports
   */
  import Header from './Header.svelte'
  import Main from './Main.svelte'
  import Footer from './Footer.svelte'
  import "carbon-components-svelte/css/all.css";

  // 5 default themes from Carbon - reactively allow theme updates
  let theme = "g10"; // "white" | "g10" | "g80" | "g90" | "g100"
  $: document.documentElement.setAttribute("theme", theme)

</script>


<Header/>
<Main/>
<Footer/>


<style>

</style>
