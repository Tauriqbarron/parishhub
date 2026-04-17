<script lang="ts">
	import { page } from '$app/stores';
	import { goto } from '$app/navigation';
	import { memberApi, type EventDetail } from '$lib/api';
	import { ArrowLeft, Calendar, Clock, MapPin, Users, Shield, Check } from 'lucide-svelte';

	let event = $state<EventDetail | null>(null);
	let loading = $state(true);
	let error = $state('');
	let rsvping = $state(false);
	let savingAttendance = $state(false);
	let attendedIds = $state<Set<number>>(new Set());

	const eventId = $derived(Number($page.params.eventId));
	const ministryId = $derived(Number($page.params.id));
	const isLeader = $derived(
		event?.rsvps !== undefined // leaders get rsvps list, members don't
	);

	async function loadEvent() {
		loading = true;
		try {
			event = await memberApi.eventDetail(eventId);
			// Initialize attendedIds from existing attendance
			attendedIds = new Set(
				event.attendance.filter(a => a.attended).map(a => a.person_id)
			);
		} catch (err) {
			error = err instanceof Error ? err.message : 'Failed to load event';
		} finally {
			loading = false;
		}
	}

	$effect(() => {
		if (eventId) loadEvent();
	});

	async function handleRsvp(status: string) {
		if (rsvping) return;
		rsvping = true;
		try {
			const result = await memberApi.rsvp(eventId, status);
			if (event) {
				event.user_rsvp = status;
				event.rsvp_count = result.rsvp_count;
				event.spots_remaining = result.spots_remaining;
			}
		} catch (err) {
			alert(err instanceof Error ? err.message : 'Failed to RSVP');
		} finally {
			rsvping = false;
		}
	}

	function toggleAttendance(personId: number) {
		if (attendedIds.has(personId)) {
			attendedIds.delete(personId);
		} else {
			attendedIds.add(personId);
		}
		attendedIds = new Set(attendedIds); // trigger reactivity
	}

	function selectAll() {
		attendedIds = new Set(event?.rsvps.map(r => r.person_id) || []);
	}

	function selectNone() {
		attendedIds = new Set();
	}

	async function saveAttendance() {
		savingAttendance = true;
		try {
			await memberApi.recordAttendance(eventId, Array.from(attendedIds));
			await loadEvent();
		} catch (err) {
			alert(err instanceof Error ? err.message : 'Failed to save attendance');
		} finally {
			savingAttendance = false;
		}
	}

	function formatDate(dateStr: string): string {
		return new Date(dateStr + 'T00:00:00').toLocaleDateString('en-US', {
			weekday: 'long', month: 'long', day: 'numeric', year: 'numeric'
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
		service: 'bg-orange-50 text-orange-700',
		meeting: 'bg-blue-50 text-blue-700',
		social: 'bg-pink-50 text-pink-700',
		outreach: 'bg-green-50 text-green-700',
		other: 'bg-gray-50 text-gray-600'
	};
</script>

<div>
	{#if loading}
	<div class="animate-pulse space-y-4">
		<div class="h-4 bg-gray-100 rounded w-16"></div>
		<div>
			<div class="h-4 bg-gray-100 rounded w-14 mb-1"></div>
			<div class="h-6 bg-gray-100 rounded w-48"></div>
		</div>
		<div class="bg-white rounded-lg border border-gray-200 p-4 space-y-3">
			<div class="flex items-center gap-2">
				<div class="h-4 w-4 bg-gray-100 rounded"></div>
				<div class="h-4 bg-gray-100 rounded w-40"></div>
			</div>
			<div class="flex items-center gap-2">
				<div class="h-4 w-4 bg-gray-100 rounded"></div>
				<div class="h-4 bg-gray-100 rounded w-28"></div>
			</div>
			<div class="flex items-center gap-2">
				<div class="h-4 w-4 bg-gray-100 rounded"></div>
				<div class="h-4 bg-gray-100 rounded w-32"></div>
			</div>
		</div>
		<div class="bg-white rounded-lg border border-gray-200 p-4">
			<div class="h-4 bg-gray-100 rounded w-12 mb-3"></div>
			<div class="flex gap-2">
				<div class="flex-1 h-9 bg-gray-100 rounded-md"></div>
				<div class="flex-1 h-9 bg-gray-100 rounded-md"></div>
				<div class="flex-1 h-9 bg-gray-100 rounded-md"></div>
			</div>
		</div>
	</div>
	{:else if error}
		<div class="p-4 bg-red-50 rounded-lg text-red-700 text-sm">{error}</div>
		<a href="/groups/{ministryId}" class="mt-3 inline-flex items-center gap-1 text-sm text-gray-500">
			<ArrowLeft class="w-4 h-4" /> Back to group
		</a>
	{:else if event}
		<a href="/groups/{ministryId}" class="inline-flex items-center gap-1 text-sm text-gray-400 hover:text-gray-600 mb-3">
			<ArrowLeft class="w-4 h-4" /> Group
		</a>

		<!-- Header -->
		<div class="mb-4">
			<div class="flex items-center gap-2 mb-1">
				<span class="inline-block px-2 py-0.5 text-xs font-medium rounded {typeColors[event.event_type] || typeColors.other}">
					{event.event_type}
				</span>
				{#if event.is_cancelled}
					<span class="text-xs text-red-500 font-medium">Cancelled</span>
				{/if}
			</div>
			<h1 class="text-xl font-semibold text-gray-900">{event.title}</h1>
			{#if event.description}
				<p class="mt-1 text-sm text-gray-500">{event.description}</p>
			{/if}
		</div>

		<!-- Event Info Card -->
		<div class="bg-white rounded-lg border border-gray-200 p-4 mb-4 space-y-2">
			<div class="flex items-center gap-2 text-sm text-gray-600">
				<Calendar class="w-4 h-4 text-gray-400" />
				{formatDate(event.event_date)}
			</div>
			{#if event.start_time}
				<div class="flex items-center gap-2 text-sm text-gray-600">
					<Clock class="w-4 h-4 text-gray-400" />
					{formatTime(event.start_time)}{event.end_time ? ' – ' + formatTime(event.end_time) : ''}
				</div>
			{/if}
			{#if event.location}
				<div class="flex items-center gap-2 text-sm text-gray-600">
					<MapPin class="w-4 h-4 text-gray-400" />
					{event.location}
				</div>
			{/if}
			{#if event.capacity}
				<div class="mt-2">
					<div class="h-1.5 bg-gray-100 rounded-full overflow-hidden">
						<div class="h-full bg-orange-500 rounded-full transition-all"
							 style="width: {Math.min(100, (event.rsvp_count / event.capacity) * 100)}%"></div>
					</div>
					<p class="mt-1 text-xs text-gray-400">
						{event.rsvp_count} / {event.capacity} spots filled
						{#if event.spots_remaining !== null && event.spots_remaining > 0}
							· {event.spots_remaining} left
						{:else if event.spots_remaining === 0}
							· <span class="text-red-500">Full</span>
						{/if}
					</p>
				</div>
			{/if}
		</div>

		<!-- RSVP Section -->
		<div class="bg-white rounded-lg border border-gray-200 p-4 mb-4">
			<h3 class="text-sm font-medium text-gray-900 mb-3">RSVP</h3>
			<div class="flex gap-2">
				<button onclick={() => handleRsvp('going')} disabled={rsvping}
					class="flex-1 py-2 rounded-md text-sm font-medium transition-colors
						{event.user_rsvp === 'going' ? 'bg-green-100 text-green-700 border border-green-300' : 'bg-gray-50 text-gray-600 border border-gray-200 hover:bg-green-50'}">
					Going
				</button>
				<button onclick={() => handleRsvp('maybe')} disabled={rsvping}
					class="flex-1 py-2 rounded-md text-sm font-medium transition-colors
						{event.user_rsvp === 'maybe' ? 'bg-yellow-100 text-yellow-700 border border-yellow-300' : 'bg-gray-50 text-gray-600 border border-gray-200 hover:bg-yellow-50'}">
					Maybe
				</button>
				<button onclick={() => handleRsvp('not_going')} disabled={rsvping}
					class="flex-1 py-2 rounded-md text-sm font-medium transition-colors
						{event.user_rsvp === 'not_going' ? 'bg-red-100 text-red-700 border border-red-300' : 'bg-gray-50 text-gray-600 border border-gray-200 hover:bg-red-50'}">
					Can't Go
				</button>
			</div>
			{#if !event.capacity}
				<p class="mt-2 text-xs text-gray-400">{event.rsvp_count} people going</p>
			{/if}
		</div>

		<!-- Leader: RSVP Summary -->
		{#if event.rsvps.length > 0 || isLeader}
			<div class="bg-white rounded-lg border border-gray-200 p-4 mb-4">
				<h3 class="text-sm font-medium text-gray-900 mb-2">Responses</h3>
				<div class="flex gap-4 text-sm">
					<span class="text-green-600">{event.rsvp_summary.going} going</span>
					<span class="text-yellow-600">{event.rsvp_summary.maybe} maybe</span>
					<span class="text-gray-400">{event.rsvp_summary.not_going} can't go</span>
				</div>
			</div>
		{/if}

		<!-- Leader: Attendance Sheet -->
		{#if event.rsvps.length > 0}
			<div class="bg-white rounded-lg border border-gray-200 p-4">
				<div class="flex items-center justify-between mb-3">
					<h3 class="text-sm font-medium text-gray-900">Take Attendance</h3>
					<div class="flex items-center gap-2">
						<span class="text-xs text-gray-400">{attendedIds.size} of {event.rsvps.length} selected</span>
						<button onclick={selectAll} class="text-xs font-medium text-orange-600 hover:text-orange-700">All</button>
						<button onclick={selectNone} class="text-xs font-medium text-gray-400 hover:text-gray-600">None</button>
					</div>
				</div>
				<div class="divide-y divide-gray-50">
					{#each event.rsvps as rsvp (rsvp.person_id)}
						<label class="flex items-center gap-3 py-2 cursor-pointer">
							<input type="checkbox"
								checked={attendedIds.has(rsvp.person_id)}
								onchange={() => toggleAttendance(rsvp.person_id)}
								class="rounded border-gray-300 text-orange-600 focus:ring-orange-500" />
							<span class="text-sm text-gray-900">{rsvp.person_name || `Person #${rsvp.person_id}`}</span>
							<span class="text-xs text-gray-400 ml-auto">{rsvp.status}</span>
						</label>
					{/each}
				</div>
				<button onclick={saveAttendance} disabled={savingAttendance}
					class="mt-3 px-4 py-1.5 text-sm font-medium rounded-md text-white bg-orange-600 hover:bg-orange-700 disabled:opacity-50">
					{savingAttendance ? 'Saving...' : 'Save Attendance'}
				</button>
			</div>
		{/if}
	{/if}
</div>
