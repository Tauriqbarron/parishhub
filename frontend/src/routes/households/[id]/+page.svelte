<script lang="ts">
	import { page } from '$app/stores';
	import { goto } from '$app/navigation';
	import {
		householdApi,
		type HouseholdWithMembers,
		type HouseholdUpdate,
		type HouseholdRole,
		type HouseholdMember
	} from '$lib/api';
	import { toasts } from '$lib/stores/toast';
	import AddMemberModal from '$lib/components/AddMemberModal.svelte';

	let household = $state<HouseholdWithMembers | null>(null);
	let loading = $state(true);
	let error = $state<string | null>(null);
	let isEditing = $state(false);
	let isSaving = $state(false);
	let showAddMemberModal = $state(false);
	let editingMemberRole = $state<{ personId: number; currentRole: HouseholdRole } | null>(null);

	// Form state for editing
	let editForm = $state<HouseholdUpdate>({});

	const householdId = $derived(Number($page.params.id));

	const roleLabels: Record<HouseholdRole, string> = {
		head: 'Head',
		spouse: 'Spouse',
		child: 'Child',
		other: 'Other'
	};

	async function loadHousehold() {
		loading = true;
		error = null;

		try {
			household = await householdApi.get(householdId);
			resetEditForm();
		} catch (err) {
			error = err instanceof Error ? err.message : 'Failed to load household';
		} finally {
			loading = false;
		}
	}

	function resetEditForm() {
		if (household) {
			editForm = {
				name: household.name,
				address_line1: household.address_line1,
				address_line2: household.address_line2,
				city: household.city,
				postal_code: household.postal_code
			};
		}
	}

	function toggleEdit() {
		if (isEditing) {
			resetEditForm();
		}
		isEditing = !isEditing;
	}

	async function handleSave() {
		if (!household) return;

		isSaving = true;
		try {
			await householdApi.update(household.id, editForm);
			await loadHousehold();
			isEditing = false;
			toasts.success('Household updated successfully');
		} catch (err) {
			toasts.error(err instanceof Error ? err.message : 'Failed to update household');
		} finally {
			isSaving = false;
		}
	}

	function handleCancel() {
		resetEditForm();
		isEditing = false;
	}

	function handleMemberAdded(member: HouseholdMember) {
		showAddMemberModal = false;
		loadHousehold();
	}

	async function handleRemoveMember(personId: number, personName: string) {
		if (!household) return;
		if (!confirm(`Are you sure you want to remove ${personName} from this household?`)) return;

		try {
			await householdApi.removeMember(household.id, personId);
			toasts.success('Member removed successfully');
			await loadHousehold();
		} catch (err) {
			toasts.error(err instanceof Error ? err.message : 'Failed to remove member');
		}
	}

	function startEditRole(personId: number, currentRole: HouseholdRole) {
		editingMemberRole = { personId, currentRole };
	}

	function cancelEditRole() {
		editingMemberRole = null;
	}

	async function saveRoleChange(personId: number, newRole: HouseholdRole) {
		if (!household) return;

		try {
			await householdApi.updateMember(household.id, personId, { role: newRole });
			toasts.success('Role updated successfully');
			editingMemberRole = null;
			await loadHousehold();
		} catch (err) {
			toasts.error(err instanceof Error ? err.message : 'Failed to update role');
		}
	}

	async function handleDeleteHousehold() {
		if (!household) return;
		if (
			!confirm(
				`Are you sure you want to delete "${household.name}"? This will remove all member associations.`
			)
		)
			return;

		try {
			await householdApi.delete(household.id);
			toasts.success('Household deleted successfully');
			goto('/households');
		} catch (err) {
			toasts.error(err instanceof Error ? err.message : 'Failed to delete household');
		}
	}

	function formatAddress(): string {
		if (!household) return '';
		const parts = [
			household.address_line1,
			household.address_line2,
			household.city,
			household.postal_code
		].filter(Boolean);
		return parts.join(', ') || 'No address';
	}

	function formatMemberName(member: HouseholdMember): string {
		const middle = member.person.middle_name ? ` ${member.person.middle_name}` : '';
		return `${member.person.first_name}${middle} ${member.person.last_name}`;
	}

	$effect(() => {
		if (householdId) {
			loadHousehold();
		}
	});
</script>

<div>
	<!-- Back link -->
	<div class="mb-4">
		<a
			href="/households"
			class="inline-flex items-center text-sm text-gray-500 hover:text-gray-700 transition-colors"
		>
			<svg class="w-4 h-4 mr-1" fill="none" stroke="currentColor" viewBox="0 0 24 24">
				<path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M15 19l-7-7 7-7" />
			</svg>
			Back to list
		</a>
	</div>

	{#if loading}
		<!-- Loading skeleton -->
		<div class="animate-pulse space-y-6">
			<div class="bg-white rounded-lg shadow p-6">
				<div class="flex items-center justify-between">
					<div class="space-y-2">
						<div class="h-8 bg-gray-200 rounded w-48"></div>
						<div class="h-4 bg-gray-200 rounded w-64"></div>
					</div>
					<div class="h-10 bg-gray-200 rounded w-20"></div>
				</div>
			</div>
			<div class="bg-white rounded-lg shadow p-6">
				<div class="h-6 bg-gray-200 rounded w-24 mb-4"></div>
				<div class="space-y-3">
					{#each Array.from({ length: 3 }, (_, i) => i) as i (i)}
						<div class="flex items-center justify-between p-3 border border-gray-200 rounded-lg">
							<div class="flex items-center gap-3">
								<div class="h-10 w-10 bg-gray-200 rounded-full"></div>
								<div class="h-4 bg-gray-200 rounded w-32"></div>
							</div>
							<div class="h-4 bg-gray-200 rounded w-16"></div>
						</div>
					{/each}
				</div>
			</div>
		</div>
	{:else if error}
		<!-- Error state -->
		<div class="bg-white rounded-lg shadow p-6 text-center">
			<svg
				class="mx-auto h-12 w-12 text-red-400"
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
			<h3 class="mt-2 text-sm font-medium text-gray-900">Error loading household</h3>
			<p class="mt-1 text-sm text-gray-500">{error}</p>
			<div class="mt-6 flex justify-center gap-3">
				<button
					onclick={() => loadHousehold()}
					class="inline-flex items-center px-4 py-2 border border-transparent text-sm font-medium rounded-md shadow-sm text-white bg-blue-600 hover:bg-blue-700"
				>
					Try again
				</button>
				<button
					onclick={() => goto('/households')}
					class="inline-flex items-center px-4 py-2 border border-gray-300 text-sm font-medium rounded-md shadow-sm text-gray-700 bg-white hover:bg-gray-50"
				>
					Go back
				</button>
			</div>
		</div>
	{:else if household}
		<!-- Household Header -->
		<div class="bg-white rounded-lg shadow">
			<div class="px-6 py-4 border-b border-gray-200">
				<div class="flex items-start justify-between">
					<div class="flex items-center gap-4">
						<div class="p-3 bg-blue-50 rounded-lg">
							<svg
								class="w-8 h-8 text-blue-600"
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
						</div>
						<div>
							{#if isEditing}
								<input
									type="text"
									bind:value={editForm.name}
									class="text-2xl font-bold text-gray-900 border-b-2 border-blue-500 focus:outline-none bg-transparent"
								/>
							{:else}
								<h1 class="text-2xl font-bold text-gray-900">{household.name}</h1>
							{/if}
							<p class="text-gray-600 mt-1">
								{household.member_count}
								{household.member_count === 1 ? 'member' : 'members'}
							</p>
						</div>
					</div>
					<div class="flex items-center gap-2">
						{#if isEditing}
							<button
								onclick={handleCancel}
								disabled={isSaving}
								class="px-4 py-2 text-sm font-medium text-gray-700 bg-white border border-gray-300 rounded-md hover:bg-gray-50 disabled:opacity-50"
							>
								Cancel
							</button>
							<button
								onclick={handleSave}
								disabled={isSaving}
								class="px-4 py-2 text-sm font-medium text-white bg-blue-600 rounded-md hover:bg-blue-700 disabled:opacity-50"
							>
								{isSaving ? 'Saving...' : 'Save'}
							</button>
						{:else}
							<button
								onclick={toggleEdit}
								class="px-4 py-2 text-sm font-medium text-gray-700 bg-white border border-gray-300 rounded-md hover:bg-gray-50"
							>
								Edit
							</button>
							<button
								onclick={handleDeleteHousehold}
								class="px-4 py-2 text-sm font-medium text-red-600 bg-white border border-red-300 rounded-md hover:bg-red-50"
							>
								Delete
							</button>
						{/if}
					</div>
				</div>
			</div>

			<!-- Address Section -->
			<div class="px-6 py-4">
				<h3 class="text-sm font-medium text-gray-500 uppercase tracking-wide mb-3">Address</h3>
				{#if isEditing}
					<div class="space-y-3">
						<div>
							<label for="address_line1" class="block text-sm font-medium text-gray-700">
								Address Line 1
							</label>
							<input
								type="text"
								id="address_line1"
								bind:value={editForm.address_line1}
								class="mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-blue-500 focus:ring-blue-500 sm:text-sm"
							/>
						</div>
						<div>
							<label for="address_line2" class="block text-sm font-medium text-gray-700">
								Address Line 2
							</label>
							<input
								type="text"
								id="address_line2"
								bind:value={editForm.address_line2}
								class="mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-blue-500 focus:ring-blue-500 sm:text-sm"
							/>
						</div>
						<div class="grid grid-cols-2 gap-4">
							<div>
								<label for="city" class="block text-sm font-medium text-gray-700">City</label>
								<input
									type="text"
									id="city"
									bind:value={editForm.city}
									class="mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-blue-500 focus:ring-blue-500 sm:text-sm"
								/>
							</div>
							<div>
								<label for="postal_code" class="block text-sm font-medium text-gray-700">
									Postal Code
								</label>
								<input
									type="text"
									id="postal_code"
									bind:value={editForm.postal_code}
									class="mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-blue-500 focus:ring-blue-500 sm:text-sm"
								/>
							</div>
						</div>
					</div>
				{:else}
					<p class="text-gray-900">{formatAddress()}</p>
				{/if}
			</div>
		</div>

		<!-- Members Section -->
		<div class="mt-6 bg-white rounded-lg shadow">
			<div class="px-6 py-4 border-b border-gray-200 flex items-center justify-between">
				<h2 class="text-lg font-medium text-gray-900">Members</h2>
				<button
					onclick={() => (showAddMemberModal = true)}
					class="inline-flex items-center px-3 py-1.5 text-sm font-medium text-blue-600 bg-blue-50 rounded-md hover:bg-blue-100 transition-colors"
				>
					<svg class="w-4 h-4 mr-1" fill="none" stroke="currentColor" viewBox="0 0 24 24">
						<path
							stroke-linecap="round"
							stroke-linejoin="round"
							stroke-width="2"
							d="M12 4v16m8-8H4"
						/>
					</svg>
					Add Member
				</button>
			</div>
			<div class="px-6 py-4">
				{#if household.members.length === 0}
					<p class="text-sm text-gray-500 text-center py-8">
						No members in this household yet. Add a member to get started.
					</p>
				{:else}
					<div class="space-y-3">
						{#each household.members as member (member.person_id)}
							<div
								class="flex items-center justify-between p-4 rounded-lg border border-gray-200 bg-gray-50 hover:bg-gray-100 transition-colors"
							>
								<div class="flex items-center gap-4">
									<div class="p-2 bg-white rounded-full shadow-sm">
										<svg
											class="w-6 h-6 text-gray-600"
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
										<a
											href="/people/{member.person_id}"
											class="font-medium text-gray-900 hover:text-blue-600 transition-colors"
										>
											{formatMemberName(member)}
										</a>
										<div class="flex items-center gap-2 mt-1">
											{#if editingMemberRole?.personId === member.person_id}
												<select
													value={editingMemberRole.currentRole}
													onchange={(e) =>
														saveRoleChange(
															member.person_id,
															(e.target as HTMLSelectElement).value as HouseholdRole
														)}
													class="text-xs rounded border-gray-300 shadow-sm focus:border-blue-500 focus:ring-blue-500"
												>
													{#each Object.entries(roleLabels) as [value, label] ([value, label])}
														<option {value}>{label}</option>
													{/each}
												</select>
												<button
													onclick={cancelEditRole}
													class="text-xs text-gray-500 hover:text-gray-700"
												>
													Cancel
												</button>
											{:else}
												<button
													onclick={() => startEditRole(member.person_id, member.role)}
													class="inline-flex items-center px-2 py-0.5 rounded text-xs font-medium bg-gray-200 text-gray-700 hover:bg-gray-300 transition-colors"
													title="Click to change role"
												>
													{roleLabels[member.role]}
													<svg
														class="w-3 h-3 ml-1"
														fill="none"
														stroke="currentColor"
														viewBox="0 0 24 24"
													>
														<path
															stroke-linecap="round"
															stroke-linejoin="round"
															stroke-width="2"
															d="M19 9l-7 7-7-7"
														/>
													</svg>
												</button>
											{/if}
											{#if member.is_primary_household}
												<span
													class="inline-flex items-center px-2 py-0.5 rounded text-xs font-medium bg-green-100 text-green-700"
												>
													Primary
												</span>
											{/if}
										</div>
									</div>
								</div>
								<button
									onclick={() => handleRemoveMember(member.person_id, formatMemberName(member))}
									class="p-2 rounded hover:bg-red-100 text-red-600 transition-colors"
									title="Remove from household"
								>
									<svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
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
	{/if}

	<!-- Add Member Modal -->
	{#if showAddMemberModal && household}
		<AddMemberModal
			householdId={household.id}
			existingMemberIds={household.members.map((m) => m.person_id)}
			onSave={handleMemberAdded}
			onClose={() => (showAddMemberModal = false)}
		/>
	{/if}
</div>
