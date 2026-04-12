<script lang="ts">
	import type { PersonWithRelations } from '$lib/api';

	interface Props {
		person: PersonWithRelations;
		isEditing: boolean;
		isSaving: boolean;
		onToggleEdit: () => void;
		onSave: () => void;
		onCancel: () => void;
		onRecordDeath?: () => void;
	}

	let { person, isEditing, isSaving, onToggleEdit, onSave, onCancel, onRecordDeath }: Props =
		$props();

	const isDeceased = $derived(person.death !== null);

	function formatName(p: PersonWithRelations): string {
		const parts = [p.first_name];
		if (p.middle_name) parts.push(p.middle_name);
		parts.push(p.last_name);
		return parts.join(' ');
	}
</script>

<div class="bg-white rounded-lg shadow p-6">
	<div class="flex flex-col sm:flex-row sm:items-center sm:justify-between gap-4">
		<div class="min-w-0">
			<div class="flex items-center gap-3">
				<h1 class="text-2xl font-bold text-brand-primary truncate">{formatName(person)}</h1>
				{#if isDeceased}
					<span
						class="inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium bg-brand-bg-subtle text-brand-primary border border-brand-border"
					>
						<svg class="w-3 h-3 mr-1" fill="currentColor" viewBox="0 0 24 24">
							<path
								d="M12 2c.3 0 .5.2.5.5v9.5h9.5c.3 0 .5.2.5.5s-.2.5-.5.5H12.5v9.5c0 .3-.2.5-.5.5s-.5-.2-.5-.5V12.5H2c-.3 0-.5-.2-.5-.5s.2-.5.5-.5h9.5V2.5c0-.3.2-.5.5-.5z"
							/>
						</svg>
						Deceased
					</span>
				{/if}
			</div>
			<div
				class="mt-1 flex flex-wrap items-center gap-x-4 gap-y-1 text-sm text-brand-text-secondary"
			>
				{#if person.email}
					<a href="mailto:{person.email}" class="hover:text-brand-accent transition-colors">
						{person.email}
					</a>
				{/if}
				{#if person.phone}
					<a href="tel:{person.phone}" class="hover:text-brand-accent transition-colors">
						{person.phone}
					</a>
				{/if}
				{#if !person.email && !person.phone}
					<span class="text-brand-text-muted">No contact information</span>
				{/if}
			</div>
		</div>

		<div class="flex items-center gap-2 flex-shrink-0">
			{#if isEditing}
				<button
					onclick={onCancel}
					disabled={isSaving}
					class="px-4 py-2 text-sm font-medium text-brand-primary bg-white border border-brand-border rounded-md hover:bg-brand-bg-subtle focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-brand-accent disabled:opacity-50"
				>
					Cancel
				</button>
				<button
					onclick={onSave}
					disabled={isSaving}
					class="inline-flex items-center px-4 py-2 text-sm font-medium text-white bg-brand-accent border border-transparent rounded-md hover:bg-brand-accent/90 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-brand-accent disabled:opacity-50"
				>
					{#if isSaving}
						<svg class="w-4 h-4 mr-2 animate-spin" fill="none" viewBox="0 0 24 24">
							<circle
								class="opacity-25"
								cx="12"
								cy="12"
								r="10"
								stroke="currentColor"
								stroke-width="4"
							></circle>
							<path
								class="opacity-75"
								fill="currentColor"
								d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"
							></path>
						</svg>
						Saving...
					{:else}
						Save
					{/if}
				</button>
			{:else}
				{#if !isDeceased && onRecordDeath}
					<button
						onclick={onRecordDeath}
						class="inline-flex items-center px-4 py-2 text-sm font-medium text-brand-text-secondary bg-brand-bg-subtle border border-brand-border rounded-md hover:bg-brand-bg-muted focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-brand-border transition-colors"
					>
						<svg class="w-4 h-4 mr-2" fill="currentColor" viewBox="0 0 24 24">
							<path
								d="M12 2c.3 0 .5.2.5.5v9.5h9.5c.3 0 .5.2.5.5s-.2.5-.5.5H12.5v9.5c0 .3-.2.5-.5.5s-.5-.2-.5-.5V12.5H2c-.3 0-.5-.2-.5-.5s.2-.5.5-.5h9.5V2.5c0-.3.2-.5.5-.5z"
							/>
						</svg>
						Record Death
					</button>
				{/if}
				<button
					onclick={onToggleEdit}
					class="inline-flex items-center px-4 py-2 text-sm font-medium text-brand-primary bg-white border border-brand-border rounded-md hover:bg-brand-bg-subtle focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-brand-accent"
				>
					<svg class="w-4 h-4 mr-2" fill="none" stroke="currentColor" viewBox="0 0 24 24">
						<path
							stroke-linecap="round"
							stroke-linejoin="round"
							stroke-width="2"
							d="M11 5H6a2 2 0 00-2 2v11a2 2 0 002 2h11a2 2 0 002-2v-5m-1.414-9.414a2 2 0 112.828 2.828L11.828 15H9v-2.828l8.586-8.586z"
						/>
					</svg>
					Edit
				</button>
			{/if}
		</div>
	</div>
</div>
