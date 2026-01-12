<script lang="ts">
	import type { Gender, SacramentType } from '$lib/api';

	interface Filters {
		gender?: Gender;
		min_age?: number;
		max_age?: number;
		has_sacrament?: SacramentType;
		missing_sacrament?: SacramentType;
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
		{ value: 'female', label: 'Female' },
		{ value: 'other', label: 'Other' }
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

	$effect(() => {
		gender = filters.gender || '';
		minAge = filters.min_age;
		maxAge = filters.max_age;
		hasSacrament = filters.has_sacrament || '';
		missingSacrament = filters.missing_sacrament || '';
	});

	function applyFilters() {
		onFilterChange({
			gender: gender || undefined,
			min_age: minAge,
			max_age: maxAge,
			has_sacrament: hasSacrament || undefined,
			missing_sacrament: missingSacrament || undefined
		});
	}

	function clearFilters() {
		gender = '';
		minAge = undefined;
		maxAge = undefined;
		hasSacrament = '';
		missingSacrament = '';
		onFilterChange({});
	}

	const hasActiveFilters = $derived(
		gender || minAge !== undefined || maxAge !== undefined || hasSacrament || missingSacrament
	);
</script>

<div class="bg-white border border-gray-200 rounded-lg">
	<button
		type="button"
		onclick={() => (isExpanded = !isExpanded)}
		class="w-full px-4 py-3 flex items-center justify-between text-left hover:bg-gray-50 rounded-lg"
	>
		<div class="flex items-center gap-2">
			<svg class="h-5 w-5 text-gray-500" fill="none" stroke="currentColor" viewBox="0 0 24 24">
				<path
					stroke-linecap="round"
					stroke-linejoin="round"
					stroke-width="2"
					d="M3 4a1 1 0 011-1h16a1 1 0 011 1v2.586a1 1 0 01-.293.707l-6.414 6.414a1 1 0 00-.293.707V17l-4 4v-6.586a1 1 0 00-.293-.707L3.293 7.293A1 1 0 013 6.586V4z"
				/>
			</svg>
			<span class="font-medium text-gray-700">Filters</span>
			{#if hasActiveFilters}
				<span
					class="inline-flex items-center px-2 py-0.5 rounded text-xs font-medium bg-blue-100 text-blue-800"
				>
					Active
				</span>
			{/if}
		</div>
		<svg
			class="h-5 w-5 text-gray-400 transition-transform {isExpanded ? 'rotate-180' : ''}"
			fill="none"
			stroke="currentColor"
			viewBox="0 0 24 24"
		>
			<path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M19 9l-7 7-7-7" />
		</svg>
	</button>

	{#if isExpanded}
		<div class="px-4 pb-4 border-t border-gray-200 pt-4">
			<div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
				<!-- Gender Filter -->
				<div>
					<label for="gender" class="block text-sm font-medium text-gray-700 mb-1">Gender</label>
					<select
						id="gender"
						bind:value={gender}
						onchange={applyFilters}
						class="block w-full rounded-md border-gray-300 shadow-sm focus:border-blue-500 focus:ring-blue-500 sm:text-sm"
					>
						{#each genderOptions as option (option.value)}
							<option value={option.value}>{option.label}</option>
						{/each}
					</select>
				</div>

				<!-- Age Range -->
				<fieldset>
					<legend class="block text-sm font-medium text-gray-700 mb-1">Age Range</legend>
					<div class="flex items-center gap-2">
						<input
							type="number"
							bind:value={minAge}
							onchange={applyFilters}
							placeholder="Min"
							aria-label="Minimum age"
							min="0"
							max="150"
							class="block w-full rounded-md border-gray-300 shadow-sm focus:border-blue-500 focus:ring-blue-500 sm:text-sm"
						/>
						<span class="text-gray-500">-</span>
						<input
							type="number"
							bind:value={maxAge}
							onchange={applyFilters}
							placeholder="Max"
							aria-label="Maximum age"
							min="0"
							max="150"
							class="block w-full rounded-md border-gray-300 shadow-sm focus:border-blue-500 focus:ring-blue-500 sm:text-sm"
						/>
					</div>
				</fieldset>

				<!-- Has Sacrament -->
				<div>
					<label for="hasSacrament" class="block text-sm font-medium text-gray-700 mb-1">
						Has Received
					</label>
					<select
						id="hasSacrament"
						bind:value={hasSacrament}
						onchange={applyFilters}
						class="block w-full rounded-md border-gray-300 shadow-sm focus:border-blue-500 focus:ring-blue-500 sm:text-sm"
					>
						{#each sacramentOptions as option (option.value)}
							<option value={option.value}>{option.label}</option>
						{/each}
					</select>
				</div>

				<!-- Missing Sacrament -->
				<div>
					<label for="missingSacrament" class="block text-sm font-medium text-gray-700 mb-1">
						Missing Sacrament
					</label>
					<select
						id="missingSacrament"
						bind:value={missingSacrament}
						onchange={applyFilters}
						class="block w-full rounded-md border-gray-300 shadow-sm focus:border-blue-500 focus:ring-blue-500 sm:text-sm"
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
						class="px-3 py-1.5 text-sm text-gray-600 hover:text-gray-900 hover:bg-gray-100 rounded-md transition-colors"
					>
						Clear all filters
					</button>
				</div>
			{/if}
		</div>
	{/if}
</div>
