<script lang="ts">
	import { onMount } from 'svelte';
	import { memberApi, type MinistrySummary, type MinistryEvent } from '$lib/api';
	import { Calendar, MapPin, Users } from 'lucide-svelte';

	let ministries = $state<MinistrySummary[]>([]);
	let allEvents = $state<(MinistryEvent & { ministry_name: string })[]>([]);
	let loading = $state(true);
	let error = $state('');

	onMount(async () => {
		try {
			const result = await memberApi.ministries();
			ministries = result.ministries;

			// Fetch events for each ministry
			const eventsPerMinistry = await Promise.all(
				ministries.map(async (m) => {
					try {
						const res = await memberApi.listEvents(m.id);
						return res.events.map((e) => ({ ...e, ministry_name: m.name }));
					} catch {
						return [];
					}
				})
			);

			allEvents = eventsPerMinistry
				.flat()
				.sort((a, b) => a.event_date.localeCompare(b.event_date));
		} catch (err) {
			error = err instanceof Error ? err.message : 'Failed to load events';
		} finally {
			loading = false;
		}
	});

	function formatDate(dateStr: string): string {
		return new Date(dateStr + 'T00:00:00').toLocaleDateString('en-US', {
			weekday: 'short',
			month: 'short',
			day: 'numeric'
		});
	}

	function isUpcoming(dateStr: string): boolean {
		return dateStr >= new Date().toISOString().split('T')[0];
	}

	const upcomingEvents = $derived(allEvents.filter((e) => isUpcoming(e.event_date)));
	const pastEvents = $derived(allEvents.filter((e) => !isUpcoming(e.event_date)).reverse());
</script>

<div>
	<h1 class="text-xl font-semibold text-gray-900 mb-4">Events</h1>

	{#if loading}
		<div class="space-y-3">
			{#each [1, 2, 3] as i}
				<div class="animate-pulse bg-white rounded-lg border border-gray-200 p-4">
					<div class="h-4 bg-gray-100 rounded w-1/3 mb-2"></div>
					<div class="h-3 bg-gray-100 rounded w-1/2"></div>
				</div>
			{/each}
		</div>
	{:else if error}
		<div class="p-4 bg-red-50 rounded-lg text-red-700 text-sm">{error}</div>
	{:else}
		{#if upcomingEvents.length > 0}
			<h2 class="text-sm font-medium text-gray-500 mb-2">Upcoming</h2>
			<div class="space-y-3 mb-6">
				{#each upcomingEvents as event (event.id)}
					<div class="bg-white rounded-lg border border-gray-200 p-4">
						<span class="text-xs font-medium text-orange-600">{formatDate(event.event_date)}</span>
						<h3 class="mt-0.5 text-sm font-medium text-gray-900">{event.title}</h3>
						<p class="text-xs text-gray-400">{event.ministry_name}</p>
						{#if event.location}
							<p class="mt-1 text-xs text-gray-400 flex items-center gap-0.5">
								<MapPin class="w-3 h-3" /> {event.location}
							</p>
						{/if}
					</div>
				{/each}
			</div>
		{/if}

		{#if pastEvents.length > 0}
			<h2 class="text-sm font-medium text-gray-500 mb-2">Past</h2>
			<div class="space-y-3">
				{#each pastEvents as event (event.id)}
					<div class="bg-white rounded-lg border border-gray-200 p-4 opacity-70">
						<span class="text-xs text-gray-400">{formatDate(event.event_date)}</span>
						<h3 class="mt-0.5 text-sm font-medium text-gray-700">{event.title}</h3>
						<p class="text-xs text-gray-400">{event.ministry_name} · {event.attendance_count} attended</p>
					</div>
				{/each}
			</div>
		{/if}

		{#if upcomingEvents.length === 0 && pastEvents.length === 0}
			<div class="bg-white rounded-lg border border-gray-200 p-8 text-center">
				<Calendar class="mx-auto w-10 h-10 text-gray-300" />
				<p class="mt-2 text-sm text-gray-500">No events yet</p>
			</div>
		{/if}
	{/if}
</div>
