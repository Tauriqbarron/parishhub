<script lang="ts">
	import {
		householdApi,
		type HouseholdMembership,
		type HouseholdRole,
		type Household,
		type PaginatedResponse
	} from '$lib/api';
	import { toasts } from '$lib/stores/toast';

	interface Props {
		memberships: HouseholdMembership[];
		personId: number;
		onUpdate: () => void;
	}

	let { memberships, personId, onUpdate }: Props = $props();

	let showAddModal = $state(false);
	let availableHouseholds = $state<Household[]>([]);
	let selectedHouseholdId = $state<number | null>(null);
	let selectedRole = $state<HouseholdRole>('other');
	let isLoading = $state(false);

	const roleLabels: Record<HouseholdRole, string> = {
		head: 'Head',
		spouse: 'Spouse',
		child: 'Child',
		other: 'Other'
	};

	async function loadHouseholds() {
		try {
			const response: PaginatedResponse<Household> = await householdApi.list();
			// Filter out households the person is already a member of
			const currentHouseholdIds = new Set(memberships.map((m) => m.household_id));
			availableHouseholds = response.items.filter((h) => !currentHouseholdIds.has(h.id));
		} catch {
			toasts.error('Failed to load households');
		}
	}

	function openAddModal() {
		loadHouseholds();
		showAddModal = true;
	}

	async function handleAddToHousehold() {
		if (!selectedHouseholdId) return;

		isLoading = true;
		try {
			await householdApi.addMember(selectedHouseholdId, personId, selectedRole);
			toasts.success('Added to household successfully');
			showAddModal = false;
			selectedHouseholdId = null;
			selectedRole = 'other';
			onUpdate();
		} catch {
			toasts.error('Failed to add to household');
		} finally {
			isLoading = false;
		}
	}

	async function handleRemoveFromHousehold(householdId: number) {
		if (!confirm('Are you sure you want to remove this person from the household?')) return;

		try {
			await householdApi.removeMember(householdId, personId);
			toasts.success('Removed from household');
			onUpdate();
		} catch {
			toasts.error('Failed to remove from household');
		}
	}

	function handleBackdropClick(e: MouseEvent) {
		if (e.target === e.currentTarget) {
			showAddModal = false;
		}
	}
</script>

<div class="bg-white rounded-lg shadow">
	<div class="px-6 py-4 border-b border-brand-border flex items-center justify-between">
		<h2 class="text-lg font-medium text-brand-primary" id="household-card-heading">Household</h2>
		<button
			onclick={openAddModal}
			class="inline-flex items-center px-3 py-1.5 text-sm font-medium text-brand-accent bg-brand-accent/10 rounded-sm hover:bg-brand-accent/20 transition-colors"
			aria-label="Add to household"
		>
			<svg
				class="w-4 h-4 mr-1"
				fill="none"
				stroke="currentColor"
				viewBox="0 0 24 24"
				aria-hidden="true"
				role="img"
			>
				<path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 4v16m8-8H4" />
			</svg>
			Add
		</button>
	</div>
	<div class="px-6 py-4">
		{#if memberships.length === 0}
			<p class="text-sm text-brand-text-secondary text-center py-4">
				Not a member of any household
			</p>
		{:else}
			<div class="space-y-3">
				{#each memberships.filter((m) => m.household) as membership (membership.household_id)}
					<div
						class="flex items-center justify-between p-3 rounded-lg border border-brand-border bg-brand-bg-subtle"
					>
						<div class="flex items-center gap-3">
							<div class="p-2 bg-white rounded-lg shadow-sm">
								<svg
									class="w-5 h-5 text-brand-text-secondary"
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
							<div>
								<a
									href="/households/{membership.household_id}"
									class="font-medium text-brand-primary hover:text-brand-accent transition-colors"
								>
									{membership.household?.name ?? 'Unknown Household'}
								</a>
								<div class="text-sm text-brand-text-secondary flex items-center gap-2">
									<span
										class="inline-flex items-center px-2 py-0.5 rounded text-xs font-medium bg-brand-bg-muted text-brand-primary"
									>
										{roleLabels[membership.role]}
									</span>
									{#if membership.is_primary_household}
										<span
											class="inline-flex items-center px-2 py-0.5 rounded text-xs font-medium bg-brand-success/10 text-brand-success"
										>
											Primary
										</span>
									{/if}
								</div>
							</div>
						</div>
						<button
							onclick={() => handleRemoveFromHousehold(membership.household_id)}
							class="p-1.5 rounded hover:bg-brand-error/10 text-brand-error transition-colors"
							aria-label="Remove from {membership.household?.name ?? 'household'}"
						>
							<svg
								class="w-4 h-4"
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
									d="M6 18L18 6M6 6l12 12"
								/>
							</svg>
						</button>
					</div>
				{/each}
			</div>
		{/if}
	</div>
</div>

<!-- Add to Household Modal -->
{#if showAddModal}
	<!-- svelte-ignore a11y_no_noninteractive_element_interactions -->
	<!-- svelte-ignore a11y_click_events_have_key_events -->
	<div
		class="fixed inset-0 z-50 overflow-y-auto"
		aria-labelledby="modal-title"
		role="dialog"
		aria-modal="true"
		onclick={handleBackdropClick}
		tabindex="-1"
	>
		<div class="flex min-h-full items-end justify-center p-4 text-center sm:items-center sm:p-0">
			<div class="fixed inset-0 bg-brand-bg-subtle0 bg-opacity-75 transition-opacity"></div>

			<div
				class="relative transform overflow-hidden rounded-lg bg-white text-left shadow-xl transition-all sm:my-8 sm:w-full sm:max-w-lg"
				onclick={(e) => e.stopPropagation()}
				role="document"
			>
				<div class="bg-white px-4 pb-4 pt-5 sm:p-6 sm:pb-4">
					<div class="flex items-center justify-between mb-4">
						<h3 class="text-lg font-semibold text-brand-primary" id="modal-title">
							Add to Household
						</h3>
						<button
							type="button"
							onclick={() => (showAddModal = false)}
							class="text-brand-text-muted hover:text-brand-text-secondary"
							aria-label="Close modal"
						>
							<svg
								class="h-6 w-6"
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
									d="M6 18L18 6M6 6l12 12"
								/>
							</svg>
						</button>
					</div>

					{#if availableHouseholds.length === 0}
						<p class="text-sm text-brand-text-secondary text-center py-4">
							No available households. Create a new household first.
						</p>
					{:else}
						<div class="space-y-4">
							<div>
								<label for="household" class="block text-sm font-medium text-brand-primary">
									Select Household <span aria-hidden="true">*</span><span class="sr-only"
										>(required)</span
									>
								</label>
								<select
									id="household"
									name="household"
									bind:value={selectedHouseholdId}
									aria-required="true"
									class="mt-1 block w-full rounded-sm border-brand-border shadow-sm focus:border-blue-500 focus:ring-blue-500 sm:text-sm"
								>
									<option value={null}>Choose a household...</option>
									{#each availableHouseholds as household (household.id)}
										<option value={household.id}>{household.name}</option>
									{/each}
								</select>
							</div>

							<div>
								<label for="role" class="block text-sm font-medium text-brand-primary"
									>Role <span aria-hidden="true">*</span><span class="sr-only">(required)</span
									></label
								>
								<select
									id="role"
									name="role"
									bind:value={selectedRole}
									aria-required="true"
									class="mt-1 block w-full rounded-sm border-brand-border shadow-sm focus:border-blue-500 focus:ring-blue-500 sm:text-sm"
								>
									{#each Object.entries(roleLabels) as [value, label] ([value, label])}
										<option {value}>{label}</option>
									{/each}
								</select>
							</div>
						</div>
					{/if}
				</div>

				<div class="bg-brand-bg-subtle px-4 py-3 sm:flex sm:flex-row-reverse sm:px-6 gap-2">
					{#if availableHouseholds.length > 0}
						<button
							type="button"
							onclick={handleAddToHousehold}
							disabled={isLoading || !selectedHouseholdId}
							class="inline-flex w-full justify-center rounded-sm bg-blue-600 px-3 py-2 text-sm font-semibold text-white shadow-sm hover:bg-blue-500 sm:w-auto disabled:opacity-50"
						>
							{isLoading ? 'Adding...' : 'Add to Household'}
						</button>
					{/if}
					<button
						type="button"
						onclick={() => (showAddModal = false)}
						class="mt-3 inline-flex w-full justify-center rounded-sm bg-white px-3 py-2 text-sm font-semibold text-brand-primary shadow-sm ring-1 ring-inset ring-gray-300 hover:bg-brand-bg-subtle sm:mt-0 sm:w-auto"
					>
						Cancel
					</button>
				</div>
			</div>
		</div>
	</div>
{/if}
