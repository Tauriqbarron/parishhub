<script lang="ts">
	import { goto } from '$app/navigation';
	import { peopleStore } from '$lib/stores/people';
	import type { Gender, SacramentType, PersonWithRelations, PersonFilters } from '$lib/api';
	import SearchInput from '$lib/components/SearchInput.svelte';
	import FilterPanel from '$lib/components/FilterPanel.svelte';
	import PersonTable from '$lib/components/PersonTable.svelte';
	import Pagination from '$lib/components/Pagination.svelte';

	interface Filters {
		gender?: Gender;
		min_age?: number;
		max_age?: number;
		has_sacrament?: SacramentType;
		missing_sacrament?: SacramentType;
	}

	let searchValue = $state('');

	$effect(() => {
		peopleStore.load();
	});

	function handleSearch(value: string) {
		searchValue = value;
		peopleStore.setFilters({ search: value || undefined });
	}

	function handleFilterChange(filters: Filters) {
		peopleStore.setFilters(filters);
	}

	function handleSort(field: PersonFilters['sort_by'], order: PersonFilters['sort_order']) {
		peopleStore.setSort(field, order);
	}

	function handlePageChange(page: number) {
		peopleStore.setPage(page);
	}

	function handleRowClick(person: PersonWithRelations) {
		goto(`/people/${person.id}`);
	}

	function handleEdit(person: PersonWithRelations) {
		goto(`/people/${person.id}/edit`);
	}
</script>

<div>
	<div class="mb-6 flex flex-col sm:flex-row sm:items-center sm:justify-between gap-4">
		<div>
			<h1 class="text-2xl font-bold text-brand-primary">People</h1>
			<p class="text-brand-text-secondary mt-1">Manage parishioners and their records</p>
		</div>
		<a
			href="/people/new"
			class="inline-flex items-center justify-center px-4 py-2 border border-transparent text-sm font-medium rounded-md shadow-sm text-white bg-brand-accent hover:bg-brand-accent/90 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-brand-accent"
		>
			<svg class="w-5 h-5 mr-2 -ml-1" fill="none" stroke="currentColor" viewBox="0 0 24 24">
				<path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 4v16m8-8H4" />
			</svg>
			Add Person
		</a>
	</div>

	<!-- Search and Filters -->
	<div class="space-y-4 mb-6">
		<SearchInput
			value={searchValue}
			placeholder="Search by name or email..."
			onSearch={handleSearch}
		/>
		<FilterPanel
			filters={{
				gender: $peopleStore.filters.gender,
				min_age: $peopleStore.filters.min_age,
				max_age: $peopleStore.filters.max_age,
				has_sacrament: $peopleStore.filters.has_sacrament,
				missing_sacrament: $peopleStore.filters.missing_sacrament
			}}
			onFilterChange={handleFilterChange}
		/>
	</div>

	<!-- Results -->
	<div class="bg-white shadow rounded-lg overflow-hidden">
		{#if $peopleStore.loading}
			<!-- Loading Skeleton -->
			<div class="animate-pulse">
				<div class="px-6 py-4 border-b border-brand-border">
					<div class="h-4 bg-brand-bg-muted rounded w-1/4"></div>
				</div>
				{#each Array.from({ length: 5 }, (_, i) => i) as i (i)}
					<div class="px-6 py-4 border-b border-brand-border">
						<div class="flex items-center space-x-4">
							<div class="h-4 bg-brand-bg-muted rounded w-1/4"></div>
							<div class="h-4 bg-brand-bg-muted rounded w-16"></div>
							<div class="h-4 bg-brand-bg-muted rounded w-12"></div>
							<div class="h-4 bg-brand-bg-muted rounded w-1/3"></div>
							<div class="h-4 bg-brand-bg-muted rounded w-20"></div>
						</div>
					</div>
				{/each}
			</div>
		{:else if $peopleStore.error}
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
				<h3 class="mt-2 text-sm font-medium text-brand-primary">Error loading people</h3>
				<p class="mt-1 text-sm text-brand-text-secondary">{$peopleStore.error}</p>
				<div class="mt-6">
					<button
						onclick={() => peopleStore.load($peopleStore.filters)}
						class="inline-flex items-center px-4 py-2 border border-transparent text-sm font-medium rounded-md shadow-sm text-white bg-brand-accent hover:bg-brand-accent/90"
					>
						Try again
					</button>
				</div>
			</div>
		{:else if $peopleStore.persons.length === 0}
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
						d="M17 20h5v-2a3 3 0 00-5.356-1.857M17 20H7m10 0v-2c0-.656-.126-1.283-.356-1.857M7 20H2v-2a3 3 0 015.356-1.857M7 20v-2c0-.656.126-1.283.356-1.857m0 0a5.002 5.002 0 019.288 0M15 7a3 3 0 11-6 0 3 3 0 016 0zm6 3a2 2 0 11-4 0 2 2 0 014 0zM7 10a2 2 0 11-4 0 2 2 0 014 0z"
					/>
				</svg>
				<h3 class="mt-2 text-sm font-medium text-brand-primary">No people found</h3>
				<p class="mt-1 text-sm text-brand-text-secondary">
					{#if searchValue || Object.values($peopleStore.filters).some((v) => v !== undefined && v !== '')}
						No people match your search criteria. Try adjusting your filters.
					{:else}
						Get started by adding a new person.
					{/if}
				</p>
				{#if !searchValue && !Object.values($peopleStore.filters).some((v) => v !== undefined && v !== '')}
					<div class="mt-6">
						<a
							href="/people/new"
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
							Add Person
						</a>
					</div>
				{/if}
			</div>
		{:else}
			<!-- Table -->
			<PersonTable
				persons={$peopleStore.persons}
				sortBy={$peopleStore.filters.sort_by || 'last_name'}
				sortOrder={$peopleStore.filters.sort_order || 'asc'}
				onSort={handleSort}
				onRowClick={handleRowClick}
				onEdit={handleEdit}
			/>

			<!-- Pagination -->
			<Pagination
				page={$peopleStore.page}
				pages={$peopleStore.pages}
				total={$peopleStore.total}
				perPage={$peopleStore.perPage}
				onPageChange={handlePageChange}
			/>
		{/if}
	</div>
</div>
