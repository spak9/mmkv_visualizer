<script>

	import { hex } from './Util.mjs'
	import MMKVCell from './MMKVCell.svelte'
	export let mmkvMap				// Native JavaScript Map of "Map[str, Array[UInt8Array]]"

</script>


<!-- HTML -->
{#if mmkvMap}
	<div class="table-wrapper">
		<table>
			<tr>
				<th id="keys-header">Keys</th>
				<th id="values-header" colspan="100%">Values</th>
			</tr>
			{#each [...mmkvMap] as [stringKey, arrayValue]}
				<tr>
					<td>{stringKey}</td>
					{#each arrayValue as value}
						<MMKVCell hexstring={hex(value)}/>
					{/each}
        </tr>
			{/each}
		</table>
	</div>
{/if}


<!-- Styles -->
<style>
	.table-wrapper {
	  flex: 1 1 80%;
    width: 100%;
	  overflow: auto;
	  padding: 16px; 
	}
	#keys-header {
		width: 20%;
	}
	#values-header {
		width: 80%;
	}
</style>