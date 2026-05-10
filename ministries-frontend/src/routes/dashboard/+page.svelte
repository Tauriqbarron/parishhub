<script lang="ts">
	import { goto } from '$app/navigation';
	import { onMount } from 'svelte';
	import { memberApi, type WeekDashboard, type MinistryEvent } from '$lib/api';
	import { Calendar } from 'lucide-svelte';
	import EventCard from '$lib/components/EventCard.svelte';

	let dashboard = $state<WeekDashboard | null>(null);
	let loading = $state(true);
	let error = $state('');

	onMount(async () => {
		try {
			dashboard = await memberApi.dashboard();
		} catch (err) {
			error = err instanceof Error ? err.message : 'Failed to load dashboard';
		} finally {
			loading = false;
		}
	});

	function formatDate(dateStr: string): string {
		const date = new Date(dateStr + 'T00:00:00');
		return date.toLocaleDateString('en-US', { weekday: 'short', month: 'short', day: 'numeric' });
	}

	function formatDayHeader(dateStr: string): string {
		const date = new Date(dateStr + 'T00:00:00');
		return date.toLocaleDateString('en-US', { weekday: 'long', month: 'long', day: 'numeric' });
	}

	function isToday(dateStr: string): boolean {
		const today = new Date().toISOString().split('T')[0];
		return dateStr === today;
	}

	const groupedEvents = $derived.by(() => {
		if (!dashboard) return [];
		const groups: { date: string; label: string; isToday: boolean; events: MinistryEvent[] }[] = [];
		const map = new Map<string, MinistryEvent[]>();
		for (const event of dashboard.events) {
			if (!map.has(event.event_date)) map.set(event.event_date, []);
			map.get(event.event_date)!.push(event);
		}
		for (const [date, events] of map) {
			groups.push({ date, label: formatDayHeader(date), isToday: isToday(date), events });
		}
		return groups;
	});
</script>

<div>
	<h1 class="text-xl font-semibold text-brand-primary tracking-tight mb-4">This Week</h1>

	{#if loading}
		<div class="space-y-3">
			<div class="animate-pulse flex items-center gap-1">
				<div class="h-3 bg-brand-bg-muted rounded w-48"></div>
			</div>
			{#each [1, 2, 3] as i}
				<div class="animate-pulse bg-white rounded-lg border border-brand-border p-4">
					<div class="flex items-start justify-between">
						<div class="min-w-0 flex-1">
							<div class="flex items-center gap-2">
								<div class="h-3 bg-brand-bg-muted rounded w-24"></div>
							</div>
							<div class="mt-1.5 h-4 bg-brand-bg-muted rounded w-40"></div>
							<div class="mt-1 h-3 bg-brand-bg-muted rounded w-28"></div>
						</div>
						<div class="flex items-center gap-3 ml-3">
							<div class="h-3 bg-brand-bg-muted rounded w-16"></div>
							<div class="h-3 bg-brand-bg-muted rounded w-8"></div>
						</div>
					</div>
				</div>
			{/each}
		</div>
	{:else if error}
		<div class="p-4 bg-red-50 rounded-lg text-red-700 text-sm">{error}</div>
	{:else if !dashboard || dashboard.events.length === 0}
		<div class="bg-white rounded-lg border border-brand-border p-8 text-center">
			<Calendar class="mx-auto w-10 h-10 text-brand-text-muted" />
			<p class="mt-2 text-sm text-brand-text-secondary">No events this week</p>
			<p class="text-xs text-brand-text-muted">
				{#if dashboard}
					{formatDate(dashboard.week_start)} — {formatDate(dashboard.week_end)}
				{/if}
			</p>
		</div>
	{:else}
		<p class="text-xs text-brand-text-muted mb-3">
			{formatDate(dashboard.week_start)} — {formatDate(dashboard.week_end)}
		</p>
		<div class="space-y-4">
			{#each groupedEvents as group (group.date)}
				<div>
					<h2 class="text-xs font-medium mb-1.5 {group.isToday ? 'text-brand-accent' : 'text-brand-text-muted'}">
						{group.label}
						{#if group.isToday}
							<span class="ml-1 px-1.5 py-0.5 bg-brand-accent-muted text-brand-accent rounded text-[10px]">TODAY</span>
						{/if}
					</h2>
					<div class="bg-white rounded-lg border border-brand-border overflow-hidden divide-y divide-brand-border">
						{#each group.events as event (event.id)}
							<EventCard {event} onclick={() => goto(`/groups/${event.ministry_id ?? 0}/events/${event.id}`)} />
						{/each}
					</div>
				</div>
			{/each}
		</div>
	{/if}
</div>
