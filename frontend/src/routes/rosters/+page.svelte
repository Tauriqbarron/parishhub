<script lang="ts">
	import { goto } from '$app/navigation';
	import { Calendar, Users, BarChart3, Loader2 } from 'lucide-svelte';
	import PageHeader from '$lib/components/PageHeader.svelte';
	import Breadcrumbs from '$lib/components/Breadcrumbs.svelte';
	import { rosterApi } from '$lib/api/roster';

	interface AggregateInstance {
		id: number;
		template_id: number;
		template_name: string;
		date: string;
		status: string;
		assignment_count: number;
		total_slots: number;
	}

	interface MinistryGroup {
		ministry_id: number;
		ministry_name: string;
		instances: AggregateInstance[];
	}

	interface ParishAggregate {
		date: string;
		parish_rosters: AggregateInstance[];
		ministry_rosters: MinistryGroup[];
	}

	let date = $state(todayString());
	let loading = $state(true);
	let error = $state('');
	let aggregate = $state<ParishAggregate | null>(null);

	$effect(() => {
		loadAggregate(date);
	});

	function todayString(): string {
		return new Date().toISOString().slice(0, 10);
	}

	function formatDate(d: string): string {
		return new Date(d + 'T00:00:00').toLocaleDateString('en-US', {
			weekday: 'long',
			month: 'long',
			day: 'numeric',
			year: 'numeric'
		});
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

	function fillPercent(inst: AggregateInstance): number {
		if (!inst.total_slots) return 0;
		return Math.round((inst.assignment_count / inst.total_slots) * 100);
	}

	function fillColor(pct: number): string {
		if (pct >= 90) return 'var(--color-success)';
		if (pct >= 50) return 'var(--color-accent)';
		return 'var(--color-error)';
	}

	async function loadAggregate(d: string) {
		loading = true;
		error = '';
		try {
			const data = await rosterApi.getParishAggregate(d) as any;
			// Normalize: the API may return flat or grouped data
			if (data && data.parish_rosters !== undefined) {
				aggregate = data as ParishAggregate;
			} else if (Array.isArray(data)) {
				// Fallback: flat array — group by scope
				const parish = (data as any[]).filter((i: any) => !i.ministry_name);
				const ministryMap = new Map<string, any[]>();
				for (const i of data) {
					if (i.ministry_name) {
						const key = i.ministry_name;
						if (!ministryMap.has(key)) ministryMap.set(key, []);
						ministryMap.get(key)!.push(i);
					}
				}
				aggregate = {
					date: d,
					parish_rosters: parish.map(normalizeInstance),
					ministry_rosters: Array.from(ministryMap.entries()).map(([name, instances], idx) => ({
						ministry_id: idx,
						ministry_name: name,
						instances: instances.map(normalizeInstance)
					}))
				};
			} else {
				aggregate = { date: d, parish_rosters: [], ministry_rosters: [] };
			}
		} catch (e: any) {
			error = e.message || 'Failed to load roster data';
			aggregate = null;
		} finally {
			loading = false;
		}
	}

	function normalizeInstance(i: any): AggregateInstance {
		return {
			id: i.id,
			template_id: i.template_id,
			template_name: i.template_name || 'Untitled',
			date: i.date,
			status: i.status || 'draft',
			assignment_count: i.assignments?.length ?? i.assignment_count ?? 0,
			total_slots: i.total_slots ?? i.slot_count ?? (i.assignments?.length ?? 0)
		};
	}

	function handleDateChange(e: Event) {
		const input = e.target as HTMLInputElement;
		date = input.value;
	}
</script>

<Breadcrumbs items={[{ label: 'Home', href: '/' }, { label: 'Rosters' }]} />

<PageHeader title="Parish Roster" subtitle="View and manage all rosters for a given date">
	{#snippet actions()}
		<a
			href="/rosters/templates"
			class="btn-secondary"
		>
			Manage Templates
		</a>
		<a
			href="/rosters/roles"
			class="btn-secondary"
		>
			Manage Roles
		</a>
	{/snippet}
</PageHeader>

<div class="date-bar">
	<label class="date-label">
		<Calendar class="icon-sm" />
		<input
			type="date"
			value={date}
			onchange={handleDateChange}
			class="date-input"
		/>
	</label>
	<span class="date-display">{formatDate(date)}</span>
</div>

{#if loading}
	<div class="loading-state">
		<Loader2 class="spinner" />
		<p>Loading rosters…</p>
	</div>
{:else if error}
	<div class="error-state">
		<p>{error}</p>
		<button class="btn-secondary" onclick={() => loadAggregate(date)}>Retry</button>
	</div>
{:else if !aggregate || (aggregate.parish_rosters.length === 0 && aggregate.ministry_rosters.length === 0)}
	<div class="empty-state">
		<Calendar class="empty-icon" />
		<h3>No rosters for this date</h3>
		<p>Try selecting a different date or generate a new roster instance from a template.</p>
		<a href="/rosters/templates" class="btn-primary">Go to Templates</a>
	</div>
{:else}
	<div class="dashboard">
		<!-- Parish rosters section -->
		{#if aggregate.parish_rosters.length > 0}
			<section class="scope-section">
				<h2 class="scope-heading parish-heading">
					<span class="scope-dot parish-dot"></span>
					Parish Roster
				</h2>
				<div class="card-grid">
					{#each aggregate.parish_rosters as inst}
						<button class="card" onclick={() => goto(`/rosters/instances/${inst.id}`)}>
							<div class="card-top">
								<h3 class="card-title">{inst.template_name}</h3>
								<span class="badge {statusClass(inst.status)}">{inst.status}</span>
							</div>
							<div class="fill-bar-track">
								<div
									class="fill-bar-fill"
									style="width: {Math.min(fillPercent(inst), 100)}%; background: {fillColor(fillPercent(inst))}"
								></div>
							</div>
							<div class="card-meta">
								<span class="meta-item">
									<Users class="icon-sm" />
									{inst.assignment_count} / {inst.total_slots} filled
								</span>
								<span class="fill-text">{fillPercent(inst)}%</span>
							</div>
						</button>
					{/each}
				</div>
			</section>
		{/if}

		<!-- Ministry rosters section -->
		{#each aggregate.ministry_rosters as group}
			<section class="scope-section">
				<h2 class="scope-heading ministry-heading">
					<span class="scope-dot ministry-dot"></span>
					{group.ministry_name}
				</h2>
				<div class="card-grid">
					{#each group.instances as inst}
						<button class="card" onclick={() => goto(`/rosters/instances/${inst.id}`)}>
							<div class="card-top">
								<h3 class="card-title">{inst.template_name}</h3>
								<span class="badge {statusClass(inst.status)}">{inst.status}</span>
							</div>
							<div class="fill-bar-track">
								<div
									class="fill-bar-fill"
									style="width: {Math.min(fillPercent(inst), 100)}%; background: {fillColor(fillPercent(inst))}"
								></div>
							</div>
							<div class="card-meta">
								<span class="meta-item">
									<Users class="icon-sm" />
									{inst.assignment_count} / {inst.total_slots} filled
								</span>
								<span class="fill-text">{fillPercent(inst)}%</span>
							</div>
						</button>
					{/each}
				</div>
			</section>
		{/each}
	</div>
{/if}

<style>
	.date-bar {
		display: flex;
		align-items: center;
		gap: 1rem;
		margin-bottom: 1.5rem;
		padding: 0.75rem 1rem;
		background: var(--color-bg-card);
		border: 1px solid var(--color-border);
		border-radius: 0.5rem;
	}
	.date-label {
		display: flex;
		align-items: center;
		gap: 0.5rem;
		font-size: 0.875rem;
		font-weight: 500;
		color: var(--color-text-secondary);
	}
	.date-input {
		padding: 0.375rem 0.625rem;
		border: 1px solid var(--color-border);
		border-radius: 0.375rem;
		font-size: 0.875rem;
		background: var(--color-bg);
		color: var(--color-text);
	}
	.date-display {
		font-size: 0.875rem;
		color: var(--color-text);
		font-weight: 500;
	}

	/* Scope sections */
	.scope-section {
		margin-bottom: 2rem;
	}
	.scope-heading {
		display: flex;
		align-items: center;
		gap: 0.5rem;
		font-size: 1rem;
		font-weight: 600;
		margin: 0 0 0.75rem 0;
		padding: 0.5rem 0.75rem;
		border-radius: 0.375rem;
	}
	.parish-heading {
		background: var(--color-accent-muted);
		color: var(--color-accent);
	}
	.ministry-heading {
		background: var(--color-bg-card);
		border: 1px solid var(--color-border);
		color: var(--color-text);
	}
	.scope-dot {
		width: 0.5rem;
		height: 0.5rem;
		border-radius: 999px;
	}
	.parish-dot {
		background: var(--color-accent);
	}
	.ministry-dot {
		background: var(--color-text-secondary);
	}

	/* Card grid */
	.card-grid {
		display: grid;
		grid-template-columns: repeat(auto-fill, minmax(280px, 1fr));
		gap: 0.75rem;
	}
	.card {
		background: var(--color-bg-card);
		border: 1px solid var(--color-border);
		border-radius: 0.5rem;
		padding: 1rem;
		cursor: pointer;
		text-align: left;
		width: 100%;
		font: inherit;
		color: inherit;
		transition: box-shadow 0.15s;
	}
	.card:hover {
		box-shadow: 0 2px 8px rgba(0,0,0,0.06);
	}
	.card-top {
		display: flex;
		justify-content: space-between;
		align-items: flex-start;
		margin-bottom: 0.625rem;
		gap: 0.5rem;
	}
	.card-title {
		margin: 0;
		font-size: 0.9375rem;
		font-weight: 600;
		line-height: 1.3;
	}

	/* Fill bar */
	.fill-bar-track {
		width: 100%;
		height: 0.375rem;
		background: var(--color-bg);
		border-radius: 999px;
		margin-bottom: 0.5rem;
		overflow: hidden;
	}
	.fill-bar-fill {
		height: 100%;
		border-radius: 999px;
		transition: width 0.3s ease;
		min-width: 0;
	}
	.card-meta {
		display: flex;
		justify-content: space-between;
		align-items: center;
		font-size: 0.8125rem;
		color: var(--color-text-secondary);
	}
	.meta-item {
		display: flex;
		align-items: center;
		gap: 0.25rem;
	}
	.fill-text {
		font-weight: 600;
		font-size: 0.75rem;
	}

	/* Badges */
	.badge {
		font-size: 0.6875rem;
		font-weight: 600;
		padding: 0.125rem 0.5rem;
		border-radius: 999px;
		text-transform: uppercase;
		letter-spacing: 0.025em;
		white-space: nowrap;
	}
	.badge-draft {
		background: #f3f4f6;
		color: #6b7280;
	}
	.badge-published {
		background: #ecfdf5;
		color: #059669;
	}
	.badge-completed {
		background: #eff6ff;
		color: #2563eb;
	}
	.badge-cancelled {
		background: #fef2f2;
		color: #dc2626;
	}

	/* States */
	.loading-state {
		text-align: center;
		padding: 3rem 1rem;
		color: var(--color-text-secondary);
		display: flex;
		flex-direction: column;
		align-items: center;
		gap: 0.5rem;
	}
	.spinner {
		animation: spin 1s linear infinite;
		width: 1.5rem;
		height: 1.5rem;
	}
	@keyframes spin {
		to { transform: rotate(360deg); }
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
	.empty-state {
		text-align: center;
		padding: 3rem 1rem;
		color: var(--color-text-secondary);
		display: flex;
		flex-direction: column;
		align-items: center;
		gap: 0.5rem;
	}
	.empty-icon {
		width: 2.5rem;
		height: 2.5rem;
		color: var(--color-text-muted);
		margin-bottom: 0.5rem;
	}
	.empty-state h3 {
		margin: 0;
		font-size: 1rem;
		color: var(--color-text);
	}
	.empty-state p {
		margin: 0;
		font-size: 0.875rem;
		max-width: 24rem;
	}

	/* Buttons */
	.btn-primary, .btn-secondary {
		padding: 0.5rem 1rem;
		border-radius: 0.375rem;
		font-size: 0.875rem;
		font-weight: 500;
		cursor: pointer;
		border: none;
		display: inline-flex;
		align-items: center;
		gap: 0.375rem;
		text-decoration: none;
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
		flex-shrink: 0;
	}
</style>
