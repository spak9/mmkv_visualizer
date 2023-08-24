<script>
// @ts-nocheck


	import { hex } from './Util.mjs'
	import { DataTable } from 'carbon-components-svelte'
	import MMKVCell from './MMKVCell.svelte'
	export let mmkvMap				// Native JavaScript Map of "Map[str, Array[UInt8Array]]"

	// TODO - there may be a better way to do this, but on component initialization,
	// get the longest length array from the "mmkvMap" so we know how many "header" columns we need.
	let longest_logged_array = 0;
	for (const [key, val] of mmkvMap.entries()) {
		if (val.length > longest_logged_array) {
			longest_logged_array = val.length;
		}
	}

	// Create "headers" prop for <DataTable> beforehand based on longest logged array
	let header_arr = [];
	header_arr.push({key: "Keys", value: "Keys"});
	for (let i = 1; i <= longest_logged_array; i++) {
		let header_value = `Value ${i}`;
		header_arr.push({ key: header_value, value: header_value});
	}
	console.log(header_arr);


</script>


<!-- HTML -->
<!-- {#if mmkvMap}
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
			{/each}
		</table>
	</div>
{/if} -->

{#if mmkvMap} 
	<!-- need to pass "style" as a $$restProp as I need make size 100% to fill up parent -->
	<!-- See https://carbon-components-svelte.onrender.com/components/DataTable#rest-props -->
	<DataTable
		style="width: 100%; height: 100%"
		headers={header_arr}
		rows={[
			{id: "somekey", key: "somekey", value: "somevalue", value2: "value2"}
		]}
	/>
{/if}



<!-- Styles -->
<style>
	.table-wrapper {
	  flex: 1 1 80%;
	  width:  100%;
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