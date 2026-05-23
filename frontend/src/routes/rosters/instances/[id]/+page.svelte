<script lang="ts">
	import { page } from '$app/stores';
	import { goto } from '$app/navigation';
	import {
		ArrowLeft, Users, UserPlus, Trash2, X, Check, Search,
		Send, Ban, CheckCircle, Loader2, Calendar, RefreshCw
	} from 'lucide-svelte';
	import PageHeader from '$lib/components/PageHeader.svelte';
	import Breadcrumbs from '$lib/components/Breadcrumbs.svelte';
	import { rosterApi, type RosterInstance, type RosterAssignment, type RosterTemplate } from '$lib/api/roster';
	import { api } from '$lib/api';

	interface PersonResult {
		id: number;
		first_name: string;
		last_name: string;
	}

	let instance = $state<RosterInstance | null>(null);
	let loading = $state(true);
	let error = $state('');

	// Instance mutations
	let mutating = $state(false);
	let mutateError = $state('');

	// Assign modal
	let showAssignModal = $state(false);
	let selectedSlotId = $state<number | null>(null);
	let personSearch = $state('');
	let personResults = $state<PersonResult[]>([]);
	let searching = $state(false);
	let assigning = $state(false);
	let assignError = $state('');
	let selectedPerson = $state<PersonResult | null>(null);

	// Generate inline
	let generating = $state(false);

	$effect(() => {
		const id = Number($page.params.id);
		if (id) loadInstance(id);
	});

	async function loadInstance(id: number) {
		loading = true;
		error = '';
		try {
			instance = await rosterApi.getInstance(id);
		} catch (e: any) {
			error = e.message || 'Failed to load instance';
		} finally {
			loading = false;
		}
	}

	async function handlePublish() {
		if (!instance) return;
		mutating = true;
		mutateError = '';
		try {
			instance = await rosterApi.publishInstance(instance.id);
		} catch (e: any) {
			mutateError = e.message || 'Failed to publish';
		} finally {
			mutating = false;
		}
	}

	async function handleCancel() {
		if (!instance) return;
		mutating = true;
		mutateError = '';
		try {
			instance = await rosterApi.cancelInstance(instance.id);
		} catch (e: any) {
			mutateError = e.message || 'Failed to cancel';
		} finally {
			mutating = false;
		}
	}

	async function handleComplete() {
		if (!instance) return;
		mutating = true;
		mutateError = '';
		try {
			instance = await rosterApi.completeInstance(instance.id);
		} catch (e: any) {
			mutateError = e.message || 'Failed to complete';
		} finally {
			mutating = false;
		}
	}

	async function handleRemove(assignment: RosterAssignment) {
		if (!instance) return;
		if (!confirm(`Remove ${assignment.person_name || 'this assignment'} from the roster?`)) return;
		try {
			await rosterApi.removeAssignment(assignment.id);
			instance = await rosterApi.getInstance(instance.id);
		} catch {
			// Silently fail
		}
	}

	async function handleGenerate() {
		if (!instance) return;
		generating = true;
		try {
			const newInstance = await rosterApi.generateInstance(instance.template_id, instance.date);
			goto(`/rosters/instances/${newInstance.id}`);
		} catch (e: any) {
			mutateError = e.message || 'Failed to generate';
		} finally {
			generating = false;
		}
	}

	// Assign modal
	function openAssignModal() {
		selectedSlotId = null;
		selectedPerson = null;
		personSearch = '';
		personResults = [];
		assignError = '';
		showAssignModal = true;
	}

	function closeAssignModal() {
		showAssignModal = false;
		selectedSlotId = null;
		selectedPerson = null;
	}

	async function searchPersons(query: string) {
		if (query.length < 2) {
			personResults = [];
			return;
		}
		searching = true;
		try {
			personResults = await api.get<PersonResult[]>(`/persons?search=${encodeURIComponent(query)}&limit=10`);
		} catch {
			personResults = [];
		} finally {
			searching = false;
		}
	}

	let searchTimer: ReturnType<typeof setTimeout>;
	function handleSearchInput(e: Event) {
		personSearch = (e.target as HTMLInputElement).value;
		clearTimeout(searchTimer);
		searchTimer = setTimeout(() => searchPersons(personSearch), 300);
	}

	function selectPerson(p: PersonResult) {
		selectedPerson = p;
		personSearch = `${p.first_name} ${p.last_name}`;
		personResults = [];
	}

	async function handleAssign() {
		if (!instance || !selectedSlotId || !selectedPerson) return;
		assigning = true;
		assignError = '';
		try {
			await rosterApi.assignPerson(instance.id, {
				instance_id: instance.id,
				slot_id: selectedSlotId,
				person_id: selectedPerson.id
			});
			closeAssignModal();
			instance = await rosterApi.getInstance(instance.id);
		} catch (e: any) {
			assignError = e.message || 'Failed to assign person';
		} finally {
			assigning = false;
		}
	}

	function statusClass(status: string): string {
		const map: Record<string, string> = {
			draft: 'badge-draft',
			published: 'badge-published',
			completed: 'badge-completed',
			cancelled: 'badge-cancelled'
		};
		return map[status] || 'badge-draft';
	}

	function assignmentStatusClass(status: string): string {
		const map: Record<string, string> = {
			pending: 'asgn-pending',
			accepted: 'asgn-accepted',
			declined: 'asgn-declined',
			completed: 'asgn-completed',
			cancelled: 'asgn-cancelled'
		};
		return map[status] || 'asgn-pending';
	}

	function formatDate(d: string): string {
		return new Date(d + 'T00:00:00').toLocaleDateString('en-US', {
			weekday: 'long',
			month: 'long',
			day: 'numeric',
			year: 'numeric'
		});
	}

	function getAvailableSlots() {
		if (!instance) return [];
		const assignedSlotIds = new Set(instance.assignments.map(a => a.slot_id));
		// We need template slots from the instance — fallback: derive from assignments
		return instance.assignments
			.filter(a => !assignedSlotIds.has(a.slot_id) || true) // show all slots
			.map(a => ({ id: a.slot_id, label: a.slot_label || `Slot #${a.slot_id}`, role_name: a.role_name }));
	}

	// Deduplicate slots for the dropdown
	function uniqueSlots() {
		const seen = new Set<number>();
		const result: { id: number; label: string; role_name?: string }[] = [];
		if (!instance) return result;
		for (const a of instance.assignments) {
			if (!seen.has(a.slot_id)) {
				seen.add(a.slot_id);
				result.push({ id: a.slot_id, label: a.slot_label || `Slot #${a.slot_id}`, role_name: a.role_name });
			}
		}
		return result;
	}
</script>

<Breadcrumbs items={[
	{ label: 'Home', href: '/' },
	{ label: 'Rosters', href: '/rosters' },
	{ label: instance?.template_name || 'Instance' }
]} />

{#if loading}
	<div class="loading-state">
		<Loader2 class="spinner" />
		<p>Loading roster instance…</p>
	</div>
{:else if error}
	<div class="error-state">
		<p>{error}</p>
		<button class="btn-secondary" onclick={() => loadInstance(Number($page.params.id))}>Retry</button>
	</div>
{:else if instance}
	<div class="instance-page">
		<!-- Header -->
		<div class="instance-header">
			<div class="header-left">
				<button class="back-btn" onclick={() => goto('/rosters')}>
					<ArrowLeft class="icon-sm" /> Back
				</button>
				<div class="header-info">
					<h1>{instance.template_name || 'Untitled Roster'}</h1>
					<div class="header-meta">
						<span class="meta-date">
							<Calendar class="icon-sm" />
							{formatDate(instance.date)}
						</span>
						<span class="badge {statusClass(instance.status)}">{instance.status}</span>
					</div>
				</div>
			</div>
			<div class="header-actions">
				{#if instance.status === 'draft'}
					<button class="btn-primary" onclick={handlePublish} disabled={mutating}>
						<Send class="icon-sm" /> Publish
					</button>
					<button class="btn-secondary" onclick={handleGenerate} disabled={generating}>
						<RefreshCw class={generating ? 'icon-sm spin' : 'icon-sm'} /> Regenerate
					</button>
				{:else if instance.status === 'published'}
					<button class="btn-primary" onclick={handleComplete} disabled={mutating}>
						<CheckCircle class="icon-sm" /> Complete
					</button>
					<button class="btn-danger-outline" onclick={handleCancel} disabled={mutating}>
						<Ban class="icon-sm" /> Cancel
					</button>
				{/if}
			</div>
		</div>

		{#if mutateError}
			<div class="error-banner">{mutateError}</div>
		{/if}

		<!-- Stats row -->
		<div class="stats-row">
			<div class="stat">
				<span class="stat-value">{instance.assignments.length}</span>
				<span class="stat-label">Assignments</span>
			</div>
			<div class="stat">
				<span class="stat-value">
					{instance.assignments.filter(a => a.person_id).length}
				</span>
				<span class="stat-label">Filled</span>
			</div>
			<div class="stat">
				<span class="stat-value">
					{instance.assignments.filter(a => a.status === 'accepted').length}
				</span>
				<span class="stat-label">Accepted</span>
			</div>
			<div class="stat">
				<span class="stat-value">
					{instance.assignments.filter(a => a.status === 'declined').length}
				</span>
				<span class="stat-label">Declined</span>
			</div>
		</div>

		<!-- Assignments table -->
		<div class="table-section">
			<div class="table-header-bar">
				<h2>Assignments</h2>
				{#if instance.status === 'draft' || instance.status === 'published'}
					<button class="btn-primary" onclick={openAssignModal}>
						<UserPlus class="icon-sm" /> Assign Person
					</button>
				{/if}
			</div>

			{#if instance.assignments.length === 0}
				<div class="empty-assignments">
					<Users class="empty-icon" />
					<p>No assignments yet. Generate the roster or assign people manually.</p>
				</div>
			{:else}
				<div class="table-container">
					<table>
						<thead>
							<tr>
								<th>Slot</th>
								<th>Role</th>
								<th>Person</th>
								<th>Status</th>
								<th class="th-actions">Actions</th>
							</tr>
						</thead>
						<tbody>
							{#each instance.assignments as assignment}
								<tr>
									<td class="font-medium">{assignment.slot_label || `Slot #${assignment.slot_id}`}</td>
									<td class="text-muted">{assignment.role_name || '—'}</td>
									<td>
										{#if assignment.person_name}
											<span class="person-name">{assignment.person_name}</span>
										{:else}
											<span class="text-muted italic">Unassigned</span>
										{/if}
									</td>
									<td>
										<span class="asgn-badge {assignmentStatusClass(assignment.status)}">
											{assignment.status}
										</span>
									</td>
									<td class="actions">
										{#if assignment.person_id && (instance?.status === 'draft' || instance?.status === 'published')}
											<button
												class="icon-btn danger"
												onclick={() => handleRemove(assignment)}
												title="Remove assignment"
											>
												<Trash2 class="icon-sm" />
											</button>
										{:else if !assignment.person_id && instance?.status === 'draft'}
											<span class="text-muted text-sm">—</span>
										{:else}
											<span class="text-muted text-sm">—</span>
										{/if}
									</td>
								</tr>
							{/each}
						</tbody>
					</table>
				</div>
			{/if}
		</div>
	</div>
{/if}

<!-- Assign Person Modal -->
{#if showAssignModal}
	<div class="modal-overlay" onclick={closeAssignModal} role="dialog">
		<div class="modal" onclick={(e) => e.stopPropagation()}>
			<div class="modal-header">
				<h2>Assign Person</h2>
				<button class="icon-btn" onclick={closeAssignModal}><X class="icon-sm" /></button>
			</div>
			<div class="modal-body">
				<label>
					Slot
					<select bind:value={selectedSlotId}>
						<option value={null}>-- Choose a slot --</option>
						{#each uniqueSlots() as slot}
							<option value={slot.id}>
								{slot.label}{#if slot.role_name} ({slot.role_name}){/if}
							</option>
						{/each}
					</select>
				</label>

				<label>
					Search Person
					<div class="search-wrapper">
						<Search class="search-icon" />
						<input
							type="text"
							value={personSearch}
							oninput={handleSearchInput}
							placeholder="Type at least 2 characters…"
						/>
					</div>
				</label>

				{#if searching}
					<div class="search-status">Searching…</div>
				{:else if personResults.length > 0}
					<div class="person-list">
						{#each personResults as p}
							<button
								class="person-item"
								class:selected={selectedPerson?.id === p.id}
								onclick={() => selectPerson(p)}
							>
								<span class="person-item-name">{p.first_name} {p.last_name}</span>
								{#if selectedPerson?.id === p.id}
									<Check class="icon-sm check-mark" />
								{/if}
							</button>
						{/each}
					</div>
				{:else if personSearch.length >= 2}
					<div class="search-status">No results found.</div>
				{/if}

				{#if assignError}
					<p class="form-error">{assignError}</p>
				{/if}
			</div>
			<div class="modal-footer">
				<button class="btn-secondary" onclick={closeAssignModal}>Cancel</button>
				<button
					class="btn-primary"
					onclick={handleAssign}
					disabled={assigning || !selectedSlotId || !selectedPerson}
				>
					{assigning ? 'Assigning…' : 'Assign'}
				</button>
			</div>
		</div>
	</div>
{/if}

<style>
	.instance-page {
		max-width: 56rem;
		margin: 0 auto;
	}

	/* Header */
	.instance-header {
		display: flex;
		justify-content: space-between;
		align-items: flex-start;
		gap: 1.5rem;
		margin-bottom: 1.5rem;
		padding: 1.25rem;
		background: var(--color-bg-card);
		border: 1px solid var(--color-border);
		border-radius: 0.5rem;
		flex-wrap: wrap;
	}
	.header-left {
		display: flex;
		flex-direction: column;
		gap: 0.75rem;
	}
	.header-info h1 {
		margin: 0;
		font-size: 1.375rem;
		font-weight: 700;
	}
	.header-meta {
		display: flex;
		align-items: center;
		gap: 0.75rem;
		margin-top: 0.375rem;
	}
	.meta-date {
		display: flex;
		align-items: center;
		gap: 0.25rem;
		font-size: 0.875rem;
		color: var(--color-text-secondary);
	}
	.header-actions {
		display: flex;
		align-items: center;
		gap: 0.5rem;
		flex-wrap: wrap;
	}
	.back-btn {
		background: none;
		border: none;
		cursor: pointer;
		color: var(--color-text-secondary);
		font-size: 0.8125rem;
		display: flex;
		align-items: center;
		gap: 0.25rem;
		padding: 0;
	}
	.back-btn:hover {
		color: var(--color-text);
	}

	/* Badges */
	.badge {
		font-size: 0.6875rem;
		font-weight: 600;
		padding: 0.125rem 0.5rem;
		border-radius: 999px;
		text-transform: uppercase;
		letter-spacing: 0.025em;
	}
	.badge-draft { background: #f3f4f6; color: #6b7280; }
	.badge-published { background: #ecfdf5; color: #059669; }
	.badge-completed { background: #eff6ff; color: #2563eb; }
	.badge-cancelled { background: #fef2f2; color: #dc2626; }

	/* Stats row */
	.stats-row {
		display: grid;
		grid-template-columns: repeat(4, 1fr);
		gap: 0.75rem;
		margin-bottom: 1.5rem;
	}
	.stat {
		background: var(--color-bg-card);
		border: 1px solid var(--color-border);
		border-radius: 0.5rem;
		padding: 1rem;
		text-align: center;
		display: flex;
		flex-direction: column;
		gap: 0.25rem;
	}
	.stat-value {
		font-size: 1.5rem;
		font-weight: 700;
		color: var(--color-text);
	}
	.stat-label {
		font-size: 0.75rem;
		color: var(--color-text-secondary);
		text-transform: uppercase;
		letter-spacing: 0.05em;
	}

	/* Table section */
	.table-section {
		background: var(--color-bg-card);
		border: 1px solid var(--color-border);
		border-radius: 0.5rem;
		overflow: hidden;
	}
	.table-header-bar {
		display: flex;
		justify-content: space-between;
		align-items: center;
		padding: 0.75rem 1rem;
		border-bottom: 1px solid var(--color-border);
	}
	.table-header-bar h2 {
		margin: 0;
		font-size: 0.9375rem;
		font-weight: 600;
	}

	/* Table */
	.table-container {
		overflow-x: auto;
	}
	table {
		width: 100%;
		border-collapse: collapse;
	}
	th {
		text-align: left;
		padding: 0.625rem 1rem;
		font-size: 0.75rem;
		font-weight: 600;
		color: var(--color-text-secondary);
		text-transform: uppercase;
		letter-spacing: 0.05em;
		border-bottom: 1px solid var(--color-border);
		background: var(--color-bg-subtle);
	}
	.th-actions {
		text-align: center;
		width: 5rem;
	}
	td {
		padding: 0.625rem 1rem;
		border-bottom: 1px solid var(--color-border);
		vertical-align: middle;
	}
	tr:last-child td {
		border-bottom: none;
	}
	.font-medium {
		font-weight: 500;
	}
	.text-muted {
		color: var(--color-text-secondary);
	}
	.text-sm {
		font-size: 0.8125rem;
	}
	.italic {
		font-style: italic;
	}
	.person-name {
		font-weight: 500;
	}
	.actions {
		display: flex;
		justify-content: center;
		gap: 0.25rem;
	}

	/* Assignment status badges */
	.asgn-badge {
		font-size: 0.6875rem;
		font-weight: 500;
		padding: 0.125rem 0.5rem;
		border-radius: 999px;
		text-transform: capitalize;
	}
	.asgn-pending { background: #f3f4f6; color: #6b7280; }
	.asgn-accepted { background: #ecfdf5; color: #059669; }
	.asgn-declined { background: #fef2f2; color: #dc2626; }
	.asgn-completed { background: #eff6ff; color: #2563eb; }
	.asgn-cancelled { background: #f3f4f6; color: #9ca3af; }

	/* Empty assignments */
	.empty-assignments {
		padding: 3rem 1rem;
		text-align: center;
		display: flex;
		flex-direction: column;
		align-items: center;
		gap: 0.5rem;
		color: var(--color-text-secondary);
	}
	.empty-icon {
		width: 2rem;
		height: 2rem;
		color: var(--color-text-muted);
	}

	/* State containers */
	.loading-state {
		text-align: center;
		padding: 3rem 1rem;
		color: var(--color-text-secondary);
		display: flex;
		flex-direction: column;
		align-items: center;
		gap: 0.5rem;
	}
	.error-state {
		text-align: center;
		padding: 3rem 1rem;
		color: var(--color-error);
		display: flex;
		flex-direction: column;
		align-items: center;
		gap: 0.75rem;
	}
	.error-banner {
		background: var(--color-danger-bg);
		color: var(--color-danger);
		padding: 0.75rem 1rem;
		border-radius: 0.375rem;
		margin-bottom: 1rem;
		font-size: 0.875rem;
	}

	/* Buttons */
	.btn-primary, .btn-secondary, .btn-danger-outline {
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
	.btn-danger-outline {
		background: transparent;
		color: var(--color-danger);
		border: 1px solid var(--color-danger);
	}
	.btn-danger-outline:hover {
		background: var(--color-danger-bg);
	}
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
	.icon-sm { width: 1rem; height: 1rem; flex-shrink: 0; }

	/* Spinner */
	.spinner {
		animation: spin 1s linear infinite;
		width: 1.5rem;
		height: 1.5rem;
	}
	.spin {
		animation: spin 1s linear infinite;
	}
	@keyframes spin {
		to { transform: rotate(360deg); }
	}

	/* Modal */
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
	.modal-header {
		display: flex;
		justify-content: space-between;
		align-items: center;
		padding: 1rem 1.25rem;
		border-bottom: 1px solid var(--color-border);
	}
	.modal-header h2 {
		font-size: 1rem;
		margin: 0;
	}
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
	.modal-body select {
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
		margin: 0;
	}

	/* Search */
	.search-wrapper {
		position: relative;
	}
	.search-wrapper input {
		width: 100%;
		padding: 0.5rem 0.75rem 0.5rem 2.25rem;
		border: 1px solid var(--color-border);
		border-radius: 0.375rem;
		font-size: 0.875rem;
		background: var(--color-bg);
		color: var(--color-text);
		box-sizing: border-box;
	}
	.search-icon {
		position: absolute;
		left: 0.625rem;
		top: 50%;
		transform: translateY(-50%);
		width: 0.875rem;
		height: 0.875rem;
		color: var(--color-text-muted);
		pointer-events: none;
	}
	.search-status {
		font-size: 0.8125rem;
		color: var(--color-text-secondary);
		padding: 0.25rem 0;
	}

	/* Person list */
	.person-list {
		max-height: 12rem;
		overflow-y: auto;
		border: 1px solid var(--color-border);
		border-radius: 0.375rem;
	}
	.person-item {
		display: flex;
		justify-content: space-between;
		align-items: center;
		width: 100%;
		padding: 0.5rem 0.75rem;
		border: none;
		border-bottom: 1px solid var(--color-border);
		background: none;
		cursor: pointer;
		font-size: 0.875rem;
		color: var(--color-text);
		text-align: left;
	}
	.person-item:last-child {
		border-bottom: none;
	}
	.person-item:hover {
		background: var(--color-bg-hover);
	}
	.person-item.selected {
		background: var(--color-accent-muted);
	}
	.person-item-name {
		flex: 1;
	}
	.check-mark {
		color: var(--color-accent);
	}
</style>
