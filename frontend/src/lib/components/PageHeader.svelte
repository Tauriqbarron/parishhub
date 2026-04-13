<script lang="ts">
	import type { Snippet } from 'svelte';

	interface Props {
		title: string;
		subtitle?: string;
		actions?: Snippet;
	}

	let { title, subtitle, actions }: Props = $props();
</script>

<div class="flex flex-col sm:flex-row sm:items-center sm:justify-between gap-4 mb-6">
	<div>
		<h1 class="text-2xl font-bold text-brand-primary tracking-tight">{title}</h1>
		{#if subtitle}
			<p class="text-brand-text-secondary mt-1 text-sm">{subtitle}</p>
		{/if}
	</div>
	{#if actions}
		<div class="flex items-center gap-2">
			{@render actions()}
		</div>
	{/if}
</div>
