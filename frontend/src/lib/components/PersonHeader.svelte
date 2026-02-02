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

	let { person, isEditing, isSaving, onToggleEdit, onSave, onCancel, onRecordDeath }: Props = $props();

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
			<h1 class="text-2xl font-bold text-gray-900 truncate">{formatName(person)}</h1>
			<div class="mt-1 flex flex-wrap items-center gap-x-4 gap-y-1 text-sm text-gray-500">
				{#if person.email}
					<a href="mailto:{person.email}" class="hover:text-blue-600 transition-colors">
						{person.email}
					</a>
				{/if}
				{#if person.phone}
					<a href="tel:{person.phone}" class="hover:text-blue-600 transition-colors">
						{person.phone}
					</a>
				{/if}
				{#if !person.email && !person.phone}
					<span class="text-gray-400">No contact information</span>
				{/if}
			</div>
		</div>

		<div class="flex items-center gap-2 flex-shrink-0">
			{#if isEditing}
				<button
					onclick={onCancel}
					disabled={isSaving}
					class="px-4 py-2 text-sm font-medium text-gray-700 bg-white border border-gray-300 rounded-md hover:bg-gray-50 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-blue-500 disabled:opacity-50"
				>
					Cancel
				</button>
				<button
					onclick={onSave}
					disabled={isSaving}
					class="inline-flex items-center px-4 py-2 text-sm font-medium text-white bg-blue-600 border border-transparent rounded-md hover:bg-blue-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-blue-500 disabled:opacity-50"
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
						class="inline-flex items-center px-4 py-2 text-sm font-medium text-red-600 bg-red-50 border border-red-200 rounded-md hover:bg-red-100 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-red-500 transition-colors"
					>
						<svg class="w-4 h-4 mr-2" fill="none" stroke="currentColor" viewBox="0 0 24 24">
							<path
								stroke-linecap="round"
								stroke-linejoin="round"
								stroke-width="2"
								d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-3L13.732 4c-.77-1.333-2.694-1.333-3.464 0L3.34 16c-.77 1.333.192 3 1.732 3z"
							/>
						</svg>
						Record Death
					</button>
				{/if}
				<button
					onclick={onToggleEdit}
					class="inline-flex items-center px-4 py-2 text-sm font-medium text-gray-700 bg-white border border-gray-300 rounded-md hover:bg-gray-50 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-blue-500"
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
