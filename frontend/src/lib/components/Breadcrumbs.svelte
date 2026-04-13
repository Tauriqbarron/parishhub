<script lang="ts">
	import { page } from '$app/stores';
	import { ChevronRight, Home } from 'lucide-svelte';

	interface Crumb {
		label: string;
		href?: string;
	}

	interface Props {
		items?: Crumb[];
	}

	let { items }: Props = $props();

	const defaultCrumbs: Crumb[] = $derived.by(() => {
		const path = $page.url.pathname;
		if (path === '/') return [];

		const segments = path.split('/').filter(Boolean);
		const crumbs: Crumb[] = [{ label: 'Dashboard', href: '/' }];

		let currentPath = '';
		for (const segment of segments) {
			currentPath += '/' + segment;
			if (/^\[.+\]$/.test(segment) || /^[0-9]+$/.test(segment)) continue;
			const label = segment.replace(/-/g, ' ').replace(/\b\w/g, (c) => c.toUpperCase());
			crumbs.push({ label, href: currentPath });
		}

		return crumbs;
	});

	const crumbs = $derived(items ?? defaultCrumbs);
</script>

{#if crumbs.length > 1}
	<nav aria-label="Breadcrumb" class="mb-4">
		<ol class="flex items-center gap-1 text-sm text-brand-text-muted">
			{#each crumbs as crumb, i}
				<li class="flex items-center gap-1">
					{#if i > 0}
						<ChevronRight class="w-3.5 h-3.5 flex-shrink-0" />
					{/if}
					{#if i === 0}
						<Home class="w-3.5 h-3.5 flex-shrink-0" />
					{/if}
					{#if crumb.href && i < crumbs.length - 1}
						<a href={crumb.href} class="hover:text-brand-primary transition-colors">
							{crumb.label}
						</a>
					{:else}
						<span class="text-brand-primary font-medium">{crumb.label}</span>
					{/if}
				</li>
			{/each}
		</ol>
	</nav>
{/if}
