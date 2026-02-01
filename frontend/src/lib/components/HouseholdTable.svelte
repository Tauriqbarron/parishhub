<script lang="ts">
	import type { Household, HouseholdFilters } from '$lib/api';

	type SortField = NonNullable<HouseholdFilters['sort_by']>;
	type SortOrder = 'asc' | 'desc';

	interface Props {
		households: Household[];
		sortBy: SortField;
		sortOrder: SortOrder;
		onSort: (field: SortField, order: SortOrder) => void;
		onRowClick: (household: Household) => void;
		onEdit: (household: Household) => void;
	}

	let { households, sortBy, sortOrder, onSort, onRowClick, onEdit }: Props = $props();

	function handleSort(field: SortField) {
		if (sortBy === field) {
			onSort(field, sortOrder === 'asc' ? 'desc' : 'asc');
		} else {
			onSort(field, 'asc');
		}
	}

	function formatAddress(household: Household): string {
		const parts = [household.address_line1, household.city, household.postal_code].filter(Boolean);
		return parts.join(', ') || '-';
	}
</script>

<div class="overflow-x-auto" role="region" aria-label="Households list">
	<table class="min-w-full divide-y divide-gray-200" aria-label="Households table">
		<thead class="bg-gray-50">
			<tr>
				<th
					scope="col"
					class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider"
				>
					<button
						onclick={() => handleSort('name')}
						class="group inline-flex items-center gap-1 hover:text-gray-700"
					>
						Name
						<span
							class="flex-none rounded {sortBy === 'name'
								? 'text-gray-900'
								: 'text-gray-400 group-hover:text-gray-500'}"
						>
							{#if sortBy === 'name'}
								{#if sortOrder === 'asc'}
									<svg class="h-4 w-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
										<path
											stroke-linecap="round"
											stroke-linejoin="round"
											stroke-width="2"
											d="M5 15l7-7 7 7"
										/>
									</svg>
								{:else}
									<svg class="h-4 w-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
										<path
											stroke-linecap="round"
											stroke-linejoin="round"
											stroke-width="2"
											d="M19 9l-7 7-7-7"
										/>
									</svg>
								{/if}
							{:else}
								<svg class="h-4 w-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
									<path
										stroke-linecap="round"
										stroke-linejoin="round"
										stroke-width="2"
										d="M7 16V4m0 0L3 8m4-4l4 4m6 0v12m0 0l4-4m-4 4l-4-4"
									/>
								</svg>
							{/if}
						</span>
					</button>
				</th>
				<th
					scope="col"
					class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider"
				>
					Address
				</th>
				<th
					scope="col"
					class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider"
				>
					Members
				</th>
				<th
					scope="col"
					class="px-6 py-3 text-right text-xs font-medium text-gray-500 uppercase tracking-wider"
				>
					Actions
				</th>
			</tr>
		</thead>
		<tbody class="bg-white divide-y divide-gray-200">
			{#each households as household (household.id)}
				<tr
					onclick={() => onRowClick(household)}
					onkeydown={(e) => {
						if (e.key === 'Enter' || e.key === ' ') {
							e.preventDefault();
							onRowClick(household);
						}
					}}
					tabindex="0"
					role="button"
					aria-label="View details for {household.name}"
					class="hover:bg-gray-50 cursor-pointer transition-colors"
				>
					<td class="px-6 py-4 whitespace-nowrap">
						<div class="flex items-center">
							<div class="p-2 bg-blue-50 rounded-lg mr-3">
								<svg
									class="w-5 h-5 text-blue-600"
									fill="none"
									stroke="currentColor"
									viewBox="0 0 24 24"
									aria-hidden="true"
									role="img"
								>
									<path
										stroke-linecap="round"
										stroke-linejoin="round"
										stroke-width="2"
										d="M3 12l2-2m0 0l7-7 7 7M5 10v10a1 1 0 001 1h3m10-11l2 2m-2-2v10a1 1 0 01-1 1h-3m-6 0a1 1 0 001-1v-4a1 1 0 011-1h2a1 1 0 011 1v4a1 1 0 001 1m-6 0h6"
									/>
								</svg>
							</div>
							<div class="text-sm font-medium text-gray-900">{household.name}</div>
						</div>
					</td>
					<td class="px-6 py-4 whitespace-nowrap">
						<div class="text-sm text-gray-900">{formatAddress(household)}</div>
					</td>
					<td class="px-6 py-4 whitespace-nowrap">
						<span
							class="inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium bg-gray-100 text-gray-800"
						>
							{household.member_count}
							{household.member_count === 1 ? 'member' : 'members'}
						</span>
					</td>
					<td class="px-6 py-4 whitespace-nowrap text-right text-sm font-medium">
						<button
							onclick={(e) => {
								e.stopPropagation();
								onRowClick(household);
							}}
							class="text-gray-400 hover:text-gray-600 mr-3"
							aria-label="View {household.name}"
						>
							<svg
								class="h-5 w-5"
								fill="none"
								stroke="currentColor"
								viewBox="0 0 24 24"
								aria-hidden="true"
								role="img"
							>
								<path
									stroke-linecap="round"
									stroke-linejoin="round"
									stroke-width="2"
									d="M15 12a3 3 0 11-6 0 3 3 0 016 0z"
								/>
								<path
									stroke-linecap="round"
									stroke-linejoin="round"
									stroke-width="2"
									d="M2.458 12C3.732 7.943 7.523 5 12 5c4.478 0 8.268 2.943 9.542 7-1.274 4.057-5.064 7-9.542 7-4.477 0-8.268-2.943-9.542-7z"
								/>
							</svg>
						</button>
						<button
							onclick={(e) => {
								e.stopPropagation();
								onEdit(household);
							}}
							class="text-blue-400 hover:text-blue-600"
							aria-label="Edit {household.name}"
						>
							<svg
								class="h-5 w-5"
								fill="none"
								stroke="currentColor"
								viewBox="0 0 24 24"
								aria-hidden="true"
								role="img"
							>
								<path
									stroke-linecap="round"
									stroke-linejoin="round"
									stroke-width="2"
									d="M11 5H6a2 2 0 00-2 2v11a2 2 0 002 2h11a2 2 0 002-2v-5m-1.414-9.414a2 2 0 112.828 2.828L11.828 15H9v-2.828l8.586-8.586z"
								/>
							</svg>
						</button>
					</td>
				</tr>
			{/each}
		</tbody>
	</table>
</div>
