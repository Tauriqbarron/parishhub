<script lang="ts">
	import type { Gender, SacramentType } from '$lib/api';

	interface Filters {
		gender?: Gender;
		min_age?: number;
		max_age?: number;
		has_sacrament?: SacramentType;
		missing_sacrament?: SacramentType;
		is_deceased?: boolean;
		has_household?: boolean;
	}

	interface Props {
		filters: Filters;
		onFilterChange: (filters: Filters) => void;
	}

	let { filters, onFilterChange }: Props = $props();

	let isExpanded = $state(false);

	const genderOptions: { value: Gender | ''; label: string }[] = [
		{ value: '', label: 'All Genders' },
		{ value: 'male', label: 'Male' },
		{ value: 'female', label: 'Female' }
	];

	const deceasedOptions: { value: 'all' | 'living' | 'deceased'; label: string }[] = [
		{ value: 'all', label: 'All Statuses' },
		{ value: 'living', label: 'Living' },
		{ value: 'deceased', label: 'Deceased' }
	];

	const householdOptions: { value: 'all' | 'yes' | 'no'; label: string }[] = [
		{ value: 'all', label: 'All' },
		{ value: 'yes', label: 'In Household' },
		{ value: 'no', label: 'Individual' }
	];

	const sacramentOptions: { value: SacramentType | ''; label: string }[] = [
		{ value: '', label: 'Any' },
		{ value: 'baptism', label: 'Baptism' },
		{ value: 'first_communion', label: 'First Communion' },
		{ value: 'confirmation', label: 'Confirmation' },
		{ value: 'marriage', label: 'Marriage' },
		{ value: 'holy_orders', label: 'Holy Orders' }
	];

	let gender = $state<Gender | ''>('');
	let minAge = $state<number | undefined>(undefined);
	let maxAge = $state<number | undefined>(undefined);
	let hasSacrament = $state<SacramentType | ''>('');
	let missingSacrament = $state<SacramentType | ''>('');
	let statusFilter = $state<'all' | 'living' | 'deceased'>('all');
	let householdFilter = $state<'all' | 'yes' | 'no'>('all');

	$effect(() => {
		gender = filters.gender || '';
		minAge = filters.min_age;
		maxAge = filters.max_age;
		hasSacrament = filters.has_sacrament || '';
		missingSacrament = filters.missing_sacrament || '';
		statusFilter =
			filters.is_deceased === true ? 'deceased' : filters.is_deceased === false ? 'living' : 'all';
		householdFilter =
			filters.has_household === true ? 'yes' : filters.has_household === false ? 'no' : 'all';
	});

	function applyFilters() {
		onFilterChange({
			gender: gender || undefined,
			min_age: minAge,
			max_age: maxAge,
			has_sacrament: hasSacrament || undefined,
			missing_sacrament: missingSacrament || undefined,
			is_deceased:
				statusFilter === 'deceased' ? true : statusFilter === 'living' ? false : undefined,
			has_household: householdFilter === 'yes' ? true : householdFilter === 'no' ? false : undefined
		});
	}

	function clearFilters() {
		gender = '';
		minAge = undefined;
		maxAge = undefined;
		hasSacrament = '';
		missingSacrament = '';
		statusFilter = 'all';
		householdFilter = 'all';
		onFilterChange({});
	}

	const hasActiveFilters = $derived(
		gender ||
			minAge !== undefined ||
			maxAge !== undefined ||
			hasSacrament ||
			missingSacrament ||
			statusFilter !== 'all' ||
			householdFilter !== 'all'
	);
</script>

<div class="bg-white border border-brand-border rounded-lg">
	<button
		type="button"
		onclick={() => (isExpanded = !isExpanded)}
		class="w-full px-4 py-3 flex items-center justify-between text-left hover:bg-brand-bg-muted rounded-lg"
	>
		<div class="flex items-center gap-2">
			<svg
				class="h-5 w-5 text-brand-text-muted"
				fill="none"
				stroke="currentColor"
				viewBox="0 0 24 24"
			>
				<path
					stroke-linecap="round"
					stroke-linejoin="round"
					stroke-width="2"
					d="M3 4a1 1 0 011-1h16a1 1 0 011 1v2.586a1 1 0 01-.293.707l-6.414 6.414a1 1 0 00-.293.707V17l-4 4v-6.586a1 1 0 00-.293-.707L3.293 7.293A1 1 0 013 6.586V4z"
				/>
			</svg>
			<span class="font-medium text-brand-text-secondary">Filters</span>
			{#if hasActiveFilters}
				<span
					class="inline-flex items-center px-2 py-0.5 rounded text-xs font-medium bg-brand-accent/10 text-brand-accent"
				>
					Active
				</span>
			{/if}
		</div>
		<svg
			class="h-5 w-5 text-brand-text-muted transition-transform {isExpanded ? 'rotate-180' : ''}"
			fill="none"
			stroke="currentColor"
			viewBox="0 0 24 24"
		>
			<path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M19 9l-7 7-7-7" />
		</svg>
	</button>

	{#if isExpanded}
		<div class="px-4 pb-4 border-t border-brand-border pt-4">
			<div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
				<!-- Gender Filter -->
				<div>
					<label for="gender" class="block text-sm font-medium text-brand-text-secondary mb-1"
						>Gender</label
					>
					<select
						id="gender"
						bind:value={gender}
						onchange={applyFilters}
						class="block w-full rounded-sm border-brand-border shadow-sm focus:border-brand-accent focus:ring-brand-accent sm:text-sm"
					>
						{#each genderOptions as option (option.value)}
							<option value={option.value}>{option.label}</option>
						{/each}
					</select>
				</div>

				<!-- Status Filter -->
				<div>
					<label for="status" class="block text-sm font-medium text-brand-text-secondary mb-1"
						>Status</label
					>
					<select
						id="status"
						bind:value={statusFilter}
						onchange={applyFilters}
						class="block w-full rounded-sm border-brand-border shadow-sm focus:border-brand-accent focus:ring-brand-accent sm:text-sm"
					>
						{#each deceasedOptions as option (option.value)}
							<option value={option.value}>{option.label}</option>
						{/each}
					</select>
				</div>

				<!-- Age Range -->
				<fieldset>
					<legend class="block text-sm font-medium text-brand-text-secondary mb-1">Age Range</legend
					>
					<div class="flex items-center gap-2">
						<input
							type="number"
							bind:value={minAge}
							onchange={applyFilters}
							placeholder="Min"
							aria-label="Minimum age"
							min="0"
							max="150"
							class="block w-full rounded-sm border-brand-border shadow-sm focus:border-brand-accent focus:ring-brand-accent sm:text-sm"
						/>
						<span class="text-brand-text-muted">-</span>
						<input
							type="number"
							bind:value={maxAge}
							onchange={applyFilters}
							placeholder="Max"
							aria-label="Maximum age"
							min="0"
							max="150"
							class="block w-full rounded-sm border-brand-border shadow-sm focus:border-brand-accent focus:ring-brand-accent sm:text-sm"
						/>
					</div>
				</fieldset>

				<!-- Household Filter -->
				<div>
					<label for="household" class="block text-sm font-medium text-brand-text-secondary mb-1"
						>Household</label
					>
					<select
						id="household"
						bind:value={householdFilter}
						onchange={applyFilters}
						class="block w-full rounded-sm border-brand-border shadow-sm focus:border-brand-accent focus:ring-brand-accent sm:text-sm"
					>
						{#each householdOptions as option (option.value)}
							<option value={option.value}>{option.label}</option>
						{/each}
					</select>
				</div>

				<!-- Has Sacrament -->
				<div>
					<label
						for="hasSacrament"
						class="block text-sm font-medium text-brand-text-secondary mb-1"
					>
						Has Received
					</label>
					<select
						id="hasSacrament"
						bind:value={hasSacrament}
						onchange={applyFilters}
						class="block w-full rounded-sm border-brand-border shadow-sm focus:border-brand-accent focus:ring-brand-accent sm:text-sm"
					>
						{#each sacramentOptions as option (option.value)}
							<option value={option.value}>{option.label}</option>
						{/each}
					</select>
				</div>

				<!-- Missing Sacrament -->
				<div>
					<label
						for="missingSacrament"
						class="block text-sm font-medium text-brand-text-secondary mb-1"
					>
						Missing Sacrament
					</label>
					<select
						id="missingSacrament"
						bind:value={missingSacrament}
						onchange={applyFilters}
						class="block w-full rounded-sm border-brand-border shadow-sm focus:border-brand-accent focus:ring-brand-accent sm:text-sm"
					>
						{#each sacramentOptions as option (option.value)}
							<option value={option.value}>{option.label}</option>
						{/each}
					</select>
				</div>
			</div>

			{#if hasActiveFilters}
				<div class="mt-4 flex justify-end">
					<button
						type="button"
						onclick={clearFilters}
						class="px-3 py-1.5 text-sm text-brand-accent hover:text-amber-700 hover:bg-brand-bg-muted rounded-sm transition-colors"
					>
						Clear all filters
					</button>
				</div>
			{/if}
		</div>
	{/if}
</div>
