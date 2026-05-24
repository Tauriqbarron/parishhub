<script lang="ts">
	import { goto } from '$app/navigation';
	import { Plus, Copy, Pencil, Trash2, RotateCw } from 'lucide-svelte';
	import PageHeader from '$lib/components/PageHeader.svelte';
	import Breadcrumbs from '$lib/components/Breadcrumbs.svelte';
	import { rosterApi, type RosterTemplate } from '$lib/api/roster';
	import { api } from '$lib/api';

	let templates = $state<RosterTemplate[]>([]);
	let loading = $state(true);
	let activeTab = $state<'all' | 'active' | 'inactive'>('all');

	$effect(() => {
		loadTemplates();
	});

	async function loadTemplates() {
		loading = true;
		try {
			const params: { is_active?: boolean } = {};
			if (activeTab === 'active') params.is_active = true;
			else if (activeTab === 'inactive') params.is_active = false;
			templates = await rosterApi.listTemplates(params);
		} catch {
			templates = [];
		} finally {
			loading = false;
		}
	}

	async function handleDuplicate(t: RosterTemplate) {
		try {
			await rosterApi.duplicateTemplate(t.id);
			loadTemplates();
		} catch {}
	}

	async function handleDelete(t: RosterTemplate) {
		if (!confirm(`Delete "${t.name}"?`)) return;
		try {
			await rosterApi.deleteTemplate(t.id);
			loadTemplates();
		} catch {}
	}

	function recurrenceLabel(rule: string): string {
		return (
			{ weekly: '🔄 Weekly', biweekly: '🔄 Biweekly', monthly: '🔄 Monthly', none: '—' }[rule] ||
			rule
		);
	}

	$effect(() => {
		loadTemplates();
	});
</script>

<Breadcrumbs items={[{ label: 'Home', href: '/' }, { label: 'Rosters' }]} />

<PageHeader
	title="Roster Templates"
	subtitle="Define reusable rosters with slots, recurrence, and settings"
>
	{#snippet actions()}
		<button class="btn-primary" onclick={() => goto('/rosters/templates/new')}>
			<Plus class="icon-sm" /> Create Template
		</button>
	{/snippet}
</PageHeader>

<div class="tabs">
	<button class="tab" class:active={activeTab === 'all'} onclick={() => (activeTab = 'all')}
		>All</button
	>
	<button class="tab" class:active={activeTab === 'active'} onclick={() => (activeTab = 'active')}
		>Active</button
	>
	<button
		class="tab"
		class:active={activeTab === 'inactive'}
		onclick={() => (activeTab = 'inactive')}>Inactive</button
	>
</div>

{#if loading}
	<div class="loading">Loading templates…</div>
{:else if templates.length === 0}
	<div class="empty-state">
		<p>No templates yet.</p>
		<button class="btn-secondary" onclick={() => goto('/rosters/templates/new')}
			>Create your first template</button
		>
	</div>
{:else}
	<div class="card-grid">
		{#each templates as t}
			<div class="card" onclick={() => goto(`/rosters/templates/${t.id}`)}>
				<div class="card-header">
					<h3>{t.name}</h3>
					<span class="badge" class:inactive={!t.is_active}
						>{t.is_active ? 'Active' : 'Inactive'}</span
					>
				</div>
				<div class="card-meta">
					<span>{recurrenceLabel(t.recurrence_rule)}</span>
					<span>{t.slot_count} {t.slot_count === 1 ? 'slot' : 'slots'}</span>
				</div>
				<div class="card-actions" onclick={(e) => e.stopPropagation()}>
					<button class="icon-btn" onclick={() => handleDuplicate(t)} title="Duplicate"
						><Copy class="icon-sm" /></button
					>
					<button class="icon-btn" onclick={() => goto(`/rosters/templates/${t.id}`)} title="Edit"
						><Pencil class="icon-sm" /></button
					>
					<button class="icon-btn danger" onclick={() => handleDelete(t)} title="Delete"
						><Trash2 class="icon-sm" /></button
					>
				</div>
			</div>
		{/each}
	</div>
{/if}

<style>
	.tabs {
		display: flex;
		gap: 0.25rem;
		margin-bottom: 1.5rem;
		border-bottom: 1px solid var(--color-border);
		padding-bottom: 0;
	}
	.tab {
		padding: 0.5rem 1rem;
		background: none;
		border: none;
		cursor: pointer;
		font-size: 0.875rem;
		color: var(--color-text-secondary);
		border-bottom: 2px solid transparent;
	}
	.tab.active {
		color: var(--color-accent);
		border-bottom-color: var(--color-accent);
	}
	.card-grid {
		display: grid;
		grid-template-columns: repeat(auto-fill, minmax(300px, 1fr));
		gap: 1rem;
	}
	.card {
		background: var(--color-bg-card);
		border: 1px solid var(--color-border);
		border-radius: 0.5rem;
		padding: 1rem;
		cursor: pointer;
		transition: box-shadow 0.15s;
	}
	.card:hover {
		box-shadow: 0 2px 8px rgba(0, 0, 0, 0.06);
	}
	.card-header {
		display: flex;
		justify-content: space-between;
		align-items: flex-start;
		margin-bottom: 0.5rem;
	}
	.card-header h3 {
		margin: 0;
		font-size: 0.9375rem;
	}
	.card-meta {
		display: flex;
		gap: 1rem;
		font-size: 0.8125rem;
		color: var(--color-text-secondary);
		margin-bottom: 0.75rem;
	}
	.card-actions {
		display: flex;
		gap: 0.25rem;
		border-top: 1px solid var(--color-border-subtle);
		padding-top: 0.75rem;
	}
	.badge {
		font-size: 0.75rem;
		padding: 0.125rem 0.5rem;
		border-radius: 999px;
		background: #ecfdf5;
		color: #059669;
	}
	.badge.inactive {
		background: var(--color-bg-hover);
		color: var(--color-text-secondary);
	}
	.icon-btn {
		background: none;
		border: none;
		cursor: pointer;
		padding: 0.25rem;
		border-radius: 0.25rem;
		color: var(--color-text-secondary);
	}
	.icon-btn:hover {
		background: var(--color-bg-hover);
	}
	.icon-btn.danger:hover {
		color: var(--color-danger);
	}
	.btn-primary,
	.btn-secondary {
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
	.btn-primary {
		background: var(--color-accent);
		color: white;
	}
	.btn-secondary {
		background: var(--color-bg-hover);
		color: var(--color-text);
		border: 1px solid var(--color-border);
	}
	.icon-sm {
		width: 1rem;
		height: 1rem;
	}
	.loading,
	.empty-state {
		text-align: center;
		padding: 3rem 1rem;
		color: var(--color-text-secondary);
	}
</style>
