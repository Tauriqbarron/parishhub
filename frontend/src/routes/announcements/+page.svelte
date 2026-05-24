<script lang="ts">
	import { onMount } from 'svelte';
	import { Megaphone, Loader2, Plus, ExternalLink } from 'lucide-svelte';
	import { api } from '$lib/api';

	interface Announcement {
		id: number;
		title: string;
		body: string;
		scope: string;
		channels: string[];
		created_at: string;
		created_by: string | null;
	}

	let items: Announcement[] = $state([]);
	let loading = $state(true);
	let error = $state<string | null>(null);

	async function load() {
		loading = true;
		error = null;
		try {
			const data = await api.get<Announcement[]>('/announcements');
			items = data;
		} catch (e) {
			error = e instanceof Error ? e.message : 'Failed to load announcements';
		} finally {
			loading = false;
		}
	}

	onMount(() => {
		load();
	});

	function timeAgo(iso: string): string {
		const now = Date.now();
		const then = new Date(iso).getTime();
		const diff = now - then;
		const minutes = Math.floor(diff / 60000);
		const hours = Math.floor(minutes / 60);
		const days = Math.floor(hours / 24);

		if (minutes < 60) return `${minutes}m ago`;
		if (hours < 24) return `${hours}h ago`;
		if (days < 7) return `${days}d ago`;
		return new Date(iso).toLocaleDateString('en-NZ', {
			day: 'numeric',
			month: 'short',
			year: 'numeric'
		});
	}
</script>

<div class="max-w-3xl mx-auto">
	<div class="flex items-center justify-between mb-6">
		<h1 class="text-2xl font-bold tracking-tight text-brand-primary">Announcements</h1>
		<a href="/announcements/new" class="btn-primary inline-flex items-center gap-1.5 text-sm">
			<Plus class="w-4 h-4" />
			New Announcement
		</a>
	</div>

	{#if loading}
		<div class="flex items-center justify-center py-16">
			<Loader2 class="w-6 h-6 animate-spin text-brand-text-muted" />
		</div>
	{:else if error}
		<div class="card p-6 text-center">
			<p class="text-sm text-red-800 mb-3">{error}</p>
			<button onclick={load} class="btn-primary text-sm">Retry</button>
		</div>
	{:else if items.length === 0}
		<div class="card p-12 text-center">
			<Megaphone class="w-10 h-10 text-brand-text-muted/30 mx-auto mb-3" />
			<p class="text-brand-text-secondary font-medium">No announcements yet</p>
			<p class="text-xs text-brand-text-muted mt-1 mb-4">
				Create your first announcement to reach your parish community.
			</p>
			<a href="/announcements/new" class="btn-primary inline-flex items-center gap-1.5 text-sm">
				<Plus class="w-4 h-4" />
				Create Announcement
			</a>
		</div>
	{:else}
		<div class="space-y-3">
			{#each items as a (a.id)}
				<div class="card p-4 hover:shadow-md transition-shadow">
					<div class="flex items-start justify-between gap-3">
						<div class="min-w-0 flex-1">
							<h3 class="text-sm font-semibold text-brand-primary">
								{a.title}
							</h3>
							<p class="text-xs text-brand-text-muted mt-1 line-clamp-2">
								{a.body}
							</p>
						</div>
						<span class="text-xs text-brand-text-muted whitespace-nowrap">
							{timeAgo(a.created_at)}
						</span>
					</div>
					<div class="flex items-center gap-2 mt-3">
						<span
							class="text-[10px] font-medium text-brand-text-muted uppercase bg-brand-bg-subtle px-1.5 py-0.5 rounded-sm"
						>
							{a.scope}
						</span>
						{#each a.channels as ch}
							<span class="text-[10px] text-brand-text-muted">
								{ch}
							</span>
						{/each}
					</div>
				</div>
			{/each}
		</div>
	{/if}
</div>
