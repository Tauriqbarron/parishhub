<script lang="ts">
	import { page } from '$app/stores';
	import { goto } from '$app/navigation';
	import { onMount } from 'svelte';
	import { memberApi, type MinistryMember, type MinistryEvent } from '$lib/api';
	import { ArrowLeft, Users, Calendar, Plus, X, Trash2, Shield } from 'lucide-svelte';

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

	// Add member form
	let showAddMember = $state(false);
	let newEmail = $state('');
	let newName = $state('');
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

	async function handleAddMember() {
		if (!newEmail.trim()) return;
		addingMember = true;
		addError = '';
		try {
			await memberApi.addMember(ministryId, {
				email: newEmail.trim(),
				name: newName.trim() || undefined
			});
			newEmail = '';
			newName = '';
			showAddMember = false;
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
				location: eventLocation.trim() || undefined,
				description: eventDescription.trim() || undefined
			});
			eventTitle = '';
			eventDate = '';
			eventLocation = '';
			eventDescription = '';
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
		<div class="animate-pulse space-y-3">
			<div class="h-6 bg-gray-100 rounded w-1/3"></div>
			<div class="h-4 bg-gray-100 rounded w-1/2"></div>
			<div class="h-32 bg-gray-100 rounded"></div>
		</div>
	{:else if error}
		<div class="p-4 bg-red-50 rounded-lg text-red-700 text-sm">{error}</div>
		<a href="/groups" class="mt-3 inline-flex items-center gap-1 text-sm text-gray-500">
			<ArrowLeft class="w-4 h-4" /> Back to groups
		</a>
	{:else if ministry}
		<a href="/groups" class="inline-flex items-center gap-1 text-sm text-gray-400 hover:text-gray-600 mb-3">
			<ArrowLeft class="w-4 h-4" /> Groups
		</a>

		<div class="mb-4">
			<div class="flex items-center gap-2">
				<h1 class="text-xl font-semibold text-gray-900">{ministry.name}</h1>
				{#if isLeader}
					<span class="inline-flex items-center gap-0.5 px-2 py-0.5 bg-orange-50 text-orange-700 rounded text-xs font-medium">
						<Shield class="w-3 h-3" /> {ministry.user_role}
					</span>
				{/if}
			</div>
			{#if ministry.description}
				<p class="mt-1 text-sm text-gray-500">{ministry.description}</p>
			{/if}
		</div>

		<!-- Tabs -->
		<div class="border-b border-gray-200 mb-4">
			<div class="flex gap-4">
				<button
					class="pb-2 text-sm font-medium border-b-2 transition-colors
						{activeTab === 'members' ? 'border-orange-500 text-orange-600' : 'border-transparent text-gray-400 hover:text-gray-600'}"
					onclick={() => (activeTab = 'members')}
				>
					<span class="flex items-center gap-1"><Users class="w-4 h-4" /> Members ({ministry.members.length})</span>
				</button>
				<button
					class="pb-2 text-sm font-medium border-b-2 transition-colors
						{activeTab === 'events' ? 'border-orange-500 text-orange-600' : 'border-transparent text-gray-400 hover:text-gray-600'}"
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
						class="mb-3 inline-flex items-center gap-1 px-3 py-1.5 text-sm font-medium rounded-md text-orange-600 border border-orange-200 hover:bg-orange-50"
					>
						<Plus class="w-4 h-4" /> Add Member
					</button>
				{:else}
					<div class="mb-3 bg-white rounded-lg border border-gray-200 p-4">
						<div class="flex items-center justify-between mb-3">
							<h3 class="text-sm font-medium text-gray-900">Add Member</h3>
							<button onclick={() => (showAddMember = false)} class="text-gray-400 hover:text-gray-600">
								<X class="w-4 h-4" />
							</button>
						</div>
						{#if addError}
							<p class="mb-2 text-sm text-red-600">{addError}</p>
						{/if}
						<div class="space-y-2">
							<input
								type="email"
								bind:value={newEmail}
								placeholder="Email address"
								class="w-full px-3 py-1.5 text-sm border border-gray-200 rounded-md focus:border-orange-400 focus:ring-1 focus:ring-orange-400 outline-none"
							/>
							<input
								type="text"
								bind:value={newName}
								placeholder="Name (optional)"
								class="w-full px-3 py-1.5 text-sm border border-gray-200 rounded-md focus:border-orange-400 focus:ring-1 focus:ring-orange-400 outline-none"
							/>
							<button
								onclick={handleAddMember}
								disabled={addingMember || !newEmail.trim()}
								class="px-3 py-1.5 text-sm font-medium rounded-md text-white bg-orange-600 hover:bg-orange-700 disabled:opacity-50"
							>
								{addingMember ? 'Adding...' : 'Add'}
							</button>
						</div>
					</div>
				{/if}
			{/if}

			<div class="bg-white rounded-lg border border-gray-200 divide-y divide-gray-100">
				{#if ministry.members.length === 0}
					<p class="p-4 text-sm text-gray-400 text-center">No members yet</p>
				{:else}
					{#each ministry.members as member (member.id)}
						<div class="px-4 py-3 flex items-center justify-between">
							<div>
								<p class="text-sm font-medium text-gray-900">
									{member.person_name || `Person #${member.person_id}`}
								</p>
								<p class="text-xs text-gray-400">
									<span class="capitalize">{member.role}</span>
									{#if member.joined_date}
										· Joined {formatDate(member.joined_date)}
									{/if}
								</p>
							</div>
							{#if isLeader && member.role !== 'leader' && member.role !== 'admin'}
								<button
									onclick={() => handleRemoveMember(member)}
									class="p-1 text-gray-300 hover:text-red-500"
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
						class="mb-3 inline-flex items-center gap-1 px-3 py-1.5 text-sm font-medium rounded-md text-orange-600 border border-orange-200 hover:bg-orange-50"
					>
						<Plus class="w-4 h-4" /> Create Event
					</button>
				{:else}
					<div class="mb-3 bg-white rounded-lg border border-gray-200 p-4">
						<div class="flex items-center justify-between mb-3">
							<h3 class="text-sm font-medium text-gray-900">New Event</h3>
							<button onclick={() => (showCreateEvent = false)} class="text-gray-400 hover:text-gray-600">
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
								class="w-full px-3 py-1.5 text-sm border border-gray-200 rounded-md focus:border-orange-400 focus:ring-1 focus:ring-orange-400 outline-none"
							/>
							<input
								type="date"
								bind:value={eventDate}
								class="w-full px-3 py-1.5 text-sm border border-gray-200 rounded-md focus:border-orange-400 focus:ring-1 focus:ring-orange-400 outline-none"
							/>
							<input
								type="text"
								bind:value={eventLocation}
								placeholder="Location (optional)"
								class="w-full px-3 py-1.5 text-sm border border-gray-200 rounded-md focus:border-orange-400 focus:ring-1 focus:ring-orange-400 outline-none"
							/>
							<textarea
								bind:value={eventDescription}
								placeholder="Description (optional)"
								rows={2}
								class="w-full px-3 py-1.5 text-sm border border-gray-200 rounded-md focus:border-orange-400 focus:ring-1 focus:ring-orange-400 outline-none resize-none"
							></textarea>
							<button
								onclick={handleCreateEvent}
								disabled={creatingEvent || !eventTitle.trim() || !eventDate}
								class="px-3 py-1.5 text-sm font-medium rounded-md text-white bg-orange-600 hover:bg-orange-700 disabled:opacity-50"
							>
								{creatingEvent ? 'Creating...' : 'Create'}
							</button>
						</div>
					</div>
				{/if}
			{/if}

			<div class="bg-white rounded-lg border border-gray-200 divide-y divide-gray-100">
				{#if ministry.events.length === 0}
					<p class="p-4 text-sm text-gray-400 text-center">No events yet</p>
				{:else}
					{#each ministry.events as event (event.id)}
						<div class="px-4 py-3">
							<h4 class="text-sm font-medium text-gray-900">{event.title}</h4>
							<p class="text-xs text-gray-400">
								{formatDate(event.event_date)}
								{#if event.location}· {event.location}{/if}
								· {event.attendance_count} attended
							</p>
							{#if event.description}
								<p class="mt-1 text-xs text-gray-400">{event.description}</p>
							{/if}
						</div>
					{/each}
				{/if}
			</div>
		{/if}
	{/if}
</div>
