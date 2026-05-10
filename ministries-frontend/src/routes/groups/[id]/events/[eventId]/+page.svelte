<script lang="ts">
	import { page } from '$app/stores';
	import { goto } from '$app/navigation';
	import { memberApi, type EventDetail } from '$lib/api';
	import { ArrowLeft, Calendar, Clock, MapPin, Users, Shield, Check, Edit3, Trash2, X } from 'lucide-svelte';

	let event = $state<EventDetail | null>(null);
	let loading = $state(true);
	let error = $state('');
	let rsvping = $state(false);
	let savingAttendance = $state(false);
	let attendedIds = $state<Set<number>>(new Set());

	// Edit state
	let isEditing = $state(false);
	let saving = $state(false);
	let editTitle = $state('');
	let editDescription = $state('');
	let editDate = $state('');
	let editLocation = $state('');
	let editStartTime = $state('');
	let editEndTime = $state('');
	let editEventType = $state('other');
	let editCapacity = $state('');

	// Delete state
	let showDeleteConfirm = $state(false);
	let deleting = $state(false);

	const eventId = $derived(Number($page.params.eventId));
	const ministryId = $derived(Number($page.params.id));
	const isLeader = $derived(
		event?.rsvps !== undefined // leaders get rsvps list, members don't
	);

	async function loadEvent() {
		loading = true;
		try {
			event = await memberApi.eventDetail(eventId);
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

	function startEditing() {
		if (!event) return;
		editTitle = event.title;
		editDescription = event.description || '';
		editDate = event.event_date;
		editLocation = event.location || '';
		editStartTime = event.start_time || '';
		editEndTime = event.end_time || '';
		editEventType = event.event_type;
		editCapacity = event.capacity ? String(event.capacity) : '';
		isEditing = true;
	}

	function cancelEditing() {
		isEditing = false;
	}

	async function saveEdit() {
		if (!editTitle.trim() || !editDate) return;
		saving = true;
		try {
			await memberApi.updateEvent(eventId, {
				title: editTitle.trim(),
				description: editDescription.trim() || undefined,
				event_date: editDate,
				location: editLocation.trim() || undefined,
				start_time: editStartTime || undefined,
				end_time: editEndTime || undefined,
				event_type: editEventType,
				capacity: editCapacity ? Number(editCapacity) : undefined
			});
			isEditing = false;
			await loadEvent();
		} catch (err) {
			alert(err instanceof Error ? err.message : 'Failed to save changes');
		} finally {
			saving = false;
		}
	}

	async function handleDelete() {
		deleting = true;
		try {
			await memberApi.deleteEvent(eventId);
			goto(`/groups/${ministryId}?tab=events`);
		} catch (err) {
			alert(err instanceof Error ? err.message : 'Failed to delete event');
			showDeleteConfirm = false;
			deleting = false;
		}
	}

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
		attendedIds = new Set(attendedIds);
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
		service: 'bg-brand-accent-muted text-brand-accent',
		meeting: 'bg-blue-50 text-blue-700',
		social: 'bg-pink-50 text-pink-700',
		outreach: 'bg-green-50 text-green-700',
		other: 'bg-brand-bg-subtle text-brand-text-secondary'
	};
</script>

<div>
	{#if loading}
	<div class="animate-pulse space-y-4">
		<div class="h-4 bg-brand-bg-muted rounded w-16"></div>
		<div>
			<div class="h-4 bg-brand-bg-muted rounded w-14 mb-1"></div>
			<div class="h-6 bg-brand-bg-muted rounded w-48"></div>
		</div>
		<div class="bg-white rounded-lg border border-brand-border p-4 space-y-3">
			<div class="flex items-center gap-2"><div class="h-4 w-4 bg-brand-bg-muted rounded"></div><div class="h-4 bg-brand-bg-muted rounded w-40"></div></div>
			<div class="flex items-center gap-2"><div class="h-4 w-4 bg-brand-bg-muted rounded"></div><div class="h-4 bg-brand-bg-muted rounded w-28"></div></div>
			<div class="flex items-center gap-2"><div class="h-4 w-4 bg-brand-bg-muted rounded"></div><div class="h-4 bg-brand-bg-muted rounded w-32"></div></div>
		</div>
		<div class="bg-white rounded-lg border border-brand-border p-4">
			<div class="h-4 bg-brand-bg-muted rounded w-12 mb-3"></div>
			<div class="flex gap-2">
				<div class="flex-1 h-9 bg-brand-bg-muted rounded-sm"></div>
				<div class="flex-1 h-9 bg-brand-bg-muted rounded-sm"></div>
				<div class="flex-1 h-9 bg-brand-bg-muted rounded-sm"></div>
			</div>
		</div>
	</div>
	{:else if error}
		<div class="p-4 bg-red-50 rounded-lg text-red-700 text-sm">{error}</div>
		<a href="/groups/{ministryId}" class="mt-3 inline-flex items-center gap-1 text-sm text-brand-text-secondary">
			<ArrowLeft class="w-4 h-4" /> Back to group
		</a>
	{:else if event}
		<a href="/groups/{ministryId}" class="inline-flex items-center gap-1 text-sm text-brand-text-muted hover:text-brand-text-secondary mb-3">
			<ArrowLeft class="w-4 h-4" /> Group
		</a>

		{#if isEditing}
			<!-- Edit Form -->
			<div class="bg-white rounded-lg border border-brand-border p-4 mb-4">
				<div class="flex items-center justify-between mb-3">
					<h3 class="text-sm font-medium text-brand-primary">Edit Event</h3>
					<button onclick={cancelEditing} class="text-brand-text-muted hover:text-brand-text-secondary">
						<X class="w-4 h-4" />
					</button>
				</div>
				<div class="space-y-2">
					<input type="text" bind:value={editTitle} placeholder="Event title"
						class="w-full px-3 py-1.5 text-sm border border-brand-border rounded-sm focus:border-brand-accent focus:ring-1 focus:ring-brand-accent outline-none" />
					<input type="date" bind:value={editDate}
						class="w-full px-3 py-1.5 text-sm border border-brand-border rounded-sm focus:border-brand-accent focus:ring-1 focus:ring-brand-accent outline-none" />
					<input type="text" bind:value={editLocation} placeholder="Location (optional)"
						class="w-full px-3 py-1.5 text-sm border border-brand-border rounded-sm focus:border-brand-accent focus:ring-1 focus:ring-brand-accent outline-none" />
					<textarea bind:value={editDescription} placeholder="Description (optional)" rows={2}
						class="w-full px-3 py-1.5 text-sm border border-brand-border rounded-sm focus:border-brand-accent focus:ring-1 focus:ring-brand-accent outline-none resize-none"></textarea>
					<select bind:value={editEventType}
						class="w-full px-3 py-1.5 text-sm border border-brand-border rounded-sm focus:border-brand-accent focus:ring-1 focus:ring-brand-accent outline-none">
						<option value="other">Other</option>
						<option value="service">Service</option>
						<option value="meeting">Meeting</option>
						<option value="social">Social</option>
						<option value="outreach">Outreach</option>
					</select>
					<div class="flex gap-2">
						<input type="time" bind:value={editStartTime} placeholder="Start time"
							class="flex-1 px-3 py-1.5 text-sm border border-brand-border rounded-sm focus:border-brand-accent focus:ring-1 focus:ring-brand-accent outline-none" />
						<input type="time" bind:value={editEndTime} placeholder="End time"
							class="flex-1 px-3 py-1.5 text-sm border border-brand-border rounded-sm focus:border-brand-accent focus:ring-1 focus:ring-brand-accent outline-none" />
					</div>
					<input type="number" bind:value={editCapacity} placeholder="Capacity (optional)" min="1"
						class="w-full px-3 py-1.5 text-sm border border-brand-border rounded-sm focus:border-brand-accent focus:ring-1 focus:ring-brand-accent outline-none" />
					<div class="flex items-center gap-2 pt-1">
						<button onclick={saveEdit} disabled={saving || !editTitle.trim() || !editDate}
							class="px-3 py-1.5 text-sm font-medium rounded-sm text-white bg-brand-accent hover:bg-brand-accent/90 disabled:opacity-50">
							{saving ? 'Saving...' : 'Save'}
						</button>
						<button onclick={cancelEditing}
							class="px-3 py-1.5 text-sm text-brand-text-secondary hover:text-brand-primary">
							Cancel
						</button>
					</div>
				</div>
			</div>
		{:else}
			<!-- Header -->
			<div class="mb-4">
				<div class="flex items-center justify-between">
					<div>
						<div class="flex items-center gap-2 mb-1">
							<span class="inline-block px-2 py-0.5 text-xs font-medium rounded {typeColors[event.event_type] || typeColors.other}">
								{event.event_type}
							</span>
							{#if event.is_cancelled}
								<span class="text-xs text-red-500 font-medium">Cancelled</span>
							{/if}
						</div>
						<h1 class="text-xl font-semibold text-brand-primary tracking-tight">{event.title}</h1>
						{#if event.description}
							<p class="mt-1 text-sm text-brand-text-secondary">{event.description}</p>
						{/if}
					</div>
					{#if isLeader}
						<div class="flex items-center gap-1">
							<button onclick={startEditing} title="Edit event"
								class="p-2 text-brand-text-muted hover:text-brand-text-secondary rounded-sm hover:bg-brand-bg-muted transition-colors">
								<Edit3 class="w-4 h-4" />
							</button>
							<button onclick={() => (showDeleteConfirm = true)} title="Delete event"
								class="p-2 text-brand-text-muted hover:text-red-500 rounded-sm hover:bg-red-50 transition-colors">
								<Trash2 class="w-4 h-4" />
							</button>
						</div>
					{/if}
				</div>
			</div>

			<!-- Event Info Card -->
			<div class="bg-white rounded-lg border border-brand-border p-4 mb-4 space-y-2">
				<div class="flex items-center gap-2 text-sm text-brand-text-secondary">
					<Calendar class="w-4 h-4 text-brand-text-muted" />
					{formatDate(event.event_date)}
				</div>
				{#if event.start_time}
					<div class="flex items-center gap-2 text-sm text-brand-text-secondary">
						<Clock class="w-4 h-4 text-brand-text-muted" />
						{formatTime(event.start_time)}{event.end_time ? ' – ' + formatTime(event.end_time) : ''}
					</div>
				{/if}
				{#if event.location}
					<div class="flex items-center gap-2 text-sm text-brand-text-secondary">
						<MapPin class="w-4 h-4 text-brand-text-muted" />
						{event.location}
					</div>
				{/if}
				{#if event.capacity}
					<div class="mt-2">
						<div class="h-1.5 bg-brand-bg-muted rounded-full overflow-hidden">
							<div class="h-full bg-brand-accent-muted0 rounded-full transition-all"
								style="width: {Math.min(100, (event.rsvp_count / event.capacity) * 100)}%"></div>
						</div>
						<p class="mt-1 text-xs text-brand-text-muted">
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
			<div class="bg-white rounded-lg border border-brand-border p-4 mb-4">
				<h3 class="text-sm font-medium text-brand-primary mb-3">RSVP</h3>
				<div class="flex gap-2">
					<button onclick={() => handleRsvp('going')} disabled={rsvping}
						class="flex-1 py-2 rounded-sm text-sm font-medium transition-colors
							{event.user_rsvp === 'going' ? 'bg-green-100 text-green-700 border border-green-300' : 'bg-brand-bg-subtle text-brand-text-secondary border border-brand-border hover:bg-green-50'}">
						Going
					</button>
					<button onclick={() => handleRsvp('maybe')} disabled={rsvping}
						class="flex-1 py-2 rounded-sm text-sm font-medium transition-colors
							{event.user_rsvp === 'maybe' ? 'bg-yellow-100 text-yellow-700 border border-yellow-300' : 'bg-brand-bg-subtle text-brand-text-secondary border border-brand-border hover:bg-yellow-50'}">
						Maybe
					</button>
					<button onclick={() => handleRsvp('not_going')} disabled={rsvping}
						class="flex-1 py-2 rounded-sm text-sm font-medium transition-colors
							{event.user_rsvp === 'not_going' ? 'bg-red-100 text-red-700 border border-red-300' : 'bg-brand-bg-subtle text-brand-text-secondary border border-brand-border hover:bg-red-50'}">
						Can't Go
					</button>
				</div>
				{#if !event.capacity}
					<p class="mt-2 text-xs text-brand-text-muted">{event.rsvp_count} people going</p>
				{/if}
			</div>

			<!-- Leader: RSVP Summary -->
			{#if event.rsvps.length > 0 || isLeader}
				<div class="bg-white rounded-lg border border-brand-border p-4 mb-4">
					<h3 class="text-sm font-medium text-brand-primary mb-2">Responses</h3>
					<div class="flex gap-4 text-sm">
						<span class="text-green-600">{event.rsvp_summary.going} going</span>
						<span class="text-yellow-600">{event.rsvp_summary.maybe} maybe</span>
						<span class="text-brand-text-muted">{event.rsvp_summary.not_going} can't go</span>
					</div>
				</div>
			{/if}

			<!-- Leader: Attendance Sheet -->
			{#if event.rsvps.length > 0}
				<div class="bg-white rounded-lg border border-brand-border p-4">
					<div class="flex items-center justify-between mb-3">
						<h3 class="text-sm font-medium text-brand-primary">Take Attendance</h3>
						<div class="flex items-center gap-2">
							<span class="text-xs text-brand-text-muted">{attendedIds.size} of {event.rsvps.length} selected</span>
							<button onclick={selectAll} class="text-xs font-medium text-brand-accent hover:text-brand-accent">All</button>
							<button onclick={selectNone} class="text-xs font-medium text-brand-text-muted hover:text-brand-text-secondary">None</button>
						</div>
					</div>
					<div class="divide-y divide-brand-border">
						{#each event.rsvps as rsvp (rsvp.person_id)}
							<label class="flex items-center gap-3 py-2 cursor-pointer">
								<input type="checkbox"
									checked={attendedIds.has(rsvp.person_id)}
									onchange={() => toggleAttendance(rsvp.person_id)}
									class="rounded border-brand-border-strong text-brand-accent focus:ring-brand-accent" />
								<span class="text-sm text-brand-primary">{rsvp.person_name || `Person #${rsvp.person_id}`}</span>
								<span class="text-xs text-brand-text-muted ml-auto">{rsvp.status}</span>
							</label>
						{/each}
					</div>
					<button onclick={saveAttendance} disabled={savingAttendance}
						class="mt-3 px-4 py-1.5 text-sm font-medium rounded-sm text-white bg-brand-accent hover:bg-brand-accent/90 disabled:opacity-50">
						{savingAttendance ? 'Saving...' : 'Save Attendance'}
					</button>
				</div>
			{/if}
		{/if}

		<!-- Delete Confirmation Modal -->
		{#if showDeleteConfirm}
			<!-- svelte-ignore a11y_no_static_element_interactions -->
			<div class="fixed inset-0 z-50 flex items-center justify-center bg-black/40" onclick={() => (showDeleteConfirm = false)} onkeydown={(e) => e.key === 'Escape' && (showDeleteConfirm = false)} role="dialog" aria-modal="true" tabindex="-1">
				<!-- svelte-ignore a11y_no_static_element_interactions -->
				<div class="bg-white rounded-lg shadow-lg p-6 max-w-sm w-full mx-4" onclick={(e) => e.stopPropagation()}>
					<h3 class="text-lg font-medium text-brand-primary">Delete Event</h3>
					<p class="mt-2 text-sm text-brand-text-secondary">
						Delete <strong>{event.title}</strong>? This will remove all RSVPs and attendance records. Cannot be undone.
					</p>
					<div class="mt-4 flex items-center gap-3 justify-end">
						<button onclick={() => (showDeleteConfirm = false)} class="px-4 py-2 text-sm text-brand-text-secondary">Cancel</button>
						<button onclick={handleDelete} disabled={deleting}
							class="px-4 py-2 text-sm font-medium rounded-sm text-white bg-red-600 hover:bg-red-700 disabled:opacity-50">
							{deleting ? 'Deleting...' : 'Delete'}
						</button>
					</div>
				</div>
			</div>
		{/if}
	{/if}
</div>
