<script lang="ts">
	import type { Sacrament, SacramentType } from '$lib/api';

	interface Props {
		sacraments: Sacrament[];
	}

	let { sacraments }: Props = $props();

	const sacramentAbbreviations: Record<SacramentType, string> = {
		baptism: 'B',
		first_communion: 'FC',
		confirmation: 'C',
		marriage: 'M',
		holy_orders: 'HO'
	};

	const sacramentColors: Record<SacramentType, string> = {
		baptism: 'bg-blue-100 text-blue-800',
		first_communion: 'bg-purple-100 text-purple-800',
		confirmation: 'bg-green-100 text-green-800',
		marriage: 'bg-pink-100 text-pink-800',
		holy_orders: 'bg-amber-100 text-amber-800'
	};

	const sacramentLabels: Record<SacramentType, string> = {
		baptism: 'Baptism',
		first_communion: 'First Communion',
		confirmation: 'Confirmation',
		marriage: 'Marriage',
		holy_orders: 'Holy Orders'
	};

	const uniqueSacramentTypes = $derived(
		[...new Set(sacraments.map((s) => s.sacrament_type))].sort((a, b) => {
			const order: SacramentType[] = [
				'baptism',
				'first_communion',
				'confirmation',
				'marriage',
				'holy_orders'
			];
			return order.indexOf(a) - order.indexOf(b);
		})
	);
</script>

<div class="flex flex-wrap gap-1">
	{#each uniqueSacramentTypes as sacramentType (sacramentType)}
		<span
			class="inline-flex items-center px-1.5 py-0.5 rounded text-xs font-medium {sacramentColors[
				sacramentType
			]}"
			title={sacramentLabels[sacramentType]}
		>
			{sacramentAbbreviations[sacramentType]}
		</span>
	{/each}
	{#if sacraments.length === 0}
		<span class="text-gray-400 text-xs">-</span>
	{/if}
</div>
