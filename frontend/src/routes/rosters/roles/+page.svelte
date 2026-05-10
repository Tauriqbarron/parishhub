<script lang="ts">
	import { Plus, Trash2, Pencil, Users, X, Check } from 'lucide-svelte';
	import PageHeader from '$lib/components/PageHeader.svelte';
	import Breadcrumbs from '$lib/components/Breadcrumbs.svelte';
	import { rosterApi, type RosterRole } from '$lib/api/roster';
	import { api } from '$lib/api';

	interface Person {
		id: number;
		first_name: string;
		last_name: string;
	}

	let roles = $state<RosterRole[]>([]);
	let loading = $state(true);
	let error = $state('');

	// Create/Edit modal
	let showModal = $state(false);
	let editingRole = $state<RosterRole | null>(null);
	let nameInput = $state('');
	let descInput = $state('');
	let saving = $state(false);
	let saveError = $state('');

	// Delete dialog
	let deletingRole = $state<RosterRole | null>(null);
	let deleteError = $state('');
	let deleting = $state(false);

	// Assign person modal
	let assignRole = $state<RosterRole | null>(null);
	let persons = $state<Person[]>([]);
	let selectedPersonId = $state<number | null>(null);
	let assigning = $state(false);

	$effect(() => {
		loadRoles();
	});

	async function loadRoles() {
		loading = true;
		error = '';
		try {
			roles = await rosterApi.listRoles();
		} catch (e: any) {
			error = e.message || 'Failed to load roles';
		} finally {
			loading = false;
		}
	}

	function openCreate() {
		editingRole = null;
		nameInput = '';
		descInput = '';
		saveError = '';
		showModal = true;
	}

	function openEdit(role: RosterRole) {
		editingRole = role;
		nameInput = role.name;
		descInput = role.description || '';
		saveError = '';
		showModal = true;
	}

	function closeModal() {
		showModal = false;
		editingRole = null;
	}

	async function handleSave() {
		if (!nameInput.trim()) return;
		saving = true;
		saveError = '';
		try {
			if (editingRole) {
				await rosterApi.updateRole(editingRole.id, { name: nameInput, description: descInput || undefined });
			} else {
				await rosterApi.createRole({ name: nameInput, description: descInput || undefined });
			}
			closeModal();
			await loadRoles();
		} catch (e: any) {
			saveError = e.message || 'Failed to save role';
		} finally {
			saving = false;
		}
	}

	function confirmDelete(role: RosterRole) {
		deletingRole = role;
		deleteError = '';
	}

	async function handleDelete() {
		if (!deletingRole) return;
		deleting = true;
		deleteError = '';
		try {
			await rosterApi.deleteRole(deletingRole.id);
			deletingRole = null;
			await loadRoles();
		} catch (e: any) {
			deleteError = e.message || 'Failed to delete role';
		} finally {
			deleting = false;
		}
	}

	async function openAssign(role: RosterRole) {
		assignRole = role;
		selectedPersonId = null;
		try {
			persons = await api.get<Person[]>('/persons?limit=1000');
		} catch {
			persons = [];
		}
	}

	async function handleAssign() {
		if (!assignRole || !selectedPersonId) return;
		assigning = true;
		try {
			await rosterApi.assignRole(assignRole.id, selectedPersonId);
			assignRole = null;
			await loadRoles();
		} catch (e: any) {
			// Silently fail — user can retry
		} finally {
			assigning = false;
		}
	}
</script>

<Breadcrumbs items={[{ label: 'Home', href: '/' }, { label: 'Rosters', href: '/rosters' }, { label: 'Roles' }]} />

<PageHeader title="Roster Roles" description="Manage capability badges assigned to parish members (Reader, Usher, Sacristan, etc.)">
	<button class="btn-primary" onclick={openCreate}>
		<Plus class="icon-sm" /> Add Role
	</button>
</PageHeader>

{#if error}
	<div class="error-banner">{error}</div>
{/if}

{#if loading}
	<div class="loading">Loading roles…</div>
{:else if roles.length === 0}
	<div class="empty-state">
		<p>No roster roles defined yet.</p>
		<button class="btn-secondary" onclick={openCreate}>Create your first role</button>
	</div>
{:else}
	<div class="table-container">
		<table>
			<thead>
				<tr>
					<th>Name</th>
					<th>Description</th>
					<th>Persons</th>
					<th>Actions</th>
				</tr>
			</thead>
			<tbody>
				{#each roles as role}
					<tr>
						<td class="font-medium">{role.name}</td>
						<td class="text-muted">{role.description || '—'}</td>
						<td>
							<button class="link-btn" onclick={() => openAssign(role)}>
								{role.person_count} {role.person_count === 1 ? 'person' : 'persons'}
							</button>
						</td>
						<td class="actions">
							<button class="icon-btn" onclick={() => openEdit(role)} title="Edit">
								<Pencil class="icon-sm" />
							</button>
							<button class="icon-btn danger" onclick={() => confirmDelete(role)} title="Delete">
								<Trash2 class="icon-sm" />
							</button>
						</td>
					</tr>
				{/each}
			</tbody>
		</table>
	</div>
{/if}

<!-- Create/Edit Modal -->
{#if showModal}
	<div class="modal-overlay" onclick={closeModal} role="dialog">
		<div class="modal" onclick={(e) => e.stopPropagation()}>
			<div class="modal-header">
				<h2>{editingRole ? 'Edit Role' : 'Create Role'}</h2>
				<button class="icon-btn" onclick={closeModal}><X class="icon-sm" /></button>
			</div>
			<div class="modal-body">
				<label>
					Name
					<input type="text" bind:value={nameInput} placeholder="e.g. Reader" maxlength={100} />
				</label>
				<label>
					Description
					<textarea bind:value={descInput} placeholder="Optional description" rows={3}></textarea>
				</label>
				{#if saveError}<p class="form-error">{saveError}</p>{/if}
			</div>
			<div class="modal-footer">
				<button class="btn-secondary" onclick={closeModal}>Cancel</button>
				<button class="btn-primary" onclick={handleSave} disabled={saving || !nameInput.trim()}>
					{saving ? 'Saving…' : editingRole ? 'Save' : 'Create'}
				</button>
			</div>
		</div>
	</div>
{/if}

<!-- Delete Confirm Dialog -->
{#if deletingRole}
	<div class="modal-overlay" onclick={() => (deletingRole = null)} role="dialog">
		<div class="modal modal-sm" onclick={(e) => e.stopPropagation()}>
			<div class="modal-header">
				<h2>Delete Role</h2>
			</div>
			<div class="modal-body">
				<p>Are you sure you want to delete <strong>{deletingRole.name}</strong>?</p>
				<p class="text-muted text-sm">This cannot be undone. Roles referenced by template slots cannot be deleted.</p>
				{#if deleteError}<p class="form-error">{deleteError}</p>{/if}
			</div>
			<div class="modal-footer">
				<button class="btn-secondary" onclick={() => (deletingRole = null)}>Cancel</button>
				<button class="btn-danger" onclick={handleDelete} disabled={deleting}>Delete</button>
			</div>
		</div>
	</div>
{/if}

<!-- Assign Person Modal -->
{#if assignRole}
	<div class="modal-overlay" onclick={() => (assignRole = null)} role="dialog">
		<div class="modal modal-sm" onclick={(e) => e.stopPropagation()}>
			<div class="modal-header">
				<h2>Assign <strong>{assignRole.name}</strong></h2>
				<button class="icon-btn" onclick={() => (assignRole = null)}><X class="icon-sm" /></button>
			</div>
			<div class="modal-body">
				<label>
					Select Person
					<select bind:value={selectedPersonId}>
						<option value={null}>-- Choose --</option>
						{#each persons as p}
							<option value={p.id}>{p.first_name} {p.last_name}</option>
						{/each}
					</select>
				</label>
			</div>
			<div class="modal-footer">
				<button class="btn-secondary" onclick={() => (assignRole = null)}>Cancel</button>
				<button class="btn-primary" onclick={handleAssign} disabled={assigning || !selectedPersonId}>Assign</button>
			</div>
		</div>
	</div>
{/if}

<style>
	.table-container {
		background: var(--color-bg-card);
		border: 1px solid var(--color-border);
		border-radius: 0.5rem;
		overflow: hidden;
	}
	table {
		width: 100%;
		border-collapse: collapse;
	}
	th {
		text-align: left;
		padding: 0.75rem 1rem;
		font-size: 0.8125rem;
		font-weight: 600;
		color: var(--color-text-secondary);
		border-bottom: 1px solid var(--color-border);
	}
	td {
		padding: 0.75rem 1rem;
		border-bottom: 1px solid var(--color-border-subtle);
	}
	tr:last-child td { border-bottom: none; }
	.font-medium { font-weight: 500; }
	.text-muted { color: var(--color-text-secondary); }
	.text-sm { font-size: 0.8125rem; }
	.actions { display: flex; gap: 0.25rem; }
	.link-btn {
		background: none;
		border: none;
		color: var(--color-accent);
		cursor: pointer;
		font-size: inherit;
		padding: 0;
		text-decoration: underline;
	}
	.link-btn:hover { color: var(--color-accent-hover); }
	.icon-btn {
		background: none;
		border: none;
		cursor: pointer;
		padding: 0.25rem;
		border-radius: 0.25rem;
		color: var(--color-text-secondary);
	}
	.icon-btn:hover { background: var(--color-bg-hover); }
	.icon-btn.danger:hover { color: var(--color-danger); background: var(--color-danger-bg); }
	.btn-primary, .btn-secondary, .btn-danger {
		padding: 0.5rem 1rem;
		border-radius: 0.375rem;
		font-size: 0.875rem;
		font-weight: 500;
		cursor: pointer;
		border: none;
		display: inline-flex;
		align-items: center;
		gap: 0.375rem;
	}
	.btn-primary { background: var(--color-accent); color: white; }
	.btn-primary:disabled { opacity: 0.5; cursor: not-allowed; }
	.btn-secondary { background: var(--color-bg-hover); color: var(--color-text); border: 1px solid var(--color-border); }
	.btn-danger { background: var(--color-danger); color: white; }
	.icon-sm { width: 1rem; height: 1rem; }
	.loading, .empty-state {
		text-align: center;
		padding: 3rem 1rem;
		color: var(--color-text-secondary);
	}
	.error-banner {
		background: var(--color-danger-bg);
		color: var(--color-danger);
		padding: 0.75rem 1rem;
		border-radius: 0.375rem;
		margin-bottom: 1rem;
	}
	.modal-overlay {
		position: fixed;
		inset: 0;
		background: rgba(0,0,0,0.4);
		display: flex;
		align-items: center;
		justify-content: center;
		z-index: 100;
	}
	.modal {
		background: var(--color-bg-card);
		border-radius: 0.5rem;
		width: 100%;
		max-width: 28rem;
		box-shadow: 0 4px 24px rgba(0,0,0,0.12);
	}
	.modal-sm { max-width: 24rem; }
	.modal-header {
		display: flex;
		justify-content: space-between;
		align-items: center;
		padding: 1rem 1.25rem;
		border-bottom: 1px solid var(--color-border);
	}
	.modal-header h2 { font-size: 1rem; margin: 0; }
	.modal-body {
		padding: 1.25rem;
		display: flex;
		flex-direction: column;
		gap: 0.75rem;
	}
	.modal-body label {
		display: flex;
		flex-direction: column;
		gap: 0.25rem;
		font-size: 0.8125rem;
		font-weight: 500;
	}
	.modal-body input, .modal-body textarea, .modal-body select {
		padding: 0.5rem 0.75rem;
		border: 1px solid var(--color-border);
		border-radius: 0.375rem;
		font-size: 0.875rem;
		background: var(--color-bg);
		color: var(--color-text);
	}
	.modal-footer {
		display: flex;
		justify-content: flex-end;
		gap: 0.5rem;
		padding: 0.75rem 1.25rem;
		border-top: 1px solid var(--color-border);
	}
	.form-error {
		color: var(--color-danger);
		font-size: 0.8125rem;
	}
</style>
