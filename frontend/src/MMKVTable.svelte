<script>

	import { hex } from './Util.mjs'
	import MMKVCell from './MMKVCell.svelte'
	export let mmkvMap		// Native JavaScript Map of "Map[str, Array[UInt8Array]]"

</script>


<!-- HTML -->
{#if mmkvMap}
	<div class="table-wrapper">
		<table>
			<tr>
				<th>Keys</th>
				<th colspan="100%">Values</th>
			</tr>

			{#each [...mmkvMap] as [stringKey, arrayValue]}
				<tr>
					<td>{stringKey}</td>

					{#each arrayValue as value}
						<MMKVCell hexstring={hex(value)}/>
					{/each}
			{/each}
		</table>
	</div>
{/if}


<!-- Styles -->
<style>
	.table-wrapper {
	  flex: 1 0 80%;
	  width:  100%;
	  overflow: auto;
	  padding: 16px; 
	}
</style>