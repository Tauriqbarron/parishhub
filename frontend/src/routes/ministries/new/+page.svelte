<script lang="ts">
	import { goto } from '$app/navigation';
	import { ArrowLeft } from 'lucide-svelte';
	import { ministryApi, type MinistryCreate } from '$lib/api';
	import { toasts } from '$lib/stores/toast';
	import Breadcrumbs from '$lib/components/Breadcrumbs.svelte';
	import PageHeader from '$lib/components/PageHeader.svelte';

	let name = $state('');
	let description = $state('');
	let isActive = $state(true);
	let saving = $state(false);
	let error = $state<string | null>(null);

	async function handleSubmit(e: SubmitEvent) {
		e.preventDefault();
		if (!name.trim()) {
			error = 'Ministry name is required.';
			return;
		}

		saving = true;
		error = null;

		try {
			const data: MinistryCreate = {
				name: name.trim(),
				description: description.trim() || null,
				is_active: isActive
			};
			const ministry = await ministryApi.create(data);
			toasts.success(`Ministry "${ministry.name}" created.`);
			goto(`/ministries/${ministry.id}`);
		} catch (err) {
			error = err instanceof Error ? err.message : 'Failed to create ministry.';
		} finally {
			saving = false;
		}
	}
</script>

<div>
	<Breadcrumbs />
	<PageHeader title="New Ministry" subtitle="Create a new church ministry" />

	<div class="bg-white rounded-lg border border-brand-border p-6">
		{#if error}
			<div class="mb-4 p-3 rounded bg-red-50 text-red-700 text-sm">
				{error}
			</div>
		{/if}

		<form onsubmit={handleSubmit} class="space-y-6">
			<div>
				<label for="name" class="block text-sm font-medium text-brand-primary">
					Name <span class="text-brand-error">*</span>
				</label>
				<input
					id="name"
					type="text"
					bind:value={name}
					required
					maxlength={200}
					class="mt-1 block w-full rounded-sm border border-brand-border px-3 py-2 text-sm focus:border-brand-accent focus:ring-1 focus:ring-brand-accent outline-none"
					placeholder="e.g. Choir, Youth Group, Bible Study"
				/>
			</div>

			<div>
				<label for="description" class="block text-sm font-medium text-brand-primary">
					Description
				</label>
				<textarea
					id="description"
					bind:value={description}
					rows={4}
					maxlength={5000}
					class="mt-1 block w-full rounded-sm border border-brand-border px-3 py-2 text-sm focus:border-brand-accent focus:ring-1 focus:ring-brand-accent outline-none resize-y"
					placeholder="What does this ministry do?"
				></textarea>
			</div>

			<div class="flex items-center gap-2">
				<input
					id="is_active"
					type="checkbox"
					bind:checked={isActive}
					class="rounded border-brand-border text-brand-accent focus:ring-brand-accent"
				/>
				<label for="is_active" class="text-sm text-brand-primary"> Active </label>
			</div>

			<div class="flex items-center gap-3 pt-4 border-t border-brand-border">
				<button
					type="submit"
					disabled={saving}
					class="inline-flex items-center px-4 py-2 text-sm font-medium rounded-sm text-white bg-brand-accent hover:opacity-90 disabled:opacity-50"
				>
					{saving ? 'Creating...' : 'Create Ministry'}
				</button>
				<a
					href="/ministries"
					class="inline-flex items-center gap-1 px-4 py-2 text-sm font-medium rounded-sm text-brand-text-secondary hover:text-brand-primary"
				>
					<ArrowLeft class="w-4 h-4" />
					Cancel
				</a>
			</div>
		</form>
	</div>
</div>
