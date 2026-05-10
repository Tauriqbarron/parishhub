<script lang="ts">
	import { onMount } from 'svelte';
	import { Bell, Loader2, CheckCheck, AlertCircle } from 'lucide-svelte';
	import { api } from '$lib/api';
	import type { NotificationDelivery, PaginatedNotifications } from '$stores/notifications';
	import { markAsRead } from '$stores/notifications';

	type FilterStatus = 'all' | 'unread';

	let items: NotificationDelivery[] = $state([]);
	let loading = $state(true);
	let error = $state<string | null>(null);
	let status: FilterStatus = $state('all');
	let page = $state(1);
	let total = $state(0);
	let pages = $state(1);
	let markingAll = $state(false);

	const PER_PAGE = 20;

	async function load() {
		loading = true;
		error = null;
		try {
			const data = await api.get<PaginatedNotifications>(
				`/member/notification/deliveries?status=${status}&page=${page}&per_page=${PER_PAGE}`
			);
			items = data.items;
			total = data.total;
			pages = data.pages;
		} catch (e) {
			error = e instanceof Error ? e.message : 'Failed to load notifications';
		} finally {
			loading = false;
		}
	}

	onMount(() => {
		load();
	});

	$effect(() => {
		// Re-fetch when status or page changes
		if (status || page) load();
	});

	async function handleMarkAllRead() {
		const unreadIds = items.filter((n) => !n.is_read).map((n) => n.id);
		if (unreadIds.length === 0) return;
		markingAll = true;
		try {
			await markAsRead(unreadIds);
			items = items.map((n) =>
				unreadIds.includes(n.id) ? { ...n, is_read: true } : n
			);
		} catch {
			// silently fail
		} finally {
			markingAll = false;
		}
	}

	async function handleMarkOne(id: number) {
		try {
			await markAsRead([id]);
			items = items.map((n) => (n.id === id ? { ...n, is_read: true } : n));
		} catch {
			// silently fail
		}
	}

	function timeAgo(iso: string): string {
		const now = Date.now();
		const then = new Date(iso).getTime();
		const diff = now - then;
		const seconds = Math.floor(diff / 1000);
		const minutes = Math.floor(seconds / 60);
		const hours = Math.floor(minutes / 60);
		const days = Math.floor(hours / 24);

		if (seconds < 60) return 'Just now';
		if (minutes < 60) return `${minutes}m ago`;
		if (hours < 24) return `${hours}h ago`;
		if (days < 7) return `${days}d ago`;
		return new Date(iso).toLocaleDateString();
	}

	/** Group by date */
	function grouped(): Record<string, NotificationDelivery[]> {
		const groups: Record<string, NotificationDelivery[]> = {};
		const today = new Date();
		const yesterday = new Date(today);
		yesterday.setDate(yesterday.getDate() - 1);
		const fmt = (d: Date) => d.toISOString().split('T')[0];

		for (const item of items) {
			const d = new Date(item.created_at);
			let key: string;
			if (fmt(d) === fmt(today)) {
				key = 'Today';
			} else if (fmt(d) === fmt(yesterday)) {
				key = 'Yesterday';
			} else {
				key = d.toLocaleDateString('en-NZ', {
					day: 'numeric',
					month: 'long',
					year: 'numeric'
				});
			}
			if (!groups[key]) groups[key] = [];
			groups[key].push(item);
		}
		return groups;
	}

	const groupEntries = $derived(Object.entries(grouped()));
	const unreadCount = $derived(items.filter((n) => !n.is_read).length);
</script>

<div class="max-w-3xl mx-auto">
	<div class="flex items-center justify-between mb-6">
		<h1 class="text-2xl font-bold tracking-tight text-brand-primary">Notifications</h1>
		<div class="flex items-center gap-3">
			{#if unreadCount > 0}
				<button
					onclick={handleMarkAllRead}
					disabled={markingAll}
					class="inline-flex items-center gap-1.5 text-sm font-medium text-brand-accent hover:text-brand-accent/80 transition-colors disabled:opacity-50"
				>
					{#if markingAll}
						<Loader2 class="w-4 h-4 animate-spin" />
					{:else}
						<CheckCheck class="w-4 h-4" />
					{/if}
					Mark all read
				</button>
			{/if}
			<a
				href="/announcements/new"
				class="btn-primary text-sm"
			>
				New Announcement
			</a>
		</div>
	</div>

	<!-- Filters -->
	<div class="flex gap-1 bg-brand-bg-subtle rounded-sm p-1 w-fit mb-6">
		<button
			onclick={() => { status = 'all'; page = 1; }}
			class="px-3 py-1.5 text-xs font-medium rounded-sm transition-colors {status === 'all'
				? 'bg-white text-brand-primary shadow-sm'
				: 'text-brand-text-secondary hover:text-brand-primary'}"
		>
			All
		</button>
		<button
			onclick={() => { status = 'unread'; page = 1; }}
			class="px-3 py-1.5 text-xs font-medium rounded-sm transition-colors {status === 'unread'
				? 'bg-white text-brand-primary shadow-sm'
				: 'text-brand-text-secondary hover:text-brand-primary'}"
		>
			Unread
		</button>
	</div>

	<!-- Content -->
	{#if loading && items.length === 0}
		<div class="flex items-center justify-center py-16">
			<Loader2 class="w-6 h-6 animate-spin text-brand-text-muted" />
		</div>
	{:else if error}
		<div class="card p-6 text-center">
			<AlertCircle class="w-8 h-8 text-red-500 mx-auto mb-2" />
			<p class="text-sm text-brand-text-secondary">{error}</p>
			<button onclick={load} class="btn-primary mt-4 text-sm">Retry</button>
		</div>
	{:else if items.length === 0}
		<div class="card p-12 text-center">
			<Bell class="w-10 h-10 text-brand-text-muted/30 mx-auto mb-3" />
			<p class="text-brand-text-secondary font-medium">No notifications</p>
			<p class="text-xs text-brand-text-muted mt-1">
				{status === 'unread' ? "You're all caught up!" : 'Notifications will appear here'}
			</p>
		</div>
	{:else}
		<div class="space-y-6">
			{#each groupEntries as [dateLabel, dateItems]}
				<div>
					<h2 class="text-xs font-semibold text-brand-text-muted uppercase tracking-wider mb-3 px-1">
						{dateLabel}
					</h2>
					<div class="card divide-y divide-brand-border overflow-hidden">
						{#each dateItems as notif (notif.id)}
							<button
								class="w-full text-left flex items-start gap-3 px-4 py-3 transition-colors hover:bg-brand-bg-subtle {!notif.is_read ? 'bg-amber-50/50' : ''}"
								onclick={() => !notif.is_read && handleMarkOne(notif.id)}
							>
								<!-- Unread dot -->
								<div class="flex-shrink-0 mt-1.5">
									{#if !notif.is_read}
										<span class="block w-2.5 h-2.5 rounded-full bg-brand-accent"></span>
									{:else}
										<span class="block w-2.5 h-2.5 rounded-full bg-transparent"></span>
									{/if}
								</div>

								<div class="min-w-0 flex-1">
									<div class="flex items-start justify-between gap-2">
										<p class="text-sm {!notif.is_read ? 'font-semibold text-brand-primary' : 'font-medium text-brand-text-secondary'}">
											{notif.title}
										</p>
										<span class="text-xs text-brand-text-muted whitespace-nowrap flex-shrink-0">
											{timeAgo(notif.created_at)}
										</span>
									</div>
									<p class="text-xs text-brand-text-muted mt-1 line-clamp-2">
										{notif.body}
									</p>
									<div class="flex items-center gap-2 mt-2">
										<span class="text-[10px] font-medium text-brand-text-muted uppercase tracking-wider bg-brand-bg-subtle px-1.5 py-0.5 rounded-sm">
											{notif.category}
										</span>
										<span class="text-[10px] text-brand-text-muted">
											via {notif.channel}
										</span>
									</div>
								</div>
							</button>
						{/each}
					</div>
				</div>
			{/each}
		</div>
	{/if}

	<!-- Pagination -->
	{#if pages > 1}
		<div class="flex items-center justify-center gap-2 mt-6">
			<button
				onclick={() => page = Math.max(1, page - 1)}
				disabled={page === 1 || loading}
				class="px-3 py-1.5 text-sm rounded-sm border border-brand-border hover:bg-brand-bg-subtle disabled:opacity-40 transition-colors"
			>
				Previous
			</button>
			<span class="text-sm text-brand-text-muted">{page} of {pages}</span>
			<button
				onclick={() => page = Math.min(pages, page + 1)}
				disabled={page === pages || loading}
				class="px-3 py-1.5 text-sm rounded-sm border border-brand-border hover:bg-brand-bg-subtle disabled:opacity-40 transition-colors"
			>
				Next
			</button>
		</div>
	{/if}
</div>
