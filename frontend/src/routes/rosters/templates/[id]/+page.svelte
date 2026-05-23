<script lang="ts">
	import { page } from '$app/stores';
	import { goto } from '$app/navigation';
	import { Plus, Trash2, GripVertical, ArrowLeft, Copy } from 'lucide-svelte';
	import { rosterApi, type RosterRole, type RosterTemplate, type RosterTemplateSettings } from '$lib/api/roster';

	let template = $state<RosterTemplate | null>(null);
	let loading = $state(true);
	let name = $state('');
	let description = $state('');
	let recurrence_rule = $state('none');
	let recurrence_end = $state('');
	let is_active = $state(true);
	let settings: RosterTemplateSettings = $state({ keep_assignee: false, auto_open_hours: 168, reminder_hours: [48, 24], allow_self_assign: true });
	let slots = $state<any[]>([]);
	let roles = $state<RosterRole[]>([]);
	let saving = $state(false);
	let error = $state('');
	let slotCounter = $state(100);

	$effect(() => {
		const id = Number($page.params.id);
		rosterApi.getTemplate(id).then(t => {
			template = t;
			name = t.name;
			description = t.description || '';
			recurrence_rule = t.recurrence_rule;
			recurrence_end = t.recurrence_end || '';
			is_active = t.is_active;
			settings = t.settings;
			slots = t.slots.map(s => ({ id: s.id, role_id: s.role_id, label: s.label, sort_order: s.sort_order, min_persons: s.min_persons, max_persons: s.max_persons }));
			loading = false;
		}).catch(() => goto('/rosters/templates'));
		rosterApi.listRoles().then(r => roles = r);
	});

	function addSlot() {
		slots = [...slots, { id: slotCounter++, role_id: 0, label: '', sort_order: slots.length, min_persons: 1, max_persons: 1 }];
	}
	function removeSlot(id: number) { slots = slots.filter(s => s.id !== id); }
	function updateSlot(id: number, field: string, value: any) {
		slots = slots.map(s => s.id === id ? { ...s, [field]: value } : s);
	}

	async function handleSave() {
		if (!template) return;
		if (!name.trim()) { error = 'Name is required'; return; }
		saving = true; error = '';
		try {
			await rosterApi.updateTemplate(template.id, {
				name, description: description || undefined,
				recurrence_rule, recurrence_end: recurrence_end || undefined,
				is_active, settings,
			});
			goto('/rosters/templates');
		} catch (e: any) { error = e.message || 'Failed to update'; }
		finally { saving = false; }
	}

	async function handleDuplicate() {
		if (!template) return;
		try { await rosterApi.duplicateTemplate(template.id); goto('/rosters/templates'); } catch {}
	}
</script>

{#if loading}
	<div class="loading">Loading…</div>
{:else}
	<div class="page">
		<button class="back-btn" onclick={() => goto('/rosters/templates')}><ArrowLeft class="icon-sm" /> Back to Templates</button>
		<div class="header-row">
			<h1>Edit: {template?.name}</h1>
			<button class="btn-secondary" onclick={handleDuplicate}><Copy class="icon-sm" /> Save as New</button>
		</div>

		<section>
			<h2>Details</h2>
			<label>Name <input type="text" bind:value={name} maxlength={200} /></label>
			<label>Description <textarea bind:value={description} rows={2}></textarea></label>
			<label class="toggle-label">
				<input type="checkbox" checked={is_active} onchange={(e) => (is_active = e.currentTarget.checked)} />
				Active
			</label>
		</section>

		<section>
			<h2>Recurrence</h2>
			<label>Rule
				<select bind:value={recurrence_rule}>
					<option value="none">No recurrence</option>
					<option value="weekly">Weekly</option>
					<option value="biweekly">Biweekly</option>
					<option value="monthly">Monthly</option>
				</select>
			</label>
			{#if recurrence_rule !== 'none'}
				<label>End date <input type="date" bind:value={recurrence_end} /></label>
			{/if}
		</section>

		<section>
			<div class="section-header">
				<h2>Slots</h2>
				<button class="btn-secondary" onclick={addSlot}><Plus class="icon-sm" /> Add</button>
			</div>
			{#each slots as slot}
				<div class="slot-row">
					<GripVertical class="icon-sm grip" />
					<select value={slot.role_id} onchange={(e) => updateSlot(slot.id, 'role_id', Number(e.currentTarget.value))}>
						<option value={0}>-- Role --</option>
						{#each roles as r}<option value={r.id}>{r.name}</option>{/each}
					</select>
					<input type="text" value={slot.label} oninput={(e) => updateSlot(slot.id, 'label', e.currentTarget.value)} placeholder="Label" />
					<input type="number" value={slot.min_persons} oninput={(e) => updateSlot(slot.id, 'min_persons', Number(e.currentTarget.value))} min={1} style="width:4rem" />
					<input type="number" value={slot.max_persons} oninput={(e) => updateSlot(slot.id, 'max_persons', Number(e.currentTarget.value))} min={1} style="width:4rem" />
					<button class="icon-btn danger" onclick={() => removeSlot(slot.id)}><Trash2 class="icon-sm" /></button>
				</div>
			{/each}
		</section>

		<section>
			<h2>Settings</h2>
			<label class="toggle-label">
				<input type="checkbox" checked={settings.keep_assignee} onchange={(e) => (settings = { ...settings, keep_assignee: e.currentTarget.checked })} />
				Keep assignees from previous instance
			</label>
			<label class="toggle-label">
				<input type="checkbox" checked={settings.allow_self_assign} onchange={(e) => (settings = { ...settings, allow_self_assign: e.currentTarget.checked })} />
				Allow members to self-assign
			</label>
		<label>
			Publish roster before event
			<select
				value={Math.round(settings.auto_open_hours / 24)}
				onchange={(e) => (settings = { ...settings, auto_open_hours: Number(e.currentTarget.value) * 24 })}
			>
				<option value={1}>1 day before</option>
				<option value={2}>2 days before</option>
				<option value={3}>3 days before</option>
				<option value={5}>5 days before</option>
				<option value={7}>1 week before</option>
				<option value={10}>10 days before</option>
				<option value={14}>2 weeks before</option>
				<option value={21}>3 weeks before</option>
				<option value={30}>30 days before</option>
			</select>
			<span class="helper">Roster automatically opens for members this far ahead of the event</span>
		</label>
	</section>

	{#if error}<p class="form-error">{error}</p>{/if}
		<div class="form-footer">
			<button class="btn-secondary" onclick={() => goto('/rosters/templates')}>Cancel</button>
			<button class="btn-primary" onclick={handleSave} disabled={saving}>{saving ? 'Saving…' : 'Save Changes'}</button>
		</div>
	</div>
{/if}

<style>
	.page { max-width: 48rem; margin: 0 auto; padding: 1.5rem; }
	h1 { font-size: 1.5rem; margin: 0; }
	h2 { font-size: 1rem; font-weight: 600; margin: 0 0 0.75rem 0; }
	.header-row { display: flex; justify-content: space-between; align-items: center; margin-bottom: 2rem; }
	section { margin-bottom: 1.5rem; padding: 1.25rem; background: var(--color-bg-card); border: 1px solid var(--color-border); border-radius: 0.5rem; }
	label { display: flex; flex-direction: column; gap: 0.25rem; font-size: 0.8125rem; font-weight: 500; margin-bottom: 0.75rem; }
	input, textarea, select { padding: 0.5rem 0.75rem; border: 1px solid var(--color-border); border-radius: 0.375rem; font-size: 0.875rem; background: var(--color-bg); color: var(--color-text); }
	textarea { resize: vertical; }
	.section-header { display: flex; justify-content: space-between; align-items: center; margin-bottom: 0.75rem; }
	.slot-row { display: flex; gap: 0.5rem; align-items: center; margin-bottom: 0.5rem; padding: 0.5rem; background: var(--color-bg); border-radius: 0.375rem; }
	.slot-row select { flex: 1; }
	.slot-row input[type="text"] { flex: 2; }
	.grip { color: var(--color-text-secondary); cursor: grab; }
	.toggle-label { flex-direction: row; align-items: center; gap: 0.5rem; cursor: pointer; }
	input[type="checkbox"] { width: 1.125rem; height: 1.125rem; accent-color: var(--color-accent, #D97706); cursor: pointer; border-radius: 0.25rem; }
	.toggle-label input[type="checkbox"] { margin: 0; }
	.form-footer { display: flex; justify-content: flex-end; gap: 0.75rem; margin-top: 1.5rem; }
	.btn-primary, .btn-secondary { padding: 0.5rem 1rem; border-radius: 0.375rem; font-size: 0.875rem; font-weight: 500; cursor: pointer; border: none; display: inline-flex; align-items: center; gap: 0.375rem; }
	.btn-primary { background: var(--color-accent); color: white; }
	.btn-primary:disabled { opacity: 0.5; cursor: not-allowed; }
	.btn-secondary { background: var(--color-bg-hover); color: var(--color-text); border: 1px solid var(--color-border); }
	.icon-btn { background: none; border: none; cursor: pointer; padding: 0.25rem; border-radius: 0.25rem; color: var(--color-text-secondary); }
	.icon-btn.danger:hover { color: var(--color-danger); }
	.icon-sm { width: 1rem; height: 1rem; }
	.back-btn { background: none; border: none; cursor: pointer; color: var(--color-text-secondary); font-size: 0.875rem; display: flex; align-items: center; gap: 0.25rem; margin-bottom: 1rem; }
	.helper { font-size: 0.75rem; color: var(--color-text-secondary); font-weight: 400; margin-top: 0.125rem; }
	.form-error { color: var(--color-danger); font-size: 0.875rem; }
	.loading { text-align: center; padding: 3rem; color: var(--color-text-secondary); }
</style>
