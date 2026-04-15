<script lang="ts">
	import { goto } from '$app/navigation';
	import { Plus, Users, Search } from 'lucide-svelte';
	import { ministriesStore } from '$lib/stores/ministries';
	import type { Ministry } from '$lib/api';
	import SearchInput from '$lib/components/SearchInput.svelte';
	import Pagination from '$lib/components/Pagination.svelte';
	import Breadcrumbs from '$lib/components/Breadcrumbs.svelte';
	import PageHeader from '$lib/components/PageHeader.svelte';

	let searchValue = $state('');

	$effect(() => {
		ministriesStore.load();
	});

	function handleSearch(value: string) {
		searchValue = value;
		ministriesStore.setFilters({ search: value || undefined });
	}

	function handlePageChange(page: number) {
		ministriesStore.setPage(page);
	}

	function handleRowClick(ministry: Ministry) {
		goto(`/ministries/${ministry.id}`);
	}
</script>

<div>
	<Breadcrumbs />
	<PageHeader title="Ministries" subtitle="Manage church ministries and assign leaders">
		{#snippet actions()}
			<a
				href="/ministries/new"
				class="inline-flex items-center gap-2 px-4 py-2 text-sm font-medium rounded-sm text-white bg-brand-accent hover:opacity-90 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-brand-accent"
			>
				<Plus class="w-4 h-4" />
				New Ministry
			</a>
		{/snippet}
	</PageHeader>

	<div class="space-y-4 mb-6">
		<SearchInput
			value={searchValue}
			placeholder="Search ministries..."
			onSearch={handleSearch}
		/>
	</div>

	<div class="bg-white rounded-lg border border-brand-border overflow-hidden">
		{#if $ministriesStore.loading}
			<div class="animate-pulse">
				{#each [1, 2, 3] as i}
					<div class="px-6 py-4 border-b border-brand-border">
						<div class="flex items-center space-x-4">
							<div class="h-4 bg-brand-bg-muted rounded w-1/3"></div>
							<div class="h-4 bg-brand-bg-muted rounded w-20"></div>
						</div>
					</div>
				{/each}
			</div>
		{:else if $ministriesStore.error}
			<div class="p-6 text-center">
				<h3 class="text-sm font-medium text-brand-primary">Error loading ministries</h3>
				<p class="mt-1 text-sm text-brand-text-secondary">{$ministriesStore.error}</p>
				<button
					onclick={() => ministriesStore.load($ministriesStore.filters)}
					class="mt-4 inline-flex items-center px-4 py-2 text-sm font-medium rounded-sm text-white bg-brand-accent hover:opacity-90"
				>
					Try again
				</button>
			</div>
		{:else if $ministriesStore.ministries.length === 0}
			<div class="p-6 text-center">
				<Users class="mx-auto h-12 w-12 text-brand-text-muted" />
				<h3 class="mt-2 text-sm font-medium text-brand-primary">No ministries</h3>
				<p class="mt-1 text-sm text-brand-text-secondary">
					{searchValue ? 'No ministries match your search.' : 'Create your first ministry to get started.'}
				</p>
				{#if !searchValue}
					<div class="mt-6">
						<a
							href="/ministries/new"
							class="inline-flex items-center gap-2 px-4 py-2 text-sm font-medium rounded-sm text-white bg-brand-accent hover:opacity-90"
						>
							<Plus class="w-4 h-4" />
							New Ministry
						</a>
					</div>
				{/if}
			</div>
		{:else}
			<div class="divide-y divide-brand-border">
				{#each $ministriesStore.ministries as ministry (ministry.id)}
					<button
						class="w-full text-left px-6 py-4 hover:bg-brand-bg-muted/50 transition-colors cursor-pointer"
						onclick={() => handleRowClick(ministry)}
					>
						<div class="flex items-center justify-between">
							<div class="min-w-0 flex-1">
								<div class="flex items-center gap-2">
									<h3 class="text-sm font-medium text-brand-primary truncate">{ministry.name}</h3>
									{#if !ministry.is_active}
										<span class="inline-flex items-center px-2 py-0.5 rounded text-xs font-medium bg-brand-bg-muted text-brand-text-secondary">Inactive</span>
									{/if}
								</div>
								{#if ministry.description}
									<p class="mt-0.5 text-sm text-brand-text-secondary truncate">{ministry.description}</p>
								{/if}
							</div>
							<div class="flex items-center gap-4 ml-4 text-sm text-brand-text-secondary">
								<span class="flex items-center gap-1">
									<Users class="w-4 h-4" /> {ministry.member_count}
								</span>
							</div>
						</div>
					</button>
				{/each}
			</div>

			<Pagination
				page={$ministriesStore.page}
				pages={$ministriesStore.pages}
				total={$ministriesStore.total}
				perPage={$ministriesStore.perPage}
				onPageChange={handlePageChange}
			/>
		{/if}
	</div>
</div>
