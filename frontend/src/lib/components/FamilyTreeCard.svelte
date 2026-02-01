<script lang="ts">
	import {
		relationshipApi,
		personApi,
		type FamilyTree,
		type FamilyMember,
		type RelationshipType,
		type Person,
		type PaginatedResponse
	} from '$lib/api';
	import { toasts } from '$lib/stores/toast';

	interface Props {
		familyTree: FamilyTree;
		personId: number;
		onRemoveRelationship: (relationshipId: number) => void;
		onUpdate: () => void;
	}

	let { familyTree, personId, onRemoveRelationship, onUpdate }: Props = $props();

	let showAddModal = $state(false);
	let availablePeople = $state<Person[]>([]);
	let selectedPersonId = $state<number | null>(null);
	let selectedRelationshipType = $state<RelationshipType>('spouse');
	let searchQuery = $state('');
	let isLoading = $state(false);
	let isSearching = $state(false);

	const relationshipLabels: Record<RelationshipType, string> = {
		parent: 'Parent',
		child: 'Child',
		spouse: 'Spouse',
		sibling: 'Sibling'
	};

	function formatName(member: FamilyMember): string {
		const parts = [member.first_name];
		if (member.middle_name) parts.push(member.middle_name);
		parts.push(member.last_name);
		return parts.join(' ');
	}

	// Get all existing related person IDs to exclude from search
	const existingRelatedIds = $derived(
		new Set([
			...familyTree.parents.map((p) => p.id),
			...familyTree.children.map((c) => c.id),
			...familyTree.siblings.map((s) => s.id),
			...(familyTree.spouse ? [familyTree.spouse.id] : []),
			personId
		])
	);

	async function searchPeople() {
		if (searchQuery.length < 2) {
			availablePeople = [];
			return;
		}

		isSearching = true;
		try {
			const response: PaginatedResponse<Person> = await personApi.list({ search: searchQuery });
			availablePeople = response.items.filter((p) => !existingRelatedIds.has(p.id));
		} catch {
			toasts.error('Failed to search people');
		} finally {
			isSearching = false;
		}
	}

	function openAddModal() {
		searchQuery = '';
		availablePeople = [];
		selectedPersonId = null;
		showAddModal = true;
	}

	async function handleAddRelationship() {
		if (!selectedPersonId) return;

		isLoading = true;
		try {
			await relationshipApi.create(personId, selectedPersonId, selectedRelationshipType);
			toasts.success('Relationship added successfully');
			showAddModal = false;
			onUpdate();
		} catch {
			toasts.error('Failed to add relationship');
		} finally {
			isLoading = false;
		}
	}

	function handleBackdropClick(e: MouseEvent) {
		if (e.target === e.currentTarget) {
			showAddModal = false;
		}
	}

	const hasAnyRelationships = $derived(
		familyTree.parents.length > 0 ||
			familyTree.children.length > 0 ||
			familyTree.siblings.length > 0 ||
			familyTree.spouse !== null
	);
</script>

<div class="bg-white rounded-lg shadow">
	<div class="px-6 py-4 border-b border-gray-200 flex items-center justify-between">
		<h2 class="text-lg font-medium text-gray-900" id="family-tree-heading">Family</h2>
		<button
			onclick={openAddModal}
			class="inline-flex items-center px-3 py-1.5 text-sm font-medium text-blue-600 bg-blue-50 rounded-md hover:bg-blue-100 transition-colors"
			aria-label="Add family relationship"
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
		{#if !hasAnyRelationships}
			<p class="text-sm text-gray-500 text-center py-4">No family relationships recorded</p>
		{:else}
			<div class="space-y-4">
				<!-- Spouse -->
				{#if familyTree.spouse}
					<div>
						<h3 class="text-sm font-medium text-gray-500 mb-2">Spouse</h3>
						<div
							class="flex items-center justify-between p-3 rounded-lg border border-pink-200 bg-pink-50"
						>
							<div class="flex items-center gap-3">
								<div class="w-8 h-8 rounded-full bg-pink-200 flex items-center justify-center">
									<svg
										class="w-4 h-4 text-pink-600"
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
											d="M4.318 6.318a4.5 4.5 0 000 6.364L12 20.364l7.682-7.682a4.5 4.5 0 00-6.364-6.364L12 7.636l-1.318-1.318a4.5 4.5 0 00-6.364 0z"
										/>
									</svg>
								</div>
								<a
									href="/people/{familyTree.spouse.id}"
									class="font-medium text-gray-900 hover:text-blue-600 transition-colors"
								>
									{formatName(familyTree.spouse)}
								</a>
							</div>
							<button
								onclick={() => onRemoveRelationship(familyTree.spouse!.relationship_id)}
								class="p-1.5 rounded hover:bg-red-100 text-red-600 transition-colors"
								aria-label="Remove spouse relationship with {formatName(familyTree.spouse)}"
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
					</div>
				{/if}

				<!-- Parents -->
				{#if familyTree.parents.length > 0}
					<div>
						<h3 class="text-sm font-medium text-gray-500 mb-2">Parents</h3>
						<div class="space-y-2">
							{#each familyTree.parents as parent (parent.id)}
								<div
									class="flex items-center justify-between p-3 rounded-lg border border-blue-200 bg-blue-50"
								>
									<div class="flex items-center gap-3">
										<div
											class="w-8 h-8 rounded-full bg-blue-200 flex items-center justify-center text-blue-600 text-sm font-medium"
											aria-hidden="true"
										>
											P
										</div>
										<a
											href="/people/{parent.id}"
											class="font-medium text-gray-900 hover:text-blue-600 transition-colors"
										>
											{formatName(parent)}
										</a>
									</div>
									<button
										onclick={() => onRemoveRelationship(parent.relationship_id)}
										class="p-1.5 rounded hover:bg-red-100 text-red-600 transition-colors"
										aria-label="Remove parent relationship with {formatName(parent)}"
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
					</div>
				{/if}

				<!-- Children -->
				{#if familyTree.children.length > 0}
					<div>
						<h3 class="text-sm font-medium text-gray-500 mb-2">Children</h3>
						<div class="space-y-2">
							{#each familyTree.children as child (child.id)}
								<div
									class="flex items-center justify-between p-3 rounded-lg border border-green-200 bg-green-50"
								>
									<div class="flex items-center gap-3">
										<div
											class="w-8 h-8 rounded-full bg-green-200 flex items-center justify-center text-green-600 text-sm font-medium"
											aria-hidden="true"
										>
											C
										</div>
										<a
											href="/people/{child.id}"
											class="font-medium text-gray-900 hover:text-blue-600 transition-colors"
										>
											{formatName(child)}
										</a>
									</div>
									<button
										onclick={() => onRemoveRelationship(child.relationship_id)}
										class="p-1.5 rounded hover:bg-red-100 text-red-600 transition-colors"
										aria-label="Remove child relationship with {formatName(child)}"
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
					</div>
				{/if}

				<!-- Siblings -->
				{#if familyTree.siblings.length > 0}
					<div>
						<h3 class="text-sm font-medium text-gray-500 mb-2">Siblings</h3>
						<div class="space-y-2">
							{#each familyTree.siblings as sibling (sibling.id)}
								<div
									class="flex items-center justify-between p-3 rounded-lg border border-purple-200 bg-purple-50"
								>
									<div class="flex items-center gap-3">
										<div
											class="w-8 h-8 rounded-full bg-purple-200 flex items-center justify-center text-purple-600 text-sm font-medium"
											aria-hidden="true"
										>
											S
										</div>
										<a
											href="/people/{sibling.id}"
											class="font-medium text-gray-900 hover:text-blue-600 transition-colors"
										>
											{formatName(sibling)}
										</a>
									</div>
									<button
										onclick={() => onRemoveRelationship(sibling.relationship_id)}
										class="p-1.5 rounded hover:bg-red-100 text-red-600 transition-colors"
										aria-label="Remove sibling relationship with {formatName(sibling)}"
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
					</div>
				{/if}
			</div>
		{/if}
	</div>
</div>

<!-- Add Relationship Modal -->
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
			<div class="fixed inset-0 bg-gray-500 bg-opacity-75 transition-opacity"></div>

			<div
				class="relative transform overflow-hidden rounded-lg bg-white text-left shadow-xl transition-all sm:my-8 sm:w-full sm:max-w-lg"
				onclick={(e) => e.stopPropagation()}
				role="document"
			>
				<div class="bg-white px-4 pb-4 pt-5 sm:p-6 sm:pb-4">
					<div class="flex items-center justify-between mb-4">
						<h3 class="text-lg font-semibold text-gray-900" id="modal-title">Add Relationship</h3>
						<button
							type="button"
							onclick={() => (showAddModal = false)}
							class="text-gray-400 hover:text-gray-500"
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

					<div class="space-y-4">
						<!-- Search for person -->
						<div>
							<label for="search" class="block text-sm font-medium text-gray-700">
								Search Person <span aria-hidden="true">*</span><span class="sr-only"
									>(required)</span
								>
							</label>
							<div class="mt-1 relative">
								<input
									type="text"
									id="search"
									name="search"
									bind:value={searchQuery}
									oninput={() => searchPeople()}
									placeholder="Type at least 2 characters..."
									aria-required="true"
									class="block w-full rounded-md border-gray-300 shadow-sm focus:border-blue-500 focus:ring-blue-500 sm:text-sm"
								/>
								{#if isSearching}
									<div class="absolute right-3 top-1/2 -translate-y-1/2" aria-hidden="true">
										<svg
											class="w-4 h-4 animate-spin text-gray-400"
											fill="none"
											viewBox="0 0 24 24"
											role="img"
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
						</div>

						<!-- Search results -->
						{#if availablePeople.length > 0}
							<div class="max-h-48 overflow-y-auto border rounded-md divide-y">
								{#each availablePeople as person (person.id)}
									<button
										type="button"
										onclick={() => (selectedPersonId = person.id)}
										class="w-full px-3 py-2 text-left hover:bg-gray-50 transition-colors {selectedPersonId ===
										person.id
											? 'bg-blue-50 border-l-2 border-blue-500'
											: ''}"
									>
										<div class="font-medium text-gray-900">
											{person.first_name}
											{person.middle_name ?? ''}
											{person.last_name}
										</div>
										{#if person.email}
											<div class="text-sm text-gray-500">{person.email}</div>
										{/if}
									</button>
								{/each}
							</div>
						{:else if searchQuery.length >= 2 && !isSearching}
							<p class="text-sm text-gray-500 text-center py-2">No people found</p>
						{/if}

						<!-- Relationship type -->
						<div>
							<label for="relationship_type" class="block text-sm font-medium text-gray-700">
								Relationship Type <span aria-hidden="true">*</span><span class="sr-only"
									>(required)</span
								>
							</label>
							<select
								id="relationship_type"
								name="relationship_type"
								bind:value={selectedRelationshipType}
								aria-required="true"
								aria-describedby="relationship-help"
								class="mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-blue-500 focus:ring-blue-500 sm:text-sm"
							>
								{#each Object.entries(relationshipLabels) as [value, label] ([value, label])}
									<option {value}>{label}</option>
								{/each}
							</select>
							<p id="relationship-help" class="mt-1 text-xs text-gray-500">
								This describes the selected person's relationship to this person
							</p>
						</div>
					</div>
				</div>

				<div class="bg-gray-50 px-4 py-3 sm:flex sm:flex-row-reverse sm:px-6 gap-2">
					<button
						type="button"
						onclick={handleAddRelationship}
						disabled={isLoading || !selectedPersonId}
						class="inline-flex w-full justify-center rounded-md bg-blue-600 px-3 py-2 text-sm font-semibold text-white shadow-sm hover:bg-blue-500 sm:w-auto disabled:opacity-50"
					>
						{isLoading ? 'Adding...' : 'Add Relationship'}
					</button>
					<button
						type="button"
						onclick={() => (showAddModal = false)}
						class="mt-3 inline-flex w-full justify-center rounded-md bg-white px-3 py-2 text-sm font-semibold text-gray-900 shadow-sm ring-1 ring-inset ring-gray-300 hover:bg-gray-50 sm:mt-0 sm:w-auto"
					>
						Cancel
					</button>
				</div>
			</div>
		</div>
	</div>
{/if}
