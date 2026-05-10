<script lang="ts">
	import { page } from '$app/stores';
	import { goto } from '$app/navigation';
	import { ArrowLeft, Edit3, Trash2, X, Check, Shield, UserPlus, UserMinus } from 'lucide-svelte';
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

	// Leadership management
	let leaderSearch = $state<{ id: number; name: string } | null>(null);
	let addingLeader = $state(false);
	let removingLeaderId = $state<number | null>(null);

	// Delete
	let showDeleteConfirm = $state(false);
	let deleting = $state(false);

	const ministryId = $derived(Number($page.params.id));

	// Filter members into leader + co-leaders only
	const leaders = $derived(
		ministry?.members.filter(m => m.role === 'leader' || m.role === 'co-leader') ?? []
	);

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

	async function addLeader() {
		if (!leaderSearch) return;
		addingLeader = true;
		try {
			await ministryApi.addMember({ ministry_id: ministryId, person_id: leaderSearch.id });
			toasts.success(`${leaderSearch.name} added to leadership.`);
			leaderSearch = null;
			await loadMinistry();
		} catch (err) {
			toasts.error(err instanceof Error ? err.message : 'Failed to add leader.');
		} finally {
			addingLeader = false;
		}
	}

	async function removeLeader(personId: number, personName: string, role: string) {
		removingLeaderId = personId;
		try {
			await ministryApi.removeMember(ministryId, personId);
			toasts.success(`${personName} removed from leadership.`);
			await loadMinistry();
		} catch (err) {
			toasts.error(err instanceof Error ? err.message : 'Failed to remove leader.');
		} finally {
			removingLeaderId = null;
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

		<!-- Leadership Section (Leader + Co-Leaders) -->
		<div class="bg-white rounded-lg border border-brand-border overflow-visible">
			<div class="px-6 py-3 border-b border-brand-border">
				<h2 class="text-sm font-semibold text-brand-primary flex items-center gap-1">
					<Shield class="w-4 h-4" /> Leadership ({leaders.length})
				</h2>
			</div>

			<!-- Add person to leadership -->
			<div class="px-6 py-3 border-b border-brand-border bg-brand-bg-muted/30">
				<div class="flex items-center gap-2">
					<div class="flex-1">
						<PersonSearchInput
							value={leaderSearch}
							placeholder="Search person to add to leadership..."
							onSelect={(v) => {
								if (v && 'id' in v) leaderSearch = { id: v.id, name: v.name };
								else leaderSearch = null;
							}}
						/>
					</div>
					{#if leaderSearch}
						<button onclick={addLeader} disabled={addingLeader}
							class="inline-flex items-center gap-1 px-3 py-1.5 text-sm font-medium rounded-sm text-white bg-brand-accent hover:opacity-90 disabled:opacity-50 whitespace-nowrap">
							<UserPlus class="w-4 h-4" /> {addingLeader ? 'Adding...' : 'Add'}
						</button>
						<button onclick={() => (leaderSearch = null)}
							class="px-2 py-1.5 text-sm text-brand-text-secondary"><X class="w-4 h-4" /></button>
					{/if}
				</div>
				<p class="mt-1 text-xs text-brand-text-secondary">First person becomes the Leader, others become Co-Leaders.</p>
			</div>

			{#if leaders.length === 0}
				<p class="p-6 text-sm text-brand-text-secondary text-center">No leadership assigned. Search above to add someone.</p>
			{:else}
				<div class="divide-y divide-brand-border">
					{#each leaders as member (member.id)}
						<div class="px-6 py-3 flex items-center justify-between">
							<div class="flex items-center gap-3">
								<a href="/people/{member.person_id}" class="group flex items-center gap-2">
									<div class="w-8 h-8 rounded-full bg-brand-accent/10 flex items-center justify-center text-xs font-medium text-brand-accent">
										{(member.person_name || '??').split(' ').map(n => n[0]).join('').slice(0, 2)}
									</div>
									<p class="text-sm font-medium text-brand-primary group-hover:text-brand-accent transition-colors">
										{member.person_name || `Person #${member.person_id}`}
									</p>
								</a>
								{#if member.role === 'leader'}
									<span class="inline-flex items-center gap-1 px-2 py-0.5 rounded-full text-xs font-medium bg-amber-100 text-amber-800">
										<Shield class="w-3 h-3" /> Leader
									</span>
								{:else if member.role === 'co-leader'}
									<span class="inline-flex items-center gap-1 px-2 py-0.5 rounded-full text-xs font-medium bg-blue-50 text-blue-700">
										<Shield class="w-3 h-3" /> Co-Leader
									</span>
								{/if}
							</div>
							<button
								onclick={() => removeLeader(member.person_id, member.person_name || `Person #${member.person_id}`, member.role)}
								disabled={removingLeaderId === member.person_id}
								class="text-red-400 hover:text-red-600 disabled:opacity-50">
								<UserMinus class="w-4 h-4" />
							</button>
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
