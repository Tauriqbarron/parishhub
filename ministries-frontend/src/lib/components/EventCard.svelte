<script lang="ts">
	import type { MinistryEvent } from '$lib/api';
	import { Calendar, Clock, MapPin, Repeat, Users } from 'lucide-svelte';

	let { event, onclick }: { event: MinistryEvent; onclick?: () => void } = $props();

	function formatDate(dateStr: string): string {
		return new Date(dateStr + 'T00:00:00').toLocaleDateString('en-US', {
			weekday: 'short', month: 'short', day: 'numeric'
		});
	}

	function formatTime(time: string | null): string {
		if (!time) return '';
		const [h, m] = time.split(':');
		const hour = parseInt(h);
		const ampm = hour >= 12 ? 'PM' : 'AM';
		const h12 = hour % 12 || 12;
		return `${h12}:${m} ${ampm}`;
	}

	const typeColors: Record<string, string> = {
		service: 'bg-brand-accent-muted text-brand-accent',
		meeting: 'bg-blue-50 text-blue-700',
		social: 'bg-pink-50 text-pink-700',
		outreach: 'bg-green-50 text-green-700',
		other: 'bg-brand-bg-subtle text-brand-text-secondary'
	};

	const timeRange = $derived(
		event.start_time
			? `${formatTime(event.start_time)}${event.end_time ? ' – ' + formatTime(event.end_time) : ''}`
			: ''
	);
</script>

<button {onclick} class="w-full text-left px-4 py-3 hover:bg-brand-bg-subtle transition-colors border-b border-brand-border last:border-b-0">
	<div class="flex items-start justify-between gap-2">
		<div class="min-w-0 flex-1">
			<div class="flex items-center gap-1.5 mb-0.5">
				<span class="inline-block px-1.5 py-0.5 text-xs font-medium rounded {typeColors[event.event_type] || typeColors.other}">
					{event.event_type}
				</span>
				{#if event.recurrence_rule}
					<Repeat class="w-3 h-3 text-brand-text-muted" />
				{/if}
				{#if event.is_cancelled}
					<span class="text-xs text-red-500 font-medium">Cancelled</span>
				{/if}
			</div>
			<h4 class="text-sm font-medium text-brand-primary truncate">{event.title}</h4>
			<div class="flex flex-wrap items-center gap-x-3 gap-y-0.5 mt-0.5 text-xs text-brand-text-muted">
				<span class="flex items-center gap-0.5">
					<Calendar class="w-3 h-3" />
					{formatDate(event.event_date)}
				</span>
				{#if timeRange}
					<span class="flex items-center gap-0.5">
						<Clock class="w-3 h-3" />
						{timeRange}
					</span>
				{/if}
				{#if event.location}
					<span class="flex items-center gap-0.5">
						<MapPin class="w-3 h-3" />
						{event.location}
					</span>
				{/if}
			</div>
		</div>
		<div class="text-right shrink-0">
			{#if event.capacity}
				<span class="flex items-center gap-0.5 text-xs {event.spots_remaining === 0 ? 'text-red-500' : 'text-brand-text-muted'}">
					<Users class="w-3 h-3" />
					{event.spots_remaining === 0 ? 'Full' : `${event.spots_remaining} left`}
				</span>
			{:else}
				<span class="text-xs text-brand-text-muted">{event.rsvp_count} going</span>
			{/if}
		</div>
	</div>
</button>
