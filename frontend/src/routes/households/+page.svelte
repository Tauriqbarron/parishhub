<script lang="ts">
	import { goto } from '$app/navigation';
	import { householdsStore } from '$lib/stores/households';
	import type { Household, HouseholdFilters, HouseholdWithMembers } from '$lib/api';
	import SearchInput from '$lib/components/SearchInput.svelte';
	import HouseholdTable from '$lib/components/HouseholdTable.svelte';
	import Pagination from '$lib/components/Pagination.svelte';
	import CreateHouseholdModal from '$lib/components/CreateHouseholdModal.svelte';

	let searchValue = $state('');
	let showCreateModal = $state(false);

	$effect(() => {
		householdsStore.load();
	});

	function handleSearch(value: string) {
		searchValue = value;
		householdsStore.setFilters({ search: value || undefined });
	}

	function handleSort(field: HouseholdFilters['sort_by'], order: HouseholdFilters['sort_order']) {
		householdsStore.setSort(field, order);
	}

	function handlePageChange(page: number) {
		householdsStore.setPage(page);
	}

	function handleRowClick(household: Household) {
		goto(`/households/${household.id}`);
	}

	function handleEdit(household: Household) {
		goto(`/households/${household.id}`);
	}

	function handleHouseholdCreated(household: HouseholdWithMembers) {
		showCreateModal = false;
		householdsStore.load();
		goto(`/households/${household.id}`);
	}
</script>

<div>
	<div class="mb-6 flex flex-col sm:flex-row sm:items-center sm:justify-between gap-4">
		<div>
			<h1 class="text-2xl font-bold text-brand-primary">Households</h1>
			<p class="text-brand-text-secondary mt-1">Manage parish households and their members</p>
		</div>
		<button
			onclick={() => (showCreateModal = true)}
			class="inline-flex items-center justify-center px-4 py-2 border border-transparent text-sm font-medium rounded-md shadow-sm text-white bg-brand-accent hover:bg-brand-accent/90 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-brand-accent"
		>
			<svg class="w-5 h-5 mr-2 -ml-1" fill="none" stroke="currentColor" viewBox="0 0 24 24">
				<path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 4v16m8-8H4" />
			</svg>
			New Household
		</button>
	</div>

	<!-- Search -->
	<div class="mb-6">
		<SearchInput
			value={searchValue}
			placeholder="Search by household name..."
			onSearch={handleSearch}
		/>
	</div>

	<!-- Results -->
	<div class="bg-white shadow rounded-lg overflow-hidden">
		{#if $householdsStore.loading}
			<!-- Loading Skeleton -->
			<div class="animate-pulse">
				<div class="px-6 py-4 border-b border-brand-border">
					<div class="h-4 bg-brand-bg-muted rounded w-1/4"></div>
				</div>
				{#each Array.from({ length: 5 }, (_, i) => i) as i (i)}
					<div class="px-6 py-4 border-b border-brand-border">
						<div class="flex items-center space-x-4">
							<div class="h-10 w-10 bg-brand-bg-muted rounded-lg"></div>
							<div class="h-4 bg-brand-bg-muted rounded w-1/4"></div>
							<div class="h-4 bg-brand-bg-muted rounded w-1/3"></div>
							<div class="h-4 bg-brand-bg-muted rounded w-16"></div>
						</div>
					</div>
				{/each}
			</div>
		{:else if $householdsStore.error}
			<!-- Error State -->
			<div class="p-6 text-center">
				<svg
					class="mx-auto h-12 w-12 text-brand-error"
					fill="none"
					stroke="currentColor"
					viewBox="0 0 24 24"
				>
					<path
						stroke-linecap="round"
						stroke-linejoin="round"
						stroke-width="2"
						d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-3L13.732 4c-.77-1.333-2.694-1.333-3.464 0L3.34 16c-.77 1.333.192 3 1.732 3z"
					/>
				</svg>
				<h3 class="mt-2 text-sm font-medium text-brand-primary">Error loading households</h3>
				<p class="mt-1 text-sm text-brand-text-secondary">{$householdsStore.error}</p>
				<div class="mt-6">
					<button
						onclick={() => householdsStore.load($householdsStore.filters)}
						class="inline-flex items-center px-4 py-2 border border-transparent text-sm font-medium rounded-md shadow-sm text-white bg-brand-accent hover:bg-brand-accent/90"
					>
						Try again
					</button>
				</div>
			</div>
		{:else if $householdsStore.households.length === 0}
			<!-- Empty State -->
			<div class="p-6 text-center">
				<svg
					class="mx-auto h-12 w-12 text-brand-text-muted"
					fill="none"
					stroke="currentColor"
					viewBox="0 0 24 24"
				>
					<path
						stroke-linecap="round"
						stroke-linejoin="round"
						stroke-width="2"
						d="M3 12l2-2m0 0l7-7 7 7M5 10v10a1 1 0 001 1h3m10-11l2 2m-2-2v10a1 1 0 01-1 1h-3m-6 0a1 1 0 001-1v-4a1 1 0 011-1h2a1 1 0 011 1v4a1 1 0 001 1m-6 0h6"
					/>
				</svg>
				<h3 class="mt-2 text-sm font-medium text-brand-primary">No households found</h3>
				<p class="mt-1 text-sm text-brand-text-secondary">
					{#if searchValue}
						No households match your search criteria. Try a different search term.
					{:else}
						Get started by creating a new household.
					{/if}
				</p>
				{#if !searchValue}
					<div class="mt-6">
						<button
							onclick={() => (showCreateModal = true)}
							class="inline-flex items-center px-4 py-2 border border-transparent text-sm font-medium rounded-md shadow-sm text-white bg-brand-accent hover:bg-brand-accent/90"
						>
							<svg class="w-5 h-5 mr-2 -ml-1" fill="none" stroke="currentColor" viewBox="0 0 24 24">
								<path
									stroke-linecap="round"
									stroke-linejoin="round"
									stroke-width="2"
									d="M12 4v16m8-8H4"
								/>
							</svg>
							New Household
						</button>
					</div>
				{/if}
			</div>
		{:else}
			<!-- Table -->
			<HouseholdTable
				households={$householdsStore.households}
				sortBy={$householdsStore.filters.sort_by || 'name'}
				sortOrder={$householdsStore.filters.sort_order || 'asc'}
				onSort={handleSort}
				onRowClick={handleRowClick}
				onEdit={handleEdit}
			/>

			<!-- Pagination -->
			<Pagination
				page={$householdsStore.page}
				pages={$householdsStore.pages}
				total={$householdsStore.total}
				perPage={$householdsStore.perPage}
				onPageChange={handlePageChange}
			/>
		{/if}
	</div>
</div>

{#if showCreateModal}
	<CreateHouseholdModal onSave={handleHouseholdCreated} onClose={() => (showCreateModal = false)} />
{/if}
