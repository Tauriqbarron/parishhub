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

	function hasPersonAddress(person: PersonWithRelations): boolean {
		return !!(person.address_line1 || person.city || person.postal_code);
	}

	function getHouseholdAddress(person: PersonWithRelations): {
		address: string;
		householdName: string;
	} | null {
		const membership =
			person.household_memberships?.find((m) => m.is_primary_household && m.household) ??
			person.household_memberships?.[0];
		if (!membership?.household) return null;
		const h = membership.household;
		const parts = [h.address_line1, h.address_line2, h.city, h.postal_code].filter(Boolean);
		if (parts.length === 0) return null;
		return { address: parts.join(', '), householdName: h.name };
	}

	function getDisplayAddress(person: PersonWithRelations): {
		address: string;
		fromHousehold: boolean;
		householdName?: string;
	} {
		if (hasPersonAddress(person)) {
			const parts = [
				person.address_line1,
				person.address_line2,
				person.city,
				person.postal_code
			].filter(Boolean);
			return { address: parts.join(', '), fromHousehold: false };
		}
		const householdAddr = getHouseholdAddress(person);
		if (householdAddr) {
			return {
				address: householdAddr.address,
				fromHousehold: true,
				householdName: householdAddr.householdName
			};
		}
		return { address: '-', fromHousehold: false };
	}
</script>

<div class="overflow-x-auto" role="region" aria-label="People list">
	<table class="min-w-full divide-y divide-brand-border" aria-label="People table">
		<thead class="bg-brand-bg-subtle">
			<tr>
				<th
					scope="col"
					class="px-6 py-3 text-left text-xs font-medium text-brand-text-secondary uppercase tracking-wider"
				>
					<button
						onclick={() => handleSort('last_name')}
						class="group inline-flex items-center gap-1 hover:text-brand-primary"
					>
						Name
						<span
							class="flex-none rounded {sortBy === 'last_name'
								? 'text-brand-primary'
								: 'text-brand-text-muted group-hover:text-brand-text-secondary'}"
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
						class="group inline-flex items-center gap-1 hover:text-brand-primary"
					>
						Age
						<span
							class="flex-none rounded {sortBy === 'date_of_birth'
								? 'text-brand-primary'
								: 'text-brand-text-muted group-hover:text-brand-text-secondary'}"
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
						class="group inline-flex items-center gap-1 hover:text-brand-primary"
					>
						Contact
						<span
							class="flex-none rounded {sortBy === 'email'
								? 'text-brand-primary'
								: 'text-brand-text-muted group-hover:text-brand-text-secondary'}"
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
					Address
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
		<tbody class="bg-white divide-y divide-brand-border">
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
					class="hover:bg-brand-bg-subtle cursor-pointer transition-colors"
				>
					<td class="px-6 py-4 whitespace-nowrap">
						<div class="flex items-center">
							<div class="text-sm font-medium text-brand-primary">{formatName(person)}</div>
							{#if person.death}
								<span class="ml-2 inline-flex items-center text-brand-text-muted" title="Deceased">
									<svg class="w-4 h-4" fill="currentColor" viewBox="0 0 24 24" aria-hidden="true">
										<path
											d="M12 2c.3 0 .5.2.5.5v9.5h9.5c.3 0 .5.2.5.5s-.2.5-.5.5H12.5v9.5c0 .3-.2.5-.5.5s-.5-.2-.5-.5V12.5H2c-.3 0-.5-.2-.5-.5s.2-.5.5-.5h9.5V2.5c0-.3.2-.5.5-.5z"
										/>
									</svg>
								</span>
							{/if}
						</div>
					</td>
					<td class="px-6 py-4 whitespace-nowrap">
						<div class="text-sm text-brand-primary">
							{calculateAge(person.date_of_birth) ?? '-'}
						</div>
					</td>
					<td class="px-6 py-4 whitespace-nowrap">
						<div class="text-sm text-brand-primary">{formatGender(person.gender)}</div>
					</td>
					<td class="px-6 py-4 whitespace-nowrap">
						<div class="text-sm text-brand-primary">{person.email || '-'}</div>
					</td>
					<td class="px-6 py-4">
						{#if getDisplayAddress(person).fromHousehold}
							{@const addr = getDisplayAddress(person)}
							<div class="text-sm text-brand-primary" title="From household: {addr.householdName}">
								<span class="inline-flex items-center gap-1">
									<svg
										class="w-3.5 h-3.5 text-brand-text-muted flex-shrink-0"
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
									<span class="truncate max-w-[200px]">{addr.address}</span>
								</span>
								<span class="text-xs text-brand-text-muted block mt-0.5"
									>from {addr.householdName}</span
								>
							</div>
						{:else}
							<div class="text-sm text-brand-primary truncate max-w-[200px]">
								{getDisplayAddress(person).address}
							</div>
						{/if}
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
							class="text-brand-text-muted hover:text-brand-text-secondary mr-3"
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
							class="text-brand-accent hover:text-brand-accent/80"
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
