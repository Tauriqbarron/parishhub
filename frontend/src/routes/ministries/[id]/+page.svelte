<script lang="ts">
	import { page } from '$app/stores';
	import { goto } from '$app/navigation';
	import {
		ministryApi,
		type MinistryDetail,
		type MinistryMember,
		type MinistryEvent,
		type MinistryUpdate
	} from '$lib/api';
	import { toasts } from '$lib/stores/toast';
	import Breadcrumbs from '$lib/components/Breadcrumbs.svelte';
	import PageHeader from '$lib/components/PageHeader.svelte';
	import { ArrowLeft, Users, Calendar, Trash2, Edit3, Plus, X, Check } from 'lucide-svelte';

	let ministry = $state<MinistryDetail | null>(null);
	let loading = $state(true);
	let error = $state<string | null>(null);

	// Edit mode
	let isEditing = $state(false);
	let editName = $state('');
	let editDescription = $state('');
	let editIsActive = $state(true);
	let saving = $state(false);

	// Delete confirmation
	let showDeleteConfirm = $state(false);
	let deleting = $state(false);

	// Tab state
	let activeTab = $state<'members' | 'events'>('members');

	const ministryId = $derived(Number($page.params.id));

	async function loadMinistry() {
		loading = true;
		error = null;
		try {
			ministry = await ministryApi.get(ministryId);
			resetEditForm();
		} catch (err) {
			error = err instanceof Error ? err.message : 'Failed to load ministry';
		} finally {
			loading = false;
		}
	}

	function resetEditForm() {
		if (!ministry) return;
		editName = ministry.name;
		editDescription = ministry.description || '';
		editIsActive = ministry.is_active;
	}

	$effect(() => {
		if (ministryId) loadMinistry();
	});

	function startEditing() {
		resetEditForm();
		isEditing = true;
	}

	function cancelEditing() {
		isEditing = false;
		resetEditForm();
	}

	async function saveEdit() {
		if (!ministry || !editName.trim()) return;
		saving = true;
		try {
			const data: MinistryUpdate = {
				name: editName.trim(),
				description: editDescription.trim() || null,
				is_active: editIsActive
			};
			await ministryApi.update(ministryId, data);
			toasts.success('Ministry updated.');
			isEditing = false;
			await loadMinistry();
		} catch (err) {
			toasts.error(err instanceof Error ? err.message : 'Failed to update ministry.');
		} finally {
			saving = false;
		}
	}

	async function handleDelete() {
		deleting = true;
		try {
			await ministryApi.delete(ministryId);
			toasts.success('Ministry deleted.');
			goto('/ministries');
		} catch (err) {
			toasts.error(err instanceof Error ? err.message : 'Failed to delete ministry.');
			showDeleteConfirm = false;
		} finally {
			deleting = false;
		}
	}

	async function handleRemoveMember(member: MinistryMember) {
		if (!ministry) return;
		try {
			await ministryApi.removeMember(ministryId, member.id);
			toasts.success(`Removed ${member.person_name || 'member'} from ministry.`);
			await loadMinistry();
		} catch (err) {
			toasts.error(err instanceof Error ? err.message : 'Failed to remove member.');
		}
	}

	async function handleDeleteEvent(event: MinistryEvent) {
		if (!ministry) return;
		try {
			await ministryApi.deleteEvent(ministryId, event.id);
			toasts.success(`Event "${event.title}" deleted.`);
			await loadMinistry();
		} catch (err) {
			toasts.error(err instanceof Error ? err.message : 'Failed to delete event.');
		}
	}

	function formatDate(dateStr: string): string {
		return new Date(dateStr).toLocaleDateString('en-US', {
			year: 'numeric',
			month: 'short',
			day: 'numeric'
		});
	}
</script>

<div>
	<Breadcrumbs />

	{#if loading}
		<div class="animate-pulse space-y-4">
			<div class="h-8 bg-brand-bg-muted rounded w-1/3"></div>
			<div class="h-4 bg-brand-bg-muted rounded w-1/2"></div>
			<div class="h-32 bg-brand-bg-muted rounded"></div>
		</div>
	{:else if error}
		<div class="p-6 text-center">
			<h3 class="text-sm font-medium text-brand-primary">Error loading ministry</h3>
			<p class="mt-1 text-sm text-brand-text-secondary">{error}</p>
			<div class="mt-4">
				<a
					href="/ministries"
					class="inline-flex items-center gap-1 text-sm text-brand-accent hover:underline"
				>
					<ArrowLeft class="w-4 h-4" /> Back to ministries
				</a>
			</div>
		</div>
	{:else if ministry}
		<!-- Header -->
		<div class="mb-6">
			{#if isEditing}
				<div class="space-y-4">
					<div>
						<label for="edit-name" class="block text-sm font-medium text-brand-primary">
							Name <span class="text-brand-error">*</span>
						</label>
						<input
							id="edit-name"
							type="text"
							bind:value={editName}
							required
							maxlength={200}
							class="mt-1 block w-full rounded-sm border border-brand-border px-3 py-2 text-sm focus:border-brand-accent focus:ring-1 focus:ring-brand-accent outline-none"
						/>
					</div>
					<div>
						<label for="edit-desc" class="block text-sm font-medium text-brand-primary">
							Description
						</label>
						<textarea
							id="edit-desc"
							bind:value={editDescription}
							rows={3}
							maxlength={5000}
							class="mt-1 block w-full rounded-sm border border-brand-border px-3 py-2 text-sm focus:border-brand-accent focus:ring-1 focus:ring-brand-accent outline-none resize-y"
						></textarea>
					</div>
					<div class="flex items-center gap-2">
						<input
							id="edit-active"
							type="checkbox"
							bind:checked={editIsActive}
							class="rounded border-brand-border text-brand-accent focus:ring-brand-accent"
						/>
						<label for="edit-active" class="text-sm text-brand-primary"> Active </label>
					</div>
					<div class="flex items-center gap-2">
						<button
							onclick={saveEdit}
							disabled={saving || !editName.trim()}
							class="inline-flex items-center gap-1 px-3 py-1.5 text-sm font-medium rounded-sm text-white bg-brand-accent hover:opacity-90 disabled:opacity-50"
						>
							<Check class="w-4 h-4" />
							{saving ? 'Saving...' : 'Save'}
						</button>
						<button
							onclick={cancelEditing}
							class="inline-flex items-center gap-1 px-3 py-1.5 text-sm font-medium rounded-sm text-brand-text-secondary hover:text-brand-primary"
						>
							<X class="w-4 h-4" /> Cancel
						</button>
					</div>
				</div>
			{:else}
				<div class="flex items-start justify-between">
					<div>
						<div class="flex items-center gap-2">
							<h1 class="text-2xl font-semibold text-brand-primary">{ministry.name}</h1>
							{#if !ministry.is_active}
								<span
									class="inline-flex items-center px-2 py-0.5 rounded text-xs font-medium bg-brand-bg-muted text-brand-text-secondary"
								>
									Inactive
								</span>
							{/if}
						</div>
						{#if ministry.description}
							<p class="mt-1 text-sm text-brand-text-secondary">{ministry.description}</p>
						{/if}
						<div class="mt-2 flex items-center gap-4 text-sm text-brand-text-secondary">
							<span class="flex items-center gap-1">
								<Users class="w-4 h-4" />
								{ministry.member_count} member{ministry.member_count !== 1 ? 's' : ''}
							</span>
							<span class="flex items-center gap-1">
								<Calendar class="w-4 h-4" />
								{ministry.events.length} event{ministry.events.length !== 1 ? 's' : ''}
							</span>
						</div>
					</div>
					<div class="flex items-center gap-2">
						<button
							onclick={startEditing}
							class="inline-flex items-center gap-1 px-3 py-1.5 text-sm font-medium rounded-sm text-brand-text-secondary hover:text-brand-primary border border-brand-border hover:border-brand-accent"
						>
							<Edit3 class="w-4 h-4" /> Edit
						</button>
						<button
							onclick={() => (showDeleteConfirm = true)}
							class="inline-flex items-center gap-1 px-3 py-1.5 text-sm font-medium rounded-sm text-red-600 hover:text-red-700 border border-red-200 hover:border-red-300"
						>
							<Trash2 class="w-4 h-4" /> Delete
						</button>
					</div>
				</div>
			{/if}
		</div>

		<!-- Delete Confirmation Modal -->
		{#if showDeleteConfirm}
			<div class="fixed inset-0 z-50 flex items-center justify-center bg-black/40">
				<div class="bg-white rounded-lg shadow-lg p-6 max-w-sm w-full mx-4">
					<h3 class="text-lg font-medium text-brand-primary">Delete Ministry</h3>
					<p class="mt-2 text-sm text-brand-text-secondary">
						Are you sure you want to delete <strong>{ministry.name}</strong>? This will remove
						all members and events. This action cannot be undone.
					</p>
					<div class="mt-4 flex items-center gap-3 justify-end">
						<button
							onclick={() => (showDeleteConfirm = false)}
							class="px-4 py-2 text-sm font-medium text-brand-text-secondary hover:text-brand-primary"
						>
							Cancel
						</button>
						<button
							onclick={handleDelete}
							disabled={deleting}
							class="px-4 py-2 text-sm font-medium rounded-sm text-white bg-red-600 hover:bg-red-700 disabled:opacity-50"
						>
							{deleting ? 'Deleting...' : 'Delete'}
						</button>
					</div>
				</div>
			</div>
		{/if}

		<!-- Tabs -->
		<div class="border-b border-brand-border mb-4">
			<nav class="flex gap-4">
				<button
					class="pb-2 text-sm font-medium border-b-2 transition-colors {activeTab === 'members'
						? 'border-brand-accent text-brand-accent'
						: 'border-transparent text-brand-text-secondary hover:text-brand-primary'}"
					onclick={() => (activeTab = 'members')}
				>
					<span class="flex items-center gap-1">
						<Users class="w-4 h-4" />
						Members ({ministry.members.length})
					</span>
				</button>
				<button
					class="pb-2 text-sm font-medium border-b-2 transition-colors {activeTab === 'events'
						? 'border-brand-accent text-brand-accent'
						: 'border-transparent text-brand-text-secondary hover:text-brand-primary'}"
					onclick={() => (activeTab = 'events')}
				>
					<span class="flex items-center gap-1">
						<Calendar class="w-4 h-4" />
						Events ({ministry.events.length})
					</span>
				</button>
			</nav>
		</div>

		<!-- Members Tab -->
		{#if activeTab === 'members'}
			<div class="bg-white rounded-lg border border-brand-border overflow-hidden">
				{#if ministry.members.length === 0}
					<div class="p-6 text-center">
						<Users class="mx-auto h-10 w-10 text-brand-text-muted" />
						<p class="mt-2 text-sm text-brand-text-secondary">
							No members yet. Add members from the person's profile.
						</p>
					</div>
				{:else}
					<div class="divide-y divide-brand-border">
						{#each ministry.members as member (member.id)}
							<div class="px-6 py-3 flex items-center justify-between">
								<div>
									<a
										href="/people/{member.person_id}"
										class="text-sm font-medium text-brand-primary hover:text-brand-accent"
									>
										{member.person_name || `Person #${member.person_id}`}
									</a>
									<div class="text-xs text-brand-text-secondary">
										<span class="capitalize">{member.role}</span>
										{#if member.joined_date}
											&middot; Joined {formatDate(member.joined_date)}
										{/if}
									</div>
								</div>
								<button
									onclick={() => handleRemoveMember(member)}
									class="text-sm text-red-500 hover:text-red-700 p-1"
									title="Remove member"
								>
									<X class="w-4 h-4" />
								</button>
							</div>
						{/each}
					</div>
				{/if}
			</div>
		{/if}

		<!-- Events Tab -->
		{#if activeTab === 'events'}
			<div class="bg-white rounded-lg border border-brand-border overflow-hidden">
				{#if ministry.events.length === 0}
					<div class="p-6 text-center">
						<Calendar class="mx-auto h-10 w-10 text-brand-text-muted" />
						<p class="mt-2 text-sm text-brand-text-secondary">
							No events scheduled yet.
						</p>
					</div>
				{:else}
					<div class="divide-y divide-brand-border">
						{#each ministry.events as event (event.id)}
							<div class="px-6 py-3 flex items-center justify-between">
								<div>
									<h4 class="text-sm font-medium text-brand-primary">{event.title}</h4>
									<div class="text-xs text-brand-text-secondary">
										{formatDate(event.event_date)}
										{#if event.location}
											&middot; {event.location}
										{/if}
										&middot; {event.attendance_count} attended
									</div>
									{#if event.description}
										<p class="mt-1 text-xs text-brand-text-secondary line-clamp-2">
											{event.description}
										</p>
									{/if}
								</div>
								<button
									onclick={() => handleDeleteEvent(event)}
									class="text-sm text-red-500 hover:text-red-700 p-1"
									title="Delete event"
								>
									<Trash2 class="w-4 h-4" />
								</button>
							</div>
						{/each}
					</div>
				{/if}
			</div>
		{/if}

		<!-- Back link -->
		<div class="mt-6">
			<a
				href="/ministries"
				class="inline-flex items-center gap-1 text-sm text-brand-text-secondary hover:text-brand-primary"
			>
				<ArrowLeft class="w-4 h-4" /> Back to ministries
			</a>
		</div>
	{/if}
</div>
