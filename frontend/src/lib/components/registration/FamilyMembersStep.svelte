<script lang="ts">
	import { registrationSessionStore } from '$lib/stores/registrationSession';
	import type { FamilyRole } from '$lib/stores/registrationSession';
	import MemberCard from './MemberCard.svelte';
	import { get } from 'svelte/store';

	let members = $derived(get(registrationSessionStore).members);

	$effect(() => {
		const unsubscribe = registrationSessionStore.subscribe((session) => {
			members = session.members;
		});
		return unsubscribe;
	});

	let validationErrors = $state<Record<string, string[]>>({});

	let parents = $derived(members.filter((m) => m.familyRole === 'parent'));
	let children = $derived(members.filter((m) => m.familyRole === 'child'));

	function addMember(role: FamilyRole): void {
		const isFirstParent = role === 'parent' && parents.length === 0;
		registrationSessionStore.addMember({
			firstName: '',
			middleName: '',
			lastName: '',
			dateOfBirth: '',
			gender: '',
			phone: '',
			email: '',
			isHeadOfHousehold: isFirstParent,
			livesInHousehold: true,
			familyRole: role,
			sacraments: [],
			relationships: []
		});
	}

	function removeMember(tempId: string): void {
		const member = members.find((m) => m.tempId === tempId);
		registrationSessionStore.removeMember(tempId);
		delete validationErrors[tempId];

		if (member?.isHeadOfHousehold) {
			const remainingParents = members.filter(
				(m) => m.tempId !== tempId && m.familyRole === 'parent'
			);
			if (remainingParents.length > 0) {
				registrationSessionStore.updateMember(remainingParents[0].tempId, {
					isHeadOfHousehold: true
				});
			}
		}
	}

	function validateEmail(email: string): boolean {
		if (!email) return true;
		const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
		return emailRegex.test(email);
	}

	export function isValid(): boolean {
		if (parents.length === 0) return false;

		const newErrors: Record<string, string[]> = {};
		let allValid = true;

		for (const member of members) {
			const memberErrors: string[] = [];
			if (!member.firstName.trim()) memberErrors.push('First name is required');
			if (!member.lastName.trim()) memberErrors.push('Last name is required');
			if (member.email && !validateEmail(member.email)) memberErrors.push('Invalid email address');
			if (memberErrors.length > 0) {
				newErrors[member.tempId] = memberErrors;
				allValid = false;
			}
		}

		validationErrors = newErrors;
		return allValid;
	}
</script>

<div class="space-y-6">
	<p class="text-gray-600">
		Add the parents or guardians first, then add any children. Relationships between family members
		will be set up automatically in the next step.
	</p>

	<!-- Parents Section -->
	<div>
		<h3 class="text-sm font-semibold text-gray-700 uppercase tracking-wide mb-3">
			Parents / Guardians
		</h3>

		{#if parents.length === 0}
			<div class="text-center py-6 border-2 border-dashed border-gray-300 rounded-lg mb-3">
				<svg
					class="mx-auto h-10 w-10 text-gray-400"
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
				<p class="mt-2 text-sm text-gray-500">No parents added yet</p>
			</div>
		{/if}

		{#each parents as member (member.tempId)}
			<div class="mb-3">
				<MemberCard
					{member}
					onremove={() => removeMember(member.tempId)}
					externalErrors={validationErrors[member.tempId] || []}
				/>
			</div>
		{/each}

		<button
			type="button"
			onclick={() => addMember('parent')}
			disabled={parents.length >= 2}
			class="w-full py-3 px-4 border-2 border-dashed border-gray-300 rounded-lg text-gray-600 hover:border-blue-400 hover:text-blue-600 focus:outline-none focus:ring-2 focus:ring-blue-500 transition-colors disabled:opacity-40 disabled:cursor-not-allowed disabled:hover:border-gray-300 disabled:hover:text-gray-600"
		>
			<span class="flex items-center justify-center gap-2">
				<svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
					<path
						stroke-linecap="round"
						stroke-linejoin="round"
						stroke-width="2"
						d="M12 6v6m0 0v6m0-6h6m-6 0H6"
					/>
				</svg>
				{parents.length >= 2 ? 'Maximum 2 parents reached' : 'Add Parent / Guardian'}
			</span>
		</button>
	</div>

	<!-- Children Section -->
	{#if parents.length > 0}
		<div>
			<h3 class="text-sm font-semibold text-gray-700 uppercase tracking-wide mb-3">Children</h3>

			{#if children.length === 0}
				<div class="text-center py-6 border-2 border-dashed border-gray-300 rounded-lg mb-3">
					<svg
						class="mx-auto h-10 w-10 text-gray-400"
						fill="none"
						stroke="currentColor"
						viewBox="0 0 24 24"
					>
						<path
							stroke-linecap="round"
							stroke-linejoin="round"
							stroke-width="2"
							d="M17 20h5v-2a3 3 0 00-5.356-1.857M17 20H7m10 0v-2c0-.656-.126-1.283-.356-1.857M7 20H2v-2a3 3 0 015.356-1.857M7 20v-2c0-.656.126-1.283.356-1.857m0 0a5.002 5.002 0 019.288 0M15 7a3 3 0 11-6 0 3 3 0 016 0zm6 3a2 2 0 11-4 0 2 2 0 014 0zM7 10a2 2 0 11-4 0 2 2 0 014 0z"
						/>
					</svg>
					<p class="mt-2 text-sm text-gray-500">No children added yet</p>
					<p class="text-xs text-gray-400">Relationships to parents will be set up automatically</p>
				</div>
			{/if}

			{#each children as member (member.tempId)}
				<div class="mb-3">
					<MemberCard
						{member}
						onremove={() => removeMember(member.tempId)}
						externalErrors={validationErrors[member.tempId] || []}
					/>
				</div>
			{/each}

			<button
				type="button"
				onclick={() => addMember('child')}
				class="w-full py-3 px-4 border-2 border-dashed border-gray-300 rounded-lg text-gray-600 hover:border-blue-400 hover:text-blue-600 focus:outline-none focus:ring-2 focus:ring-blue-500 transition-colors"
			>
				<span class="flex items-center justify-center gap-2">
					<svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
						<path
							stroke-linecap="round"
							stroke-linejoin="round"
							stroke-width="2"
							d="M12 6v6m0 0v6m0-6h6m-6 0H6"
						/>
					</svg>
					Add Child
				</span>
			</button>
		</div>
	{/if}

	{#if parents.length === 0 && members.length > 0}
		<p class="text-sm text-amber-600 flex items-center gap-1">
			<svg class="w-4 h-4" fill="currentColor" viewBox="0 0 20 20">
				<path
					fill-rule="evenodd"
					d="M8.257 3.099c.765-1.36 2.722-1.36 3.486 0l5.58 9.92c.75 1.334-.213 2.98-1.742 2.98H4.42c-1.53 0-2.493-1.646-1.743-2.98l5.58-9.92zM11 13a1 1 0 11-2 0 1 1 0 012 0zm-1-8a1 1 0 00-1 1v3a1 1 0 002 0V6a1 1 0 00-1-1z"
					clip-rule="evenodd"
				/>
			</svg>
			At least one parent or guardian is required.
		</p>
	{/if}
</div>
