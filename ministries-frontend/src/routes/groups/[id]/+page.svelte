<script lang="ts">
	import { page } from '$app/stores';
	import { goto } from '$app/navigation';
	import { memberApi, type MinistryMember, type MinistryEvent } from '$lib/api';
	import { ArrowLeft, Users, Calendar, Plus, X, Trash2, Shield } from 'lucide-svelte';
	import EventCard from '$lib/components/EventCard.svelte';

	let ministry = $state<{
		id: number;
		name: string;
		description: string | null;
		is_active: boolean;
		user_role: string | null;
		members: MinistryMember[];
		events: MinistryEvent[];
	} | null>(null);

	let loading = $state(true);
	let error = $state('');
	let activeTab = $state<'members' | 'events'>('members');

$effect(() => {
	const tab = $page.url.searchParams.get('tab');
	if (tab === 'members' || tab === 'events') {
		activeTab = tab;
	}
});

	// Add member form
	let showAddMember = $state(false);
	let searchQuery = $state('');
	let searchResults = $state<Array<{ id: number; first_name: string; last_name: string; email: string | null }>>([]);
	let isSearching = $state(false);
	let searchTimeout: ReturnType<typeof setTimeout>;
	let addingMember = $state(false);
	let addError = $state('');

	// Create event form
	let showCreateEvent = $state(false);
	let eventTitle = $state('');
	let eventDate = $state('');
	let eventLocation = $state('');
	let eventDescription = $state('');
	let creatingEvent = $state(false);
	let eventError = $state('');
	let eventStartTime = $state('');
	let eventEndTime = $state('');
	let eventType = $state('other');
	let eventCapacity = $state('');
	let recurrence = $state('none');
	let recurrenceEnd = $state('');

	const ministryId = $derived(Number($page.params.id));
	const isLeader = $derived(
		ministry?.user_role === 'leader' || ministry?.user_role === 'admin'
	);

	async function loadMinistry() {
		loading = true;
		try {
			ministry = await memberApi.ministryDetail(ministryId);
		} catch (err) {
			error = err instanceof Error ? err.message : 'Failed to load group';
		} finally {
			loading = false;
		}
	}

	$effect(() => {
		if (ministryId) loadMinistry();
	});

	function handleSearchInput(e: Event) {
		const val = (e.target as HTMLInputElement).value;
		searchQuery = val;
		clearTimeout(searchTimeout);
		if (val.trim().length < 2) {
			searchResults = [];
			return;
		}
		searchTimeout = setTimeout(async () => {
			isSearching = true;
			try {
				const result = await memberApi.searchPersons(val.trim());
				const existingIds = new Set(ministry?.members.map(m => m.person_id) ?? []);
				searchResults = result.items.filter(p => !existingIds.has(p.id));
			} catch {
				searchResults = [];
			} finally {
				isSearching = false;
			}
		}, 300);
	}

	async function handleAddMember(person: { id: number; first_name: string; last_name: string }) {
		addingMember = true;
		addError = '';
		try {
			await memberApi.addMember(ministryId, { person_id: person.id });
			showAddMember = false;
			searchQuery = '';
			searchResults = [];
			await loadMinistry();
		} catch (err) {
			addError = err instanceof Error ? err.message : 'Failed to add member';
		} finally {
			addingMember = false;
		}
	}

	async function handleRemoveMember(member: MinistryMember) {
		if (!confirm(`Remove ${member.person_name || 'this member'}?`)) return;
		try {
			await memberApi.removeMember(ministryId, member.id);
			await loadMinistry();
		} catch (err) {
			alert(err instanceof Error ? err.message : 'Failed to remove member');
		}
	}

	async function handleCreateEvent() {
		if (!eventTitle.trim() || !eventDate) return;
		creatingEvent = true;
		eventError = '';
		try {
			await memberApi.createEvent(ministryId, {
				title: eventTitle.trim(),
				event_date: eventDate,
				start_time: eventStartTime || undefined,
				end_time: eventEndTime || undefined,
				event_type: eventType,
				capacity: eventCapacity ? Number(eventCapacity) : undefined,
				recurrence_rule: recurrence !== 'none' ? recurrence : undefined,
				recurrence_end: recurrence !== 'none' && recurrenceEnd ? recurrenceEnd : undefined,
				location: eventLocation.trim() || undefined,
				description: eventDescription.trim() || undefined
			});
			eventTitle = '';
			eventDate = '';
			eventLocation = '';
			eventDescription = '';
			eventStartTime = '';
			eventEndTime = '';
			eventType = 'other';
			eventCapacity = '';
			recurrence = 'none';
			recurrenceEnd = '';
			showCreateEvent = false;
			await loadMinistry();
		} catch (err) {
			eventError = err instanceof Error ? err.message : 'Failed to create event';
		} finally {
			creatingEvent = false;
		}
	}

	function formatDate(dateStr: string): string {
		return new Date(dateStr + 'T00:00:00').toLocaleDateString('en-US', {
			weekday: 'short',
			month: 'short',
			day: 'numeric',
			year: 'numeric'
		});
	}
</script>

<div>
	{#if loading}
	<div class="animate-pulse space-y-4">
		<div class="flex items-center gap-2">
			<div class="h-6 bg-brand-bg-muted rounded w-36"></div>
			<div class="h-5 bg-brand-bg-muted rounded w-16"></div>
		</div>
		<div class="h-4 bg-brand-bg-muted rounded w-48"></div>
		<div class="border-b border-brand-border pb-2">
			<div class="flex gap-4">
				<div class="h-5 bg-brand-bg-muted rounded w-24"></div>
				<div class="h-5 bg-brand-bg-muted rounded w-20"></div>
			</div>
		</div>
		<div class="bg-white rounded-lg border border-brand-border divide-y divide-brand-border">
			{#each [1, 2, 3] as i}
				<div class="px-4 py-3 flex items-center justify-between">
					<div>
						<div class="h-4 bg-brand-bg-muted rounded w-32 mb-1"></div>
						<div class="h-3 bg-brand-bg-muted rounded w-20"></div>
					</div>
					<div class="h-4 w-4 bg-brand-bg-muted rounded"></div>
				</div>
			{/each}
		</div>
	</div>
	{:else if error}
		<div class="p-4 bg-red-50 rounded-lg text-red-700 text-sm">{error}</div>
		<a href="/groups" class="mt-3 inline-flex items-center gap-1 text-sm text-brand-text-secondary">
			<ArrowLeft class="w-4 h-4" /> Back to groups
		</a>
	{:else if ministry}
		<a href="/groups" class="inline-flex items-center gap-1 text-sm text-brand-text-muted hover:text-brand-text-secondary mb-3">
			<ArrowLeft class="w-4 h-4" /> Groups
		</a>

		<div class="mb-4">
			<div class="flex items-center gap-2">
				<h1 class="text-xl font-semibold text-brand-primary tracking-tight">{ministry.name}</h1>
				{#if isLeader}
					<span class="inline-flex items-center gap-0.5 px-2 py-0.5 bg-brand-accent-muted text-brand-accent rounded text-xs font-medium">
						<Shield class="w-3 h-3" /> {ministry.user_role}
					</span>
				{/if}
			</div>
			{#if ministry.description}
				<p class="mt-1 text-sm text-brand-text-secondary">{ministry.description}</p>
			{/if}
		</div>

		<!-- Tabs -->
		<div class="border-b border-brand-border mb-4">
			<div class="flex gap-4">
				<button
					class="pb-2 text-sm font-medium border-b-2 transition-colors
						{activeTab === 'members' ? 'border-orange-500 text-brand-accent' : 'border-transparent text-brand-text-muted hover:text-brand-text-secondary'}"
					onclick={() => (activeTab = 'members')}
				>
					<span class="flex items-center gap-1"><Users class="w-4 h-4" /> Members ({ministry.members.length})</span>
				</button>
				<button
					class="pb-2 text-sm font-medium border-b-2 transition-colors
						{activeTab === 'events' ? 'border-orange-500 text-brand-accent' : 'border-transparent text-brand-text-muted hover:text-brand-text-secondary'}"
					onclick={() => (activeTab = 'events')}
				>
					<span class="flex items-center gap-1"><Calendar class="w-4 h-4" /> Events ({ministry.events.length})</span>
				</button>
			</div>
		</div>

		<!-- Members Tab -->
		{#if activeTab === 'members'}
			{#if isLeader}
				{#if !showAddMember}
					<button
						onclick={() => (showAddMember = true)}
						class="mb-3 inline-flex items-center gap-1 px-3 py-1.5 text-sm font-medium rounded-sm text-brand-accent border border-orange-200 hover:bg-brand-accent-muted"
					>
						<Plus class="w-4 h-4" /> Add Member
					</button>
				{:else}
					<div class="mb-3 bg-white rounded-lg border border-brand-border p-4">
						<div class="flex items-center justify-between mb-3">
							<h3 class="text-sm font-medium text-brand-primary">Add Member</h3>
							<button onclick={() => { showAddMember = false; searchQuery = ''; searchResults = []; }} class="text-brand-text-muted hover:text-brand-text-secondary">
								<X class="w-4 h-4" />
							</button>
						</div>
						{#if addError}
							<p class="mb-2 text-sm text-red-600">{addError}</p>
						{/if}
						<div class="relative">
							<input
								type="text"
								value={searchQuery}
								oninput={handleSearchInput}
								placeholder="Search by name..."
								class="w-full px-3 py-1.5 text-sm border border-brand-border rounded-sm focus:border-brand-accent focus:ring-1 focus:ring-brand-accent outline-none"
							/>
							{#if isSearching}
								<div class="absolute right-3 top-2">
									<svg class="animate-spin h-4 w-4 text-brand-text-muted" fill="none" viewBox="0 0 24 24">
										<circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4"></circle>
										<path class="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4z"></path>
									</svg>
								</div>
							{/if}
							{#if searchResults.length > 0}
								<div class="absolute z-50 mt-1 w-full bg-white border border-brand-border rounded-sm shadow-lg max-h-48 overflow-y-auto">
									{#each searchResults as person (person.id)}
										<button
											type="button"
											onclick={() => handleAddMember(person)}
											disabled={addingMember}
											class="w-full px-4 py-2 text-left hover:bg-brand-accent-muted border-b border-brand-border last:border-b-0 disabled:opacity-50"
										>
											<p class="text-sm font-medium text-brand-primary">{person.first_name} {person.last_name}</p>
											{#if person.email}
												<p class="text-xs text-brand-text-muted">{person.email}</p>
											{/if}
										</button>
									{/each}
								</div>
							{:else if searchQuery.trim().length >= 2 && !isSearching}
								<div class="mt-1 text-xs text-brand-text-muted">No people found</div>
							{/if}
						</div>
					</div>
				{/if}
			{/if}

			<div class="bg-white rounded-lg border border-brand-border divide-y divide-brand-border">
				{#if ministry.members.length === 0}
					<p class="p-4 text-sm text-brand-text-muted text-center">No members yet</p>
				{:else}
					{#each ministry.members as member (member.id)}
						<div class="px-4 py-3 flex items-center justify-between">
							<div>
								<p class="text-sm font-medium text-brand-primary">
									{member.person_name || `Person #${member.person_id}`}
								</p>
								<p class="text-xs text-brand-text-muted">
									<span class="capitalize">{member.role}</span>
									{#if member.joined_date}
										· Joined {formatDate(member.joined_date)}
									{/if}
								</p>
							</div>
							{#if isLeader && member.role !== 'leader' && member.role !== 'admin'}
								<button
									onclick={() => handleRemoveMember(member)}
									class="p-1 text-brand-text-muted hover:text-red-500"
									title="Remove"
								>
									<Trash2 class="w-4 h-4" />
								</button>
							{/if}
						</div>
					{/each}
				{/if}
			</div>
		{/if}

		<!-- Events Tab -->
		{#if activeTab === 'events'}
			{#if isLeader}
				{#if !showCreateEvent}
					<button
						onclick={() => (showCreateEvent = true)}
						class="mb-3 inline-flex items-center gap-1 px-3 py-1.5 text-sm font-medium rounded-sm text-brand-accent border border-orange-200 hover:bg-brand-accent-muted"
					>
						<Plus class="w-4 h-4" /> Create Event
					</button>
				{:else}
					<div class="mb-3 bg-white rounded-lg border border-brand-border p-4">
						<div class="flex items-center justify-between mb-3">
							<h3 class="text-sm font-medium text-brand-primary">New Event</h3>
							<button onclick={() => (showCreateEvent = false)} class="text-brand-text-muted hover:text-brand-text-secondary">
								<X class="w-4 h-4" />
							</button>
						</div>
						{#if eventError}
							<p class="mb-2 text-sm text-red-600">{eventError}</p>
						{/if}
						<div class="space-y-2">
							<input
								type="text"
								bind:value={eventTitle}
								placeholder="Event title"
								class="w-full px-3 py-1.5 text-sm border border-brand-border rounded-sm focus:border-brand-accent focus:ring-1 focus:ring-brand-accent outline-none"
							/>
							<input
								type="date"
								bind:value={eventDate}
								class="w-full px-3 py-1.5 text-sm border border-brand-border rounded-sm focus:border-brand-accent focus:ring-1 focus:ring-brand-accent outline-none"
							/>
							<input
								type="text"
								bind:value={eventLocation}
								placeholder="Location (optional)"
								class="w-full px-3 py-1.5 text-sm border border-brand-border rounded-sm focus:border-brand-accent focus:ring-1 focus:ring-brand-accent outline-none"
							/>
							<textarea
								bind:value={eventDescription}
								placeholder="Description (optional)"
								rows={2}
								class="w-full px-3 py-1.5 text-sm border border-brand-border rounded-sm focus:border-brand-accent focus:ring-1 focus:ring-brand-accent outline-none resize-none"
							></textarea>
							<select
								bind:value={eventType}
								class="w-full px-3 py-1.5 text-sm border border-brand-border rounded-sm focus:border-brand-accent focus:ring-1 focus:ring-brand-accent outline-none"
							>
								<option value="other">Other</option>
								<option value="service">Service</option>
								<option value="meeting">Meeting</option>
								<option value="social">Social</option>
								<option value="outreach">Outreach</option>
							</select>
							<div class="flex gap-2">
								<input
									type="time"
									bind:value={eventStartTime}
									placeholder="Start time"
									class="flex-1 px-3 py-1.5 text-sm border border-brand-border rounded-sm focus:border-brand-accent focus:ring-1 focus:ring-brand-accent outline-none"
								/>
								<input
									type="time"
									bind:value={eventEndTime}
									placeholder="End time"
									class="flex-1 px-3 py-1.5 text-sm border border-brand-border rounded-sm focus:border-brand-accent focus:ring-1 focus:ring-brand-accent outline-none"
								/>
							</div>
							<input
								type="number"
								bind:value={eventCapacity}
								placeholder="Capacity (optional)"
								min="1"
								class="w-full px-3 py-1.5 text-sm border border-brand-border rounded-sm focus:border-brand-accent focus:ring-1 focus:ring-brand-accent outline-none"
							/>
							<select
								bind:value={recurrence}
								class="w-full px-3 py-1.5 text-sm border border-brand-border rounded-sm focus:border-brand-accent focus:ring-1 focus:ring-brand-accent outline-none"
							>
								<option value="none">Does not repeat</option>
								<option value="weekly">Weekly</option>
								<option value="biweekly">Every 2 weeks</option>
								<option value="monthly">Monthly</option>
							</select>
							{#if recurrence !== 'none'}
								<input
									type="date"
									bind:value={recurrenceEnd}
									placeholder="Repeat until"
									class="w-full px-3 py-1.5 text-sm border border-brand-border rounded-sm focus:border-brand-accent focus:ring-1 focus:ring-brand-accent outline-none"
								/>
							{/if}
							<button
								onclick={handleCreateEvent}
								disabled={creatingEvent || !eventTitle.trim() || !eventDate}
								class="px-3 py-1.5 text-sm font-medium rounded-sm text-white bg-brand-accent hover:bg-brand-accent/90 disabled:opacity-50"
							>
								{creatingEvent ? 'Creating...' : 'Create'}
							</button>
						</div>
					</div>
				{/if}
			{/if}

			<div class="bg-white rounded-lg border border-brand-border divide-y divide-brand-border">
				{#if ministry.events.length === 0}
					<p class="p-4 text-sm text-brand-text-muted text-center">No events yet</p>
				{:else}
					{#each ministry.events as event (event.id)}
						<EventCard {event} onclick={() => goto(`/groups/${ministryId}/events/${event.id}`)} />
					{/each}
				{/if}
			</div>
		{/if}
	{/if}
</div>
