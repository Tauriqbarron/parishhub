<script lang="ts">
	import { UserPlus, Plus, Baby, Skull, FileText, FilePlus } from 'lucide-svelte';

	interface Props {
		onRecordSacrament?: () => void;
	}

	let { onRecordSacrament }: Props = $props();
</script>

<div class="bg-white rounded-lg border border-brand-border p-6">
	<h3 class="text-lg font-semibold text-brand-primary mb-4 tracking-tight">Quick Actions</h3>
	<div class="flex flex-wrap gap-2">
		<a
			href="/register"
			class="inline-flex items-center gap-2 px-4 py-2 bg-brand-accent text-white rounded-sm hover:opacity-90 transition-opacity text-sm font-medium"
		>
			<UserPlus class="w-4 h-4" />
			Register Household
		</a>
		<a
			href="/people/new"
			class="inline-flex items-center gap-2 px-4 py-2 bg-brand-primary text-white rounded-sm hover:bg-brand-primary-light transition-colors text-sm font-medium"
		>
			<Plus class="w-4 h-4" />
			Add Person
		</a>
		<a
			href="/households?action=create"
			class="inline-flex items-center gap-2 px-4 py-2 bg-brand-bg-muted text-brand-primary rounded-sm hover:bg-brand-border transition-colors text-sm font-medium"
		>
			<Plus class="w-4 h-4" />
			Add Household
		</a>
		<a
			href="/analytics/births/new"
			class="inline-flex items-center gap-2 px-4 py-2 bg-brand-bg-muted text-brand-primary rounded-sm hover:bg-brand-border transition-colors text-sm font-medium"
		>
			<Baby class="w-4 h-4" />
			Record Birth
		</a>
		<a
			href="/analytics/deaths/new"
			class="inline-flex items-center gap-2 px-4 py-2 bg-brand-bg-muted text-brand-primary rounded-sm hover:bg-brand-border transition-colors text-sm font-medium"
		>
			<Skull class="w-4 h-4" />
			Record Death
		</a>
		{#if onRecordSacrament}
			<button
				onclick={onRecordSacrament}
				class="inline-flex items-center gap-2 px-4 py-2 bg-brand-bg-muted text-brand-primary rounded-sm hover:bg-brand-border transition-colors text-sm font-medium"
			>
				<FileText class="w-4 h-4" />
				Record Sacrament
			</button>
		{:else}
			<a
				href="/people"
				class="inline-flex items-center gap-2 px-4 py-2 bg-brand-bg-muted text-brand-primary rounded-sm hover:bg-brand-border transition-colors text-sm font-medium"
			>
				<FilePlus class="w-4 h-4" />
				Record Sacrament
			</a>
		{/if}
	</div>
</div>
