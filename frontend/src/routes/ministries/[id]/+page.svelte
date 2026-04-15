<script lang="ts">
	import { page } from '$app/stores';
	import { goto } from '$app/navigation';
	import { ArrowLeft, Edit3, Trash2, X, Check, Shield } from 'lucide-svelte';
	import {
		ministryApi,
		personApi,
		type MinistryDetail,
		type MinistryUpdate,
		type Person
	} from '$lib/api';
	import { toasts } from '$lib/stores/toast';
	import Breadcrumbs from '$lib/components/Breadcrumbs.svelte';
	import PersonSearchInput from '$lib/components/PersonSearchInput.svelte';

	let ministry = $state<MinistryDetail | null>(null);
	let loading = $state(true);
	let error = $state<string | null>(null);

	// Edit mode
	let isEditing = $state(false);
	let editName = $state('');
	let editDescription = $state('');
	let editIsActive = $state(true);
	let saving = $state(false);

	// Leader assignment
	let leaderSearch = $state<{ id: number; name: string } | null>(null);
	let assigningLeader = $state(false);

	// Delete
	let showDeleteConfirm = $state(false);
	let deleting = $state(false);

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

	async function assignLeader() {
		if (!leaderSearch) return;
		assigningLeader = true;
		try {
			await ministryApi.update(ministryId, { leader_id: leaderSearch.id });
			toasts.success(`${leaderSearch.name} assigned as leader.`);
			leaderSearch = null;
			await loadMinistry();
		} catch (err) {
			toasts.error(err instanceof Error ? err.message : 'Failed to assign leader.');
		} finally {
			assigningLeader = false;
		}
	}

	async function removeLeader() {
		if (!ministry) return;
		try {
			await ministryApi.update(ministryId, { leader_id: null });
			toasts.success('Leader removed.');
			await loadMinistry();
		} catch (err) {
			toasts.error(err instanceof Error ? err.message : 'Failed to remove leader.');
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
			<a href="/ministries" class="mt-4 inline-flex items-center gap-1 text-sm text-brand-accent hover:underline">
				<ArrowLeft class="w-4 h-4" /> Back to ministries
			</a>
		</div>
	{:else if ministry}
		<a href="/ministries" class="inline-flex items-center gap-1 text-sm text-brand-text-secondary hover:text-brand-primary mb-4">
			<ArrowLeft class="w-4 h-4" /> Ministries
		</a>

		<!-- Ministry Info -->
		<div class="bg-white rounded-lg border border-brand-border p-6 mb-4">
			{#if isEditing}
				<div class="space-y-4 max-w-lg">
					<div>
						<label for="edit-name" class="block text-sm font-medium text-brand-primary">Name *</label>
						<input id="edit-name" type="text" bind:value={editName} required maxlength={200}
							class="mt-1 block w-full rounded-sm border border-brand-border px-3 py-2 text-sm focus:border-brand-accent focus:ring-1 focus:ring-brand-accent outline-none" />
					</div>
					<div>
						<label for="edit-desc" class="block text-sm font-medium text-brand-primary">Description</label>
						<textarea id="edit-desc" bind:value={editDescription} rows={3} maxlength={5000}
							class="mt-1 block w-full rounded-sm border border-brand-border px-3 py-2 text-sm focus:border-brand-accent focus:ring-1 focus:ring-brand-accent outline-none resize-y"></textarea>
					</div>
					<div class="flex items-center gap-2">
						<input id="edit-active" type="checkbox" bind:checked={editIsActive} class="rounded border-brand-border text-brand-accent focus:ring-brand-accent" />
						<label for="edit-active" class="text-sm text-brand-primary">Active</label>
					</div>
					<div class="flex items-center gap-2 pt-2">
						<button onclick={saveEdit} disabled={saving || !editName.trim()}
							class="inline-flex items-center gap-1 px-3 py-1.5 text-sm font-medium rounded-sm text-white bg-brand-accent hover:opacity-90 disabled:opacity-50">
							<Check class="w-4 h-4" /> {saving ? 'Saving...' : 'Save'}
						</button>
						<button onclick={cancelEditing}
							class="inline-flex items-center gap-1 px-3 py-1.5 text-sm font-medium rounded-sm text-brand-text-secondary hover:text-brand-primary">
							<X class="w-4 h-4" /> Cancel
						</button>
					</div>
				</div>
			{:else}
				<div class="flex items-start justify-between">
					<div>
						<div class="flex items-center gap-2">
							<h1 class="text-xl font-semibold text-brand-primary">{ministry.name}</h1>
							{#if !ministry.is_active}
								<span class="inline-flex items-center px-2 py-0.5 rounded text-xs font-medium bg-brand-bg-muted text-brand-text-secondary">Inactive</span>
							{/if}
						</div>
						{#if ministry.description}
							<p class="mt-1 text-sm text-brand-text-secondary">{ministry.description}</p>
						{/if}
					</div>
					<div class="flex items-center gap-2">
						<button onclick={startEditing}
							class="inline-flex items-center gap-1 px-3 py-1.5 text-sm font-medium rounded-sm text-brand-text-secondary hover:text-brand-primary border border-brand-border hover:border-brand-accent">
							<Edit3 class="w-4 h-4" /> Edit
						</button>
						<button onclick={() => (showDeleteConfirm = true)}
							class="inline-flex items-center gap-1 px-3 py-1.5 text-sm font-medium rounded-sm text-red-600 hover:text-red-700 border border-red-200 hover:border-red-300">
							<Trash2 class="w-4 h-4" /> Delete
						</button>
					</div>
				</div>
			{/if}
		</div>

		<!-- Leader Assignment -->
		<div class="bg-white rounded-lg border border-brand-border p-6 mb-4">
			<h2 class="text-sm font-semibold text-brand-primary mb-3 flex items-center gap-1">
				<Shield class="w-4 h-4" /> Leader
			</h2>

			{#if ministry.leader_id}
				<div class="flex items-center justify-between">
					<div>
						{#each ministry!.members.filter(m => m.person_id === ministry!.leader_id) as leader}
							<p class="text-sm font-medium text-brand-primary">{leader.person_name || `Person #${leader.person_id}`}</p>
						{/each}
						{#if ministry!.members.filter(m => m.person_id === ministry!.leader_id).length === 0}
							<p class="text-sm font-medium text-brand-primary">Leader assigned (ID: {ministry.leader_id})</p>
						{/if}
					</div>
					<button onclick={removeLeader}
						class="text-sm text-red-500 hover:text-red-700">Remove</button>
				</div>
			{:else}
				<p class="text-sm text-brand-text-secondary mb-3">No leader assigned. Search for a person to assign them.</p>
			{/if}

			<div class="mt-3">
				<PersonSearchInput
					value={leaderSearch}
					placeholder="Search person to assign as leader..."
					onSelect={(v) => {
						if (v && 'id' in v) leaderSearch = { id: v.id, name: v.name };
						else leaderSearch = null;
					}}
				/>
				{#if leaderSearch}
					<div class="mt-2 flex items-center gap-2">
						<span class="text-sm text-brand-primary">Assign <strong>{leaderSearch.name}</strong> as leader?</span>
						<button onclick={assignLeader} disabled={assigningLeader}
							class="px-3 py-1 text-sm font-medium rounded-sm text-white bg-brand-accent hover:opacity-90 disabled:opacity-50">
							{assigningLeader ? 'Assigning...' : 'Confirm'}
						</button>
						<button onclick={() => (leaderSearch = null)}
							class="px-3 py-1 text-sm text-brand-text-secondary">Cancel</button>
					</div>
				{/if}
			</div>
		</div>

		<!-- Members list (read-only for admin) -->
		<div class="bg-white rounded-lg border border-brand-border overflow-hidden">
			<div class="px-6 py-3 border-b border-brand-border">
				<h2 class="text-sm font-semibold text-brand-primary">Members ({ministry.members.length})</h2>
			</div>
			{#if ministry.members.length === 0}
				<p class="p-6 text-sm text-brand-text-secondary text-center">No members yet. The leader can add members from the Ministries app.</p>
			{:else}
				<div class="divide-y divide-brand-border">
					{#each ministry.members as member (member.id)}
						<div class="px-6 py-3 flex items-center justify-between">
							<div>
								<p class="text-sm text-brand-primary">{member.person_name || `Person #${member.person_id}`}</p>
								<p class="text-xs text-brand-text-secondary capitalize">{member.role}</p>
							</div>
						</div>
					{/each}
				</div>
			{/if}
		</div>

		<!-- Delete Confirmation -->
		{#if showDeleteConfirm}
			<div class="fixed inset-0 z-50 flex items-center justify-center bg-black/40">
				<div class="bg-white rounded-lg shadow-lg p-6 max-w-sm w-full mx-4">
					<h3 class="text-lg font-medium text-brand-primary">Delete Ministry</h3>
					<p class="mt-2 text-sm text-brand-text-secondary">
						Delete <strong>{ministry.name}</strong>? This removes all members and events. Cannot be undone.
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
