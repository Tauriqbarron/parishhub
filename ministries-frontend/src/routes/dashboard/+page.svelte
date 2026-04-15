<script lang="ts">
	import { onMount } from 'svelte';
	import { memberApi, type WeekDashboard } from '$lib/api';
	import { Calendar, MapPin, Users } from 'lucide-svelte';

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

	function isToday(dateStr: string): boolean {
		const today = new Date().toISOString().split('T')[0];
		return dateStr === today;
	}
</script>

<div>
	<h1 class="text-xl font-semibold text-gray-900 mb-4">This Week</h1>

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
	{:else if !dashboard || dashboard.events.length === 0}
		<div class="bg-white rounded-lg border border-gray-200 p-8 text-center">
			<Calendar class="mx-auto w-10 h-10 text-gray-300" />
			<p class="mt-2 text-sm text-gray-500">No events this week</p>
			<p class="text-xs text-gray-400">
				{#if dashboard}
					{formatDate(dashboard.week_start)} — {formatDate(dashboard.week_end)}
				{/if}
			</p>
		</div>
	{:else}
		<p class="text-xs text-gray-400 mb-3">
			{formatDate(dashboard.week_start)} — {formatDate(dashboard.week_end)}
		</p>
		<div class="space-y-3">
			{#each dashboard.events as event (event.id)}
				<div
					class="bg-white rounded-lg border border-gray-200 p-4 hover:border-orange-200 transition-colors
						{isToday(event.event_date) ? 'border-l-4 border-l-orange-500' : ''}"
				>
					<div class="flex items-start justify-between">
						<div class="min-w-0 flex-1">
							<div class="flex items-center gap-2">
								<span class="text-xs font-medium {isToday(event.event_date) ? 'text-orange-600' : 'text-gray-400'}">
									{formatDate(event.event_date)}
									{#if isToday(event.event_date)}
										<span class="ml-1 px-1.5 py-0.5 bg-orange-100 text-orange-700 rounded text-[10px]">TODAY</span>
									{/if}
								</span>
							</div>
							<h3 class="mt-1 text-sm font-medium text-gray-900">{event.title}</h3>
							<p class="text-xs text-gray-500">{event.ministry_name}</p>
							{#if event.description}
								<p class="mt-1 text-xs text-gray-400 line-clamp-2">{event.description}</p>
							{/if}
						</div>
						<div class="flex items-center gap-3 ml-3 text-xs text-gray-400 shrink-0">
							{#if event.location}
								<span class="flex items-center gap-0.5">
									<MapPin class="w-3 h-3" /> {event.location}
								</span>
							{/if}
							<span class="flex items-center gap-0.5">
								<Users class="w-3 h-3" /> {event.attendance_count}
							</span>
						</div>
					</div>
				</div>
			{/each}
		</div>
	{/if}
</div>
