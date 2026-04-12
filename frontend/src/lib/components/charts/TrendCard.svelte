<script lang="ts">
	interface Props {
		value: number | string;
		label: string;
		trend?: number | null;
		trendLabel?: string;
	}

	let { value, label, trend, trendLabel }: Props = $props();

	let trendDirection = $derived(
		trend === null || trend === undefined
			? 'neutral'
			: trend > 0
				? 'up'
				: trend < 0
					? 'down'
					: 'neutral'
	);
</script>

<div class="bg-white rounded-lg shadow p-6">
	<div class="flex items-center justify-between">
		<div>
			<p class="text-3xl font-bold text-brand-primary">{value}</p>
			<p class="text-sm font-medium text-brand-text-muted">{label}</p>
		</div>
		{#if trend !== null && trend !== undefined}
			<div class="flex items-center gap-1">
				{#if trendDirection === 'up'}
					<svg
						class="w-5 h-5 text-brand-success"
						fill="none"
						stroke="currentColor"
						viewBox="0 0 24 24"
					>
						<path
							stroke-linecap="round"
							stroke-linejoin="round"
							stroke-width="2"
							d="M5 10l7-7m0 0l7 7m-7-7v18"
						/>
					</svg>
					<span class="text-sm font-medium text-brand-success">+{trend.toFixed(1)}%</span>
				{:else if trendDirection === 'down'}
					<svg
						class="w-5 h-5 text-brand-error"
						fill="none"
						stroke="currentColor"
						viewBox="0 0 24 24"
					>
						<path
							stroke-linecap="round"
							stroke-linejoin="round"
							stroke-width="2"
							d="M19 14l-7 7m0 0l-7-7m7 7V3"
						/>
					</svg>
					<span class="text-sm font-medium text-brand-error">{trend.toFixed(1)}%</span>
				{:else}
					<svg
						class="w-5 h-5 text-brand-text-muted"
						fill="none"
						stroke="currentColor"
						viewBox="0 0 24 24"
					>
						<path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M5 12h14" />
					</svg>
					<span class="text-sm font-medium text-brand-text-muted">0%</span>
				{/if}
			</div>
		{/if}
	</div>
	{#if trendLabel}
		<p class="text-xs text-brand-text-muted mt-2">{trendLabel}</p>
	{/if}
</div>
