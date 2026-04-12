<script lang="ts">
	import type { SacramentTrend } from '$lib/api';

	interface Props {
		trends: SacramentTrend[];
	}

	let { trends }: Props = $props();

	const sacramentTypes = [
		{ key: 'baptism', label: 'Baptism', color: 'var(--chart-1)' },
		{ key: 'first_communion', label: 'First Communion', color: 'var(--chart-2)' },
		{ key: 'confirmation', label: 'Confirmation', color: 'var(--chart-3)' },
		{ key: 'marriage', label: 'Marriage', color: 'var(--chart-4)' },
		{ key: 'holy_orders', label: 'Holy Orders', color: 'var(--chart-5)' }
	] as const;

	let maxValue = $derived(
		Math.max(
			...trends.flatMap((t) => [
				t.baptism,
				t.first_communion,
				t.confirmation,
				t.marriage,
				t.holy_orders
			]),
			1
		)
	);

	function getHeight(value: number): number {
		return (value / maxValue) * 100;
	}
</script>

<div class="bg-white rounded-lg shadow p-6">
	<h3 class="text-lg font-medium text-gray-900 mb-4">Sacrament Trends (Last 5 Years)</h3>

	{#if trends.length === 0}
		<p class="text-gray-500 text-sm">No sacrament data available</p>
	{:else}
		<!-- Legend -->
		<div class="flex flex-wrap gap-4 mb-6">
			{#each sacramentTypes as type}
				<div class="flex items-center gap-2">
					<div class="w-3 h-3 rounded" style="background-color: {type.color}"></div>
					<span class="text-xs text-gray-600">{type.label}</span>
				</div>
			{/each}
		</div>

		<!-- Chart -->
		<div class="relative">
			<!-- Y-axis labels -->
			<div
				class="absolute left-0 top-0 bottom-8 w-8 flex flex-col justify-between text-xs text-gray-500"
			>
				<span>{maxValue}</span>
				<span>{Math.round(maxValue / 2)}</span>
				<span>0</span>
			</div>

			<!-- Chart area -->
			<div class="ml-10 overflow-x-auto">
				<div class="flex gap-2 min-w-max" style="height: 200px;">
					{#each trends as trend}
						<div class="flex flex-col items-center">
							<!-- Bars container -->
							<div class="flex gap-1 items-end h-full pb-2">
								{#each sacramentTypes as type}
									{@const value = trend[type.key]}
									<div
										class="w-4 rounded-t transition-all duration-300 hover:opacity-80"
										style="height: {getHeight(
											value
										)}%; background-color: {type.color}; min-height: {value > 0 ? '4px' : '0'};"
										title="{type.label}: {value}"
									></div>
								{/each}
							</div>
							<!-- Year label -->
							<span class="text-xs text-gray-600 mt-1">{trend.year}</span>
						</div>
					{/each}
				</div>
			</div>
		</div>

		<!-- Totals table -->
		<div class="mt-6 overflow-x-auto">
			<table class="w-full text-sm">
				<thead>
					<tr class="border-b">
						<th class="text-left py-2 text-gray-600 font-medium">Year</th>
						{#each sacramentTypes as type}
							<th class="text-center py-2 text-gray-600 font-medium">{type.label}</th>
						{/each}
					</tr>
				</thead>
				<tbody>
					{#each trends as trend}
						<tr class="border-b">
							<td class="py-2 font-medium">{trend.year}</td>
							{#each sacramentTypes as type}
								<td class="text-center py-2">{trend[type.key]}</td>
							{/each}
						</tr>
					{/each}
				</tbody>
			</table>
		</div>
	{/if}
</div>
