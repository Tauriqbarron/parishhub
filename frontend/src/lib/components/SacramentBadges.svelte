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
		holy_orders: 'HO',
		anointing: 'A'
	};

	const sacramentColors: Record<SacramentType, string> = {
		baptism: 'bg-brand-accent/10 text-brand-accent',
		first_communion: 'bg-brand-accent/10 text-brand-accent',
		confirmation: 'bg-brand-accent/10 text-brand-accent',
		marriage: 'bg-brand-accent/10 text-brand-accent',
		holy_orders: 'bg-brand-accent/10 text-brand-accent',
		anointing: 'bg-brand-accent/10 text-brand-accent'
	};

	const sacramentLabels: Record<SacramentType, string> = {
		baptism: 'Baptism',
		first_communion: 'First Communion',
		confirmation: 'Confirmation',
		marriage: 'Marriage',
		holy_orders: 'Holy Orders',
		anointing: 'Anointing of the Sick'
	};

	const uniqueSacramentTypes = $derived(
		[...new Set(sacraments.map((s) => s.sacrament_type))].sort((a, b) => {
			const order: SacramentType[] = [
				'baptism',
				'first_communion',
				'confirmation',
				'marriage',
				'holy_orders',
				'anointing'
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
		<span class="text-brand-text-muted text-xs">-</span>
	{/if}
</div>
