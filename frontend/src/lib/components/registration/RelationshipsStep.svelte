<script lang="ts">
	import { registrationSessionStore } from '$lib/stores/registrationSession';
	import type {
		RegistrationMember,
		RegistrationMemberRelationship
	} from '$lib/stores/registrationSession';
	import { get } from 'svelte/store';

	const relationshipTypes = [
		{ value: 'parent', label: 'Parent of', inverse: 'child' },
		{ value: 'child', label: 'Child of', inverse: 'parent' },
		{ value: 'spouse', label: 'Spouse of', inverse: 'spouse' },
		{ value: 'sibling', label: 'Sibling of', inverse: 'sibling' }
	] as const;

	let members = $derived(get(registrationSessionStore).members);

	$effect(() => {
		const unsubscribe = registrationSessionStore.subscribe((session) => {
			members = session.members;
		});
		return unsubscribe;
	});

	let addingFor = $state<string | null>(null);
	let selectedTarget = $state<string>('');
	let selectedType = $state<string>('');

	function getMemberName(member: RegistrationMember): string {
		return `${member.firstName} ${member.lastName}`.trim() || 'Unnamed Member';
	}

	function getMemberById(tempId: string): RegistrationMember | undefined {
		return members.find((m) => m.tempId === tempId);
	}

	function getRelationshipLabel(type: string): string {
		const rel = relationshipTypes.find((r) => r.value === type);
		return rel ? rel.label.replace(' of', '') : type;
	}

	function getInverseType(type: string): string {
		const rel = relationshipTypes.find((r) => r.value === type);
		return rel?.inverse || type;
	}

	function hasRelationship(fromId: string, toId: string): boolean {
		const member = getMemberById(fromId);
		return member?.relationships.some((r) => r.targetTempId === toId) || false;
	}

	function getAvailableTargets(fromId: string): RegistrationMember[] {
		return members.filter((m) => m.tempId !== fromId && !hasRelationship(fromId, m.tempId));
	}

	function addRelationship(fromId: string, toId: string, type: string): void {
		const fromMember = getMemberById(fromId);
		const toMember = getMemberById(toId);
		if (!fromMember || !toMember) return;

		const newRelationship: RegistrationMemberRelationship = {
			targetTempId: toId,
			relationshipType: type
		};
		registrationSessionStore.updateMember(fromId, {
			relationships: [...fromMember.relationships, newRelationship]
		});

		const inverseType = getInverseType(type);
		if (!hasRelationship(toId, fromId)) {
			const inverseRelationship: RegistrationMemberRelationship = {
				targetTempId: fromId,
				relationshipType: inverseType
			};
			registrationSessionStore.updateMember(toId, {
				relationships: [...toMember.relationships, inverseRelationship]
			});
		}

		resetForm();
	}

	function removeRelationship(fromId: string, toId: string): void {
		const fromMember = getMemberById(fromId);
		const toMember = getMemberById(toId);
		if (!fromMember) return;

		registrationSessionStore.updateMember(fromId, {
			relationships: fromMember.relationships.filter((r) => r.targetTempId !== toId)
		});

		if (toMember) {
			registrationSessionStore.updateMember(toId, {
				relationships: toMember.relationships.filter((r) => r.targetTempId !== fromId)
			});
		}
	}

	function resetForm(): void {
		addingFor = null;
		selectedTarget = '';
		selectedType = '';
	}

	function handleAddClick(memberId: string): void {
		if (addingFor === memberId) {
			resetForm();
		} else {
			addingFor = memberId;
			selectedTarget = '';
			selectedType = '';
		}
	}

	function handleSubmit(memberId: string): void {
		if (selectedTarget && selectedType) {
			addRelationship(memberId, selectedTarget, selectedType);
		}
	}

	export function isValid(): boolean {
		return true;
	}
</script>

<div class="space-y-4">
	<p class="text-gray-600">Define how each family member is related to others in the household.</p>

	{#if members.length <= 1}
		<div class="text-center py-8 border-2 border-dashed border-gray-300 rounded-lg">
			<svg
				class="mx-auto h-12 w-12 text-gray-400"
				fill="none"
				stroke="currentColor"
				viewBox="0 0 24 24"
			>
				<path
					stroke-linecap="round"
					stroke-linejoin="round"
					stroke-width="2"
					d="M13 16h-1v-4h-1m1-4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z"
				/>
			</svg>
			<p class="mt-2 text-sm text-gray-500">
				{#if members.length === 0}
					No family members added yet
				{:else}
					Only one member in household - no relationships needed
				{/if}
			</p>
			<p class="text-xs text-gray-400">You can skip this step</p>
		</div>
	{:else}
		{#each members as member (member.tempId)}
			<div class="border rounded-lg p-4 bg-white shadow-sm">
				<div class="flex items-center justify-between mb-3">
					<h3 class="font-medium text-gray-900">
						{getMemberName(member)}
						{#if member.isHeadOfHousehold}
							<span class="ml-2 text-xs bg-blue-100 text-blue-800 px-2 py-0.5 rounded-full">
								Head of Household
							</span>
						{/if}
					</h3>
				</div>

				{#if member.relationships.length > 0}
					<div class="space-y-2 mb-3">
						{#each member.relationships as rel}
							{@const targetMember = getMemberById(rel.targetTempId)}
							{#if targetMember}
								<div class="flex items-center justify-between bg-gray-50 rounded px-3 py-2 text-sm">
									<span>
										<span class="text-gray-600">{getRelationshipLabel(rel.relationshipType)}</span>
										<span class="font-medium ml-1">{getMemberName(targetMember)}</span>
									</span>
									<button
										type="button"
										onclick={() => removeRelationship(member.tempId, rel.targetTempId)}
										class="text-red-500 hover:text-red-700 p-1"
										aria-label="Remove relationship"
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
							{/if}
						{/each}
					</div>
				{/if}

				{#if addingFor === member.tempId}
					{@const availableTargets = getAvailableTargets(member.tempId)}
					{#if availableTargets.length === 0}
						<p class="text-sm text-gray-500 italic">
							All relationships have been defined for this member.
						</p>
					{:else}
						<div class="flex flex-wrap gap-2 items-end">
							<div class="flex-1 min-w-[140px]">
								<label for="rel-type-{member.tempId}" class="block text-xs text-gray-500 mb-1">
									Relationship
								</label>
								<select
									id="rel-type-{member.tempId}"
									bind:value={selectedType}
									class="w-full border border-gray-300 rounded px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-blue-500"
								>
									<option value="">Select type...</option>
									{#each relationshipTypes as relType}
										<option value={relType.value}>{relType.label}</option>
									{/each}
								</select>
							</div>
							<div class="flex-1 min-w-[140px]">
								<label for="rel-target-{member.tempId}" class="block text-xs text-gray-500 mb-1">
									Family Member
								</label>
								<select
									id="rel-target-{member.tempId}"
									bind:value={selectedTarget}
									class="w-full border border-gray-300 rounded px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-blue-500"
								>
									<option value="">Select member...</option>
									{#each availableTargets as target}
										<option value={target.tempId}>{getMemberName(target)}</option>
									{/each}
								</select>
							</div>
							<div class="flex gap-2">
								<button
									type="button"
									onclick={() => handleSubmit(member.tempId)}
									disabled={!selectedTarget || !selectedType}
									class="px-3 py-2 bg-blue-600 text-white rounded text-sm hover:bg-blue-700 disabled:bg-gray-300 disabled:cursor-not-allowed focus:outline-none focus:ring-2 focus:ring-blue-500"
								>
									Add
								</button>
								<button
									type="button"
									onclick={resetForm}
									class="px-3 py-2 border border-gray-300 rounded text-sm hover:bg-gray-50 focus:outline-none focus:ring-2 focus:ring-gray-500"
								>
									Cancel
								</button>
							</div>
						</div>
					{/if}
				{:else}
					{@const availableTargets = getAvailableTargets(member.tempId)}
					{#if availableTargets.length > 0}
						<button
							type="button"
							onclick={() => handleAddClick(member.tempId)}
							class="text-sm text-blue-600 hover:text-blue-800 flex items-center gap-1"
						>
							<svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
								<path
									stroke-linecap="round"
									stroke-linejoin="round"
									stroke-width="2"
									d="M12 6v6m0 0v6m0-6h6m-6 0H6"
								/>
							</svg>
							Add relationship
						</button>
					{:else if member.relationships.length === 0}
						<p class="text-sm text-gray-500 italic">No relationships defined</p>
					{/if}
				{/if}
			</div>
		{/each}
	{/if}
</div>
