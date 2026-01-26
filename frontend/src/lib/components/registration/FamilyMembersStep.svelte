<script lang="ts">
	import { registrationSessionStore } from '$lib/stores/registrationSession';
	import MemberCard from './MemberCard.svelte';

	let members = $derived($registrationSessionStore.members);
	let validationErrors = $state<Record<string, string[]>>({});

	function addMember(): void {
		registrationSessionStore.addMember({
			firstName: '',
			middleName: '',
			lastName: '',
			dateOfBirth: '',
			gender: '',
			phone: '',
			email: '',
			isHeadOfHousehold: members.length === 0,
			sacraments: [],
			relationships: []
		});
	}

	function removeMember(tempId: string): void {
		registrationSessionStore.removeMember(tempId);
		delete validationErrors[tempId];
	}

	function validateEmail(email: string): boolean {
		if (!email) return true;
		const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
		return emailRegex.test(email);
	}

	export function isValid(): boolean {
		if (members.length === 0) {
			return false;
		}

		const newErrors: Record<string, string[]> = {};
		let allValid = true;

		for (const member of members) {
			const memberErrors: string[] = [];

			if (!member.firstName.trim()) {
				memberErrors.push('First name is required');
			}

			if (!member.lastName.trim()) {
				memberErrors.push('Last name is required');
			}

			if (member.email && !validateEmail(member.email)) {
				memberErrors.push('Invalid email address');
			}

			if (memberErrors.length > 0) {
				newErrors[member.tempId] = memberErrors;
				allValid = false;
			}
		}

		validationErrors = newErrors;

		const hasHead = members.some((m) => m.isHeadOfHousehold);
		if (!hasHead) {
			allValid = false;
		}

		return allValid;
	}
</script>

<div class="space-y-4">
	<p class="text-gray-600">
		Add each family member who will be part of this household. At least one member must be
		designated as the head of household.
	</p>

	{#if members.length === 0}
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
					d="M17 20h5v-2a3 3 0 00-5.356-1.857M17 20H7m10 0v-2c0-.656-.126-1.283-.356-1.857M7 20H2v-2a3 3 0 015.356-1.857M7 20v-2c0-.656.126-1.283.356-1.857m0 0a5.002 5.002 0 019.288 0M15 7a3 3 0 11-6 0 3 3 0 016 0zm6 3a2 2 0 11-4 0 2 2 0 014 0zM7 10a2 2 0 11-4 0 2 2 0 014 0z"
				/>
			</svg>
			<p class="mt-2 text-sm text-gray-500">No family members added yet</p>
			<p class="text-xs text-gray-400">Click the button below to add your first family member</p>
		</div>
	{/if}

	{#each members as member (member.tempId)}
		<MemberCard
			{member}
			onremove={() => removeMember(member.tempId)}
			externalErrors={validationErrors[member.tempId] || []}
		/>
	{/each}

	<button
		type="button"
		onclick={addMember}
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
			Add Family Member
		</span>
	</button>

	{#if members.length > 0 && !members.some((m) => m.isHeadOfHousehold)}
		<p class="text-sm text-amber-600 flex items-center gap-1">
			<svg class="w-4 h-4" fill="currentColor" viewBox="0 0 20 20">
				<path
					fill-rule="evenodd"
					d="M8.257 3.099c.765-1.36 2.722-1.36 3.486 0l5.58 9.92c.75 1.334-.213 2.98-1.742 2.98H4.42c-1.53 0-2.493-1.646-1.743-2.98l5.58-9.92zM11 13a1 1 0 11-2 0 1 1 0 012 0zm-1-8a1 1 0 00-1 1v3a1 1 0 002 0V6a1 1 0 00-1-1z"
					clip-rule="evenodd"
				/>
			</svg>
			Please designate one member as the head of household
		</p>
	{/if}
</div>
