<script>

	import { hex } from './Util.mjs'
	import MMKVCell from './MMKVCell.svelte'
	export let mmkvMap				// Native JavaScript Map of "Map[str, Array[UInt8Array]]"

	// Internal mapping of the key-value pair data interpretation of only the FIRST of all the values.
	// eg: {"my_key": "string", "userid": "uint32"}
	let recentCellMapping = {};
	for (const key in mmkvMap) {
		recentCellMapping[key] = undefined;
	}

	export function getSchema() {
		let schema = {};
		for (const key in recentCellMapping) {
			// Only populate non default "hexstring-type"
			if (recentCellMapping[key].getDataType() != 'hexstring-type') {
				// Get the type without the "-type"
				// eg. 'string-type' --> 'string'
				schema[key] = recentCellMapping[key].getDataType().slice(0, -5);
			}
		}
		return JSON.stringify(schema, null, '\t');
	}

</script>


<!-- HTML -->
{#if mmkvMap}
	<div class="table-wrapper">
		<table>
			<tr>
				<th id="keys-header">Key</th>
				<th id="values-header" colspan="100%">Values</th>
			</tr>
			{#each [...mmkvMap] as [stringKey, arrayValue]}
				<tr>
					<td>{stringKey}</td>
					<!-- Create MMKVCell per forensic value, 0th being most recent -->
					{#each arrayValue as value, i}
						{#if i === 0}
							<MMKVCell hexstring={hex(value)} bind:this={recentCellMapping[stringKey]}/>
						{:else}
							<MMKVCell hexstring={hex(value)}/>
						{/if}
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