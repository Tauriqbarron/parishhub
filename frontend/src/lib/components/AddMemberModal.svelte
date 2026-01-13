<script lang="ts">
	import {
		personApi,
		householdApi,
		type Person,
		type HouseholdRole,
		type HouseholdMember
	} from '$lib/api';
	import { toasts } from '$lib/stores/toast';

	interface Props {
		householdId: number;
		existingMemberIds: number[];
		onSave: (member: HouseholdMember) => void;
		onClose: () => void;
	}

	let { householdId, existingMemberIds, onSave, onClose }: Props = $props();

	let isLoading = $state(false);
	let searchQuery = $state('');
	let searchResults = $state<Person[]>([]);
	let isSearching = $state(false);
	let selectedPerson = $state<Person | null>(null);
	let selectedRole = $state<HouseholdRole>('other');
	let isPrimary = $state(true);

	const roleLabels: Record<HouseholdRole, string> = {
		head: 'Head',
		spouse: 'Spouse',
		child: 'Child',
		other: 'Other'
	};

	let searchTimeout: ReturnType<typeof setTimeout>;

	function handleSearchInput(e: Event) {
		const value = (e.target as HTMLInputElement).value;
		searchQuery = value;

		clearTimeout(searchTimeout);

		if (value.length < 2) {
			searchResults = [];
			return;
		}

		searchTimeout = setTimeout(async () => {
			isSearching = true;
			try {
				const response = await personApi.list({ search: value, per_page: 10 });
				// Filter out existing members
				searchResults = response.items.filter((p) => !existingMemberIds.includes(p.id));
			} catch (err) {
				toasts.error('Failed to search people');
			} finally {
				isSearching = false;
			}
		}, 300);
	}

	function selectPerson(person: Person) {
		selectedPerson = person;
		searchQuery = '';
		searchResults = [];
	}

	function clearSelection() {
		selectedPerson = null;
	}

	async function handleSubmit(e: Event) {
		e.preventDefault();

		if (!selectedPerson) {
			toasts.error('Please select a person');
			return;
		}

		isLoading = true;
		try {
			const member = await householdApi.addMember(
				householdId,
				selectedPerson.id,
				selectedRole,
				isPrimary
			);
			toasts.success('Member added successfully');
			onSave(member);
		} catch (err) {
			toasts.error(err instanceof Error ? err.message : 'Failed to add member');
		} finally {
			isLoading = false;
		}
	}

	function handleBackdropClick(e: MouseEvent) {
		if (e.target === e.currentTarget) {
			onClose();
		}
	}

	function formatPersonName(person: Person): string {
		const middle = person.middle_name ? ` ${person.middle_name}` : '';
		return `${person.first_name}${middle} ${person.last_name}`;
	}
</script>

<!-- svelte-ignore a11y_no_noninteractive_element_interactions -->
<!-- svelte-ignore a11y_click_events_have_key_events -->
<!-- svelte-ignore a11y_interactive_supports_focus -->
<div
	class="fixed inset-0 z-50 overflow-y-auto"
	aria-labelledby="modal-title"
	role="dialog"
	aria-modal="true"
	onclick={handleBackdropClick}
>
	<div class="flex min-h-full items-end justify-center p-4 text-center sm:items-center sm:p-0">
		<div class="fixed inset-0 bg-gray-500 bg-opacity-75 transition-opacity"></div>

		<div
			class="relative transform overflow-hidden rounded-lg bg-white text-left shadow-xl transition-all sm:my-8 sm:w-full sm:max-w-lg"
			onclick={(e) => e.stopPropagation()}
		>
			<form onsubmit={handleSubmit}>
				<div class="bg-white px-4 pb-4 pt-5 sm:p-6 sm:pb-4">
					<div class="flex items-center justify-between mb-4">
						<h3 class="text-lg font-semibold text-gray-900" id="modal-title">Add Member</h3>
						<button type="button" onclick={onClose} class="text-gray-400 hover:text-gray-500">
							<svg class="h-6 w-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
								<path
									stroke-linecap="round"
									stroke-linejoin="round"
									stroke-width="2"
									d="M6 18L18 6M6 6l12 12"
								/>
							</svg>
						</button>
					</div>

					<div class="space-y-4">
						<!-- Person Selection -->
						{#if selectedPerson}
							<div>
								<label class="block text-sm font-medium text-gray-700 mb-1">Selected Person</label>
								<div
									class="flex items-center justify-between p-3 rounded-lg border border-blue-200 bg-blue-50"
								>
									<div class="flex items-center gap-3">
										<div class="p-2 bg-white rounded-lg shadow-sm">
											<svg
												class="w-5 h-5 text-blue-600"
												fill="none"
												stroke="currentColor"
												viewBox="0 0 24 24"
											>
												<path
													stroke-linecap="round"
													stroke-linejoin="round"
													stroke-width="2"
													d="M16 7a4 4 0 11-8 0 4 4 0 018 0zM12 14a7 7 0 00-7 7h14a7 7 0 00-7-7z"
												/>
											</svg>
										</div>
										<div>
											<div class="font-medium text-gray-900">
												{formatPersonName(selectedPerson)}
											</div>
											{#if selectedPerson.email}
												<div class="text-sm text-gray-500">{selectedPerson.email}</div>
											{/if}
										</div>
									</div>
									<button
										type="button"
										onclick={clearSelection}
										class="p-1.5 rounded hover:bg-blue-100 text-blue-600 transition-colors"
										title="Remove selection"
									>
										<svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
											<path
												stroke-linecap="round"
												stroke-linejoin="round"
												stroke-width="2"
												d="M6 18L18 6M6 6l12 12"
											/>
										</svg>
									</button>
								</div>
							</div>
						{:else}
							<div>
								<label for="person-search" class="block text-sm font-medium text-gray-700">
									Search Person <span class="text-red-500">*</span>
								</label>
								<div class="relative mt-1">
									<input
										type="text"
										id="person-search"
										value={searchQuery}
										oninput={handleSearchInput}
										placeholder="Type to search by name or email..."
										class="block w-full rounded-md border-gray-300 shadow-sm focus:border-blue-500 focus:ring-blue-500 sm:text-sm"
									/>
									{#if isSearching}
										<div class="absolute right-3 top-2.5">
											<svg
												class="animate-spin h-5 w-5 text-gray-400"
												fill="none"
												viewBox="0 0 24 24"
											>
												<circle
													class="opacity-25"
													cx="12"
													cy="12"
													r="10"
													stroke="currentColor"
													stroke-width="4"
												></circle>
												<path
													class="opacity-75"
													fill="currentColor"
													d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"
												></path>
											</svg>
										</div>
									{/if}
								</div>

								<!-- Search Results -->
								{#if searchResults.length > 0}
									<div
										class="mt-2 border border-gray-200 rounded-md shadow-sm max-h-48 overflow-y-auto"
									>
										{#each searchResults as person (person.id)}
											<button
												type="button"
												onclick={() => selectPerson(person)}
												class="w-full px-4 py-2 text-left hover:bg-gray-50 border-b border-gray-100 last:border-b-0"
											>
												<div class="font-medium text-gray-900">{formatPersonName(person)}</div>
												{#if person.email}
													<div class="text-sm text-gray-500">{person.email}</div>
												{/if}
											</button>
										{/each}
									</div>
								{:else if searchQuery.length >= 2 && !isSearching}
									<p class="mt-2 text-sm text-gray-500">No people found matching your search.</p>
								{/if}
							</div>
						{/if}

						<!-- Role Selection -->
						<div>
							<label for="role" class="block text-sm font-medium text-gray-700">
								Role <span class="text-red-500">*</span>
							</label>
							<select
								id="role"
								bind:value={selectedRole}
								class="mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-blue-500 focus:ring-blue-500 sm:text-sm"
							>
								{#each Object.entries(roleLabels) as [value, label] ([value, label])}
									<option {value}>{label}</option>
								{/each}
							</select>
						</div>

						<!-- Primary Household -->
						<div class="flex items-center">
							<input
								type="checkbox"
								id="is-primary"
								bind:checked={isPrimary}
								class="h-4 w-4 rounded border-gray-300 text-blue-600 focus:ring-blue-500"
							/>
							<label for="is-primary" class="ml-2 block text-sm text-gray-900">
								Primary household for this person
							</label>
						</div>
					</div>
				</div>

				<div class="bg-gray-50 px-4 py-3 sm:flex sm:flex-row-reverse sm:px-6 gap-2">
					<button
						type="submit"
						disabled={isLoading || !selectedPerson}
						class="inline-flex w-full justify-center rounded-md bg-blue-600 px-3 py-2 text-sm font-semibold text-white shadow-sm hover:bg-blue-500 sm:w-auto disabled:opacity-50"
					>
						{isLoading ? 'Adding...' : 'Add Member'}
					</button>
					<button
						type="button"
						onclick={onClose}
						class="mt-3 inline-flex w-full justify-center rounded-md bg-white px-3 py-2 text-sm font-semibold text-gray-900 shadow-sm ring-1 ring-inset ring-gray-300 hover:bg-gray-50 sm:mt-0 sm:w-auto"
					>
						Cancel
					</button>
				</div>
			</form>
		</div>
	</div>
</div>
