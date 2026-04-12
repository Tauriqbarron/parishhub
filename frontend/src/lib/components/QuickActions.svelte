<script lang="ts">
	import { UserPlus, Plus, Baby, Skull, FileText, FilePlus } from 'lucide-svelte';

	interface Props {
		onRecordSacrament?: () => void;
	}

	let { onRecordSacrament }: Props = $props();
</script>

<div class="bg-white rounded-lg shadow p-6">
	<h3 class="text-lg font-medium text-gray-900 mb-4">Quick Actions</h3>
	<div class="flex flex-wrap gap-3">
		<a
			href="/register"
			class="inline-flex items-center gap-2 px-5 py-2.5 bg-indigo-600 text-white rounded-lg hover:bg-indigo-700 transition-colors font-medium shadow-sm"
		>
			<UserPlus class="w-5 h-5" />
			Register Household
		</a>
		<a
			href="/people/new"
			class="inline-flex items-center gap-2 px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition-colors"
		>
			<Plus class="w-5 h-5" />
			Add Person
		</a>
		<a
			href="/households?action=create"
			class="inline-flex items-center gap-2 px-4 py-2 bg-green-600 text-white rounded-lg hover:bg-green-700 transition-colors"
		>
			<Plus class="w-5 h-5" />
			Add Household
		</a>
		<a
			href="/analytics/births/new"
			class="inline-flex items-center gap-2 px-4 py-2 bg-pink-600 text-white rounded-lg hover:bg-pink-700 transition-colors"
		>
			<Baby class="w-5 h-5" />
			Record Birth
		</a>
		<a
			href="/analytics/deaths/new"
			class="inline-flex items-center gap-2 px-4 py-2 bg-red-600 text-white rounded-lg hover:bg-red-700 transition-colors"
		>
			<Skull class="w-5 h-5" />
			Record Death
		</a>
		{#if onRecordSacrament}
			<button
				onclick={onRecordSacrament}
				class="inline-flex items-center gap-2 px-4 py-2 bg-purple-600 text-white rounded-lg hover:bg-purple-700 transition-colors"
			>
				<FileText class="w-5 h-5" />
				Record Sacrament
			</button>
		{:else}
			<a
				href="/people"
				class="inline-flex items-center gap-2 px-4 py-2 bg-purple-600 text-white rounded-lg hover:bg-purple-700 transition-colors"
			>
				<FilePlus class="w-5 h-5" />
				Record Sacrament
			</a>
		{/if}
	</div>
</div>
