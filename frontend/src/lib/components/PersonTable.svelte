<script lang="ts">
	import type { PersonWithRelations } from '$lib/api';
	import SacramentBadges from './SacramentBadges.svelte';

	import type { PersonFilters } from '$lib/api';

	type SortField = NonNullable<PersonFilters['sort_by']>;
	type SortOrder = 'asc' | 'desc';

	interface Props {
		persons: PersonWithRelations[];
		sortBy: SortField;
		sortOrder: SortOrder;
		onSort: (field: SortField, order: SortOrder) => void;
		onRowClick: (person: PersonWithRelations) => void;
		onEdit: (person: PersonWithRelations) => void;
	}

	let { persons, sortBy, sortOrder, onSort, onRowClick, onEdit }: Props = $props();

	function handleSort(field: SortField) {
		if (sortBy === field) {
			onSort(field, sortOrder === 'asc' ? 'desc' : 'asc');
		} else {
			onSort(field, 'asc');
		}
	}

	function calculateAge(dateOfBirth: string | null): number | null {
		if (!dateOfBirth) return null;
		const today = new Date();
		const birthDate = new Date(dateOfBirth);
		let age = today.getFullYear() - birthDate.getFullYear();
		const monthDiff = today.getMonth() - birthDate.getMonth();
		if (monthDiff < 0 || (monthDiff === 0 && today.getDate() < birthDate.getDate())) {
			age--;
		}
		return age;
	}

	function formatGender(gender: string | null): string {
		if (!gender) return '-';
		return gender.charAt(0).toUpperCase();
	}

	function formatName(person: PersonWithRelations): string {
		return `${person.last_name}, ${person.first_name}`;
	}
</script>

<div class="overflow-x-auto" role="region" aria-label="People list">
	<table class="min-w-full divide-y divide-gray-200" aria-label="People table">
		<thead class="bg-gray-50">
			<tr>
				<th
					scope="col"
					class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider"
				>
					<button
						onclick={() => handleSort('last_name')}
						class="group inline-flex items-center gap-1 hover:text-gray-700"
					>
						Name
						<span
							class="flex-none rounded {sortBy === 'last_name'
								? 'text-gray-900'
								: 'text-gray-400 group-hover:text-gray-500'}"
						>
							{#if sortBy === 'last_name'}
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
					<button
						onclick={() => handleSort('date_of_birth')}
						class="group inline-flex items-center gap-1 hover:text-gray-700"
					>
						Age
						<span
							class="flex-none rounded {sortBy === 'date_of_birth'
								? 'text-gray-900'
								: 'text-gray-400 group-hover:text-gray-500'}"
						>
							{#if sortBy === 'date_of_birth'}
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
					Gender
				</th>
				<th
					scope="col"
					class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider"
				>
					<button
						onclick={() => handleSort('email')}
						class="group inline-flex items-center gap-1 hover:text-gray-700"
					>
						Contact
						<span
							class="flex-none rounded {sortBy === 'email'
								? 'text-gray-900'
								: 'text-gray-400 group-hover:text-gray-500'}"
						>
							{#if sortBy === 'email'}
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
					Sacraments
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
			{#each persons as person (person.id)}
				<tr
					onclick={() => onRowClick(person)}
					onkeydown={(e) => {
						if (e.key === 'Enter' || e.key === ' ') {
							e.preventDefault();
							onRowClick(person);
						}
					}}
					tabindex="0"
					role="button"
					aria-label="View details for {formatName(person)}"
					class="hover:bg-gray-50 cursor-pointer transition-colors"
				>
					<td class="px-6 py-4 whitespace-nowrap">
						<div class="flex items-center">
							<div class="text-sm font-medium text-gray-900">{formatName(person)}</div>
							{#if person.death}
								<span class="ml-2 inline-flex items-center text-red-600" title="Deceased">
									<svg class="w-4 h-4" fill="currentColor" viewBox="0 0 24 24" aria-hidden="true">
										<path
											d="M12 2C6.48 2 2 6.48 2 12s4.48 10 10 10 10-4.48 10-10S17.52 2 12 2zm0 18c-4.41 0-8-3.59-8-8s3.59-8 8-8 8 3.59 8 8-3.59 8-8 8zm-1-13h2v6h-2zm0 8h2v2h-2z"
										/>
									</svg>
								</span>
							{/if}
						</div>
					</td>
					<td class="px-6 py-4 whitespace-nowrap">
						<div class="text-sm text-gray-900">{calculateAge(person.date_of_birth) ?? '-'}</div>
					</td>
					<td class="px-6 py-4 whitespace-nowrap">
						<div class="text-sm text-gray-900">{formatGender(person.gender)}</div>
					</td>
					<td class="px-6 py-4 whitespace-nowrap">
						<div class="text-sm text-gray-900">{person.email || '-'}</div>
					</td>
					<td class="px-6 py-4 whitespace-nowrap">
						<SacramentBadges sacraments={person.sacraments} />
					</td>
					<td class="px-6 py-4 whitespace-nowrap text-right text-sm font-medium">
						<button
							onclick={(e) => {
								e.stopPropagation();
								onRowClick(person);
							}}
							class="text-gray-400 hover:text-gray-600 mr-3"
							aria-label="View {formatName(person)}"
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
								onEdit(person);
							}}
							class="text-blue-400 hover:text-blue-600"
							aria-label="Edit {formatName(person)}"
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
