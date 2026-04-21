<script lang="ts">
	import { X, MapPin, Clock, Users, Calendar } from 'lucide-svelte';
	import type { CalendarEvent } from '$lib/api';

	interface Props {
		event: CalendarEvent;
		onClose: () => void;
	}

	let { event, onClose }: Props = $props();

	function formatDate(dateStr: string): string {
		const d = new Date(dateStr + 'T00:00:00');
		return d.toLocaleDateString('en-NZ', {
			weekday: 'long',
			year: 'numeric',
			month: 'long',
			day: 'numeric'
		});
	}

	function formatTime(time: string | null): string {
		if (!time) return '';
		const [h, m] = time.split(':');
		const hour = parseInt(h);
		const ampm = hour >= 12 ? 'PM' : 'AM';
		const displayHour = hour === 0 ? 12 : hour > 12 ? hour - 12 : hour;
		return `${displayHour}:${m} ${ampm}`;
	}
</script>

<!-- Modal overlay -->
<!-- svelte-ignore a11y_no_static_element_interactions -->
<div class="fixed inset-0 z-modal flex items-center justify-center bg-black/40" onclick={onClose} onkeydown={(e) => e.key === 'Escape' && onClose()} role="dialog" aria-modal="true" aria-label="Event details" tabindex="-1">
	<!-- svelte-ignore a11y_no_static_element_interactions -->
	<div
		class="bg-white rounded-lg shadow-lg max-w-md w-full mx-4 overflow-hidden"
		onclick={(e) => e.stopPropagation()}
	>
		<!-- Header -->
		<div class="flex items-start justify-between p-5 border-b border-brand-border">
			<div class="min-w-0 flex-1">
				<h3 class="text-lg font-semibold text-brand-primary truncate">{event.title}</h3>
				<p class="text-sm text-brand-accent mt-0.5">{event.ministry_name}</p>
			</div>
			<button
				type="button"
				onclick={onClose}
				class="ml-3 p-1 text-brand-text-muted hover:text-brand-primary transition-colors rounded-sm hover:bg-brand-bg-muted"
				aria-label="Close"
			>
				<X class="w-5 h-5" />
			</button>
		</div>

		<!-- Details -->
		<div class="p-5 space-y-3">
			<div class="flex items-center gap-2 text-sm text-brand-text-secondary">
				<Calendar class="w-4 h-4 text-brand-text-muted flex-shrink-0" />
				<span>{formatDate(event.event_date)}</span>
			</div>

			{#if event.start_time}
				<div class="flex items-center gap-2 text-sm text-brand-text-secondary">
					<Clock class="w-4 h-4 text-brand-text-muted flex-shrink-0" />
					<span>
						{formatTime(event.start_time)}
						{#if event.end_time}
							– {formatTime(event.end_time)}
						{/if}
					</span>
				</div>
			{/if}

			{#if event.location}
				<div class="flex items-center gap-2 text-sm text-brand-text-secondary">
					<MapPin class="w-4 h-4 text-brand-text-muted flex-shrink-0" />
					<span>{event.location}</span>
				</div>
			{/if}

			{#if event.capacity}
				<div class="flex items-center gap-2 text-sm text-brand-text-secondary">
					<Users class="w-4 h-4 text-brand-text-muted flex-shrink-0" />
					<span>
						{event.rsvp_count} attending
						{#if event.spots_remaining !== null && event.spots_remaining > 0}
							· {event.spots_remaining} spots left
						{/if}
					</span>
				</div>
			{/if}

			{#if event.description}
				<div class="pt-2 border-t border-brand-border">
					<p class="text-sm text-brand-text-secondary whitespace-pre-wrap">{event.description}</p>
				</div>
			{/if}

			<div class="pt-1">
				<span class="inline-flex items-center px-2 py-0.5 rounded text-xs font-medium bg-brand-bg-subtle text-brand-text-secondary capitalize">
					{event.event_type.replace('_', ' ')}
				</span>
			</div>
		</div>
	</div>
</div>
