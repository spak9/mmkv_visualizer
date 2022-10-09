<script>

	import { hex } from './Util.mjs'
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
						<td data-hexstring={hex(value)}>{hex(value)}</td>
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