<script lang="ts">
	import { UserPlus, Plus, Baby, Skull, FileText, FilePlus } from 'lucide-svelte';

	interface Props {
		onRecordSacrament?: () => void;
	}

	let { onRecordSacrament }: Props = $props();
</script>

<div class="bg-white rounded-lg shadow border border-brand-border p-6">
	<h3 class="text-lg font-medium text-brand-primary mb-4">Quick Actions</h3>
	<div class="flex flex-wrap gap-3">
		<a
			href="/register"
			class="inline-flex items-center gap-2 px-5 py-2.5 bg-brand-accent text-white rounded-lg hover:opacity-90 transition-opacity font-medium shadow-sm"
		>
			<UserPlus class="w-5 h-5" />
			Register Household
		</a>
		<a
			href="/people/new"
			class="inline-flex items-center gap-2 px-4 py-2 bg-brand-primary text-white rounded-lg hover:bg-brand-primary-light transition-colors"
		>
			<Plus class="w-5 h-5" />
			Add Person
		</a>
		<a
			href="/households?action=create"
			class="inline-flex items-center gap-2 px-4 py-2 bg-brand-success text-white rounded-lg hover:opacity-90 transition-opacity"
		>
			<Plus class="w-5 h-5" />
			Add Household
		</a>
		<a
			href="/analytics/births/new"
			class="inline-flex items-center gap-2 px-4 py-2 bg-brand-accent text-white rounded-lg hover:opacity-90 transition-opacity"
		>
			<Baby class="w-5 h-5" />
			Record Birth
		</a>
		<a
			href="/analytics/deaths/new"
			class="inline-flex items-center gap-2 px-4 py-2 bg-brand-error text-white rounded-lg hover:opacity-90 transition-opacity"
		>
			<Skull class="w-5 h-5" />
			Record Death
		</a>
		{#if onRecordSacrament}
			<button
				onclick={onRecordSacrament}
				class="inline-flex items-center gap-2 px-4 py-2 bg-brand-primary-light text-white rounded-lg hover:opacity-90 transition-opacity"
			>
				<FileText class="w-5 h-5" />
				Record Sacrament
			</button>
		{:else}
			<a
				href="/people"
				class="inline-flex items-center gap-2 px-4 py-2 bg-brand-primary-light text-white rounded-lg hover:opacity-90 transition-opacity"
			>
				<FilePlus class="w-5 h-5" />
				Record Sacrament
			</a>
		{/if}
	</div>
</div>
