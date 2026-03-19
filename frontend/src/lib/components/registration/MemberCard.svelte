<script lang="ts">
	import type { RegistrationMember } from '$lib/stores/registrationSession';
	import { registrationSessionStore } from '$lib/stores/registrationSession';
	import Tooltip from '$lib/components/Tooltip.svelte';

	interface Props {
		member: RegistrationMember;
		onremove: () => void;
		externalErrors?: string[];
	}

	let { member, onremove, externalErrors = [] }: Props = $props();

	let expanded = $state(true);
	let showDeleteConfirm = $state(false);

	$effect(() => {
		if (externalErrors.length > 0) {
			expanded = true;
		}
	});

	function handleInput(field: keyof RegistrationMember, value: string | boolean): void {
		registrationSessionStore.updateMember(member.tempId, { [field]: value });
	}

	function handleHeadOfHousehold(checked: boolean): void {
		if (checked) {
			const session = registrationSessionStore.getSession();
			session.members.forEach((m) => {
				if (m.tempId !== member.tempId && m.isHeadOfHousehold) {
					registrationSessionStore.updateMember(m.tempId, { isHeadOfHousehold: false });
				}
			});
		}
		registrationSessionStore.updateMember(member.tempId, { isHeadOfHousehold: checked });
	}

	function confirmDelete(): void {
		showDeleteConfirm = true;
	}

	function cancelDelete(): void {
		showDeleteConfirm = false;
	}

	function executeDelete(): void {
		showDeleteConfirm = false;
		onremove();
	}

	let displayName = $derived(
		member.firstName || member.lastName
			? `${member.firstName} ${member.lastName}`.trim()
			: 'New Member'
	);
</script>

<div class="border border-gray-200 rounded-lg bg-white shadow-sm">
	<button
		type="button"
		class="w-full px-4 py-3 flex items-center justify-between text-left hover:bg-gray-50 focus:outline-none focus:ring-2 focus:ring-blue-500 focus:ring-inset rounded-t-lg"
		onclick={() => (expanded = !expanded)}
	>
		<div class="flex items-center gap-2">
			<span class="font-medium text-gray-900">{displayName}</span>
			{#if member.isHeadOfHousehold}
				<span
					class="inline-flex items-center px-2 py-0.5 rounded text-xs font-medium bg-blue-100 text-blue-800"
				>
					Head of Household
				</span>
			{/if}
			{#if member.familyRole === 'child' && !member.livesInHousehold}
				<span
					class="inline-flex items-center px-2 py-0.5 rounded text-xs font-medium bg-amber-100 text-amber-800"
				>
					Not in household
				</span>
			{/if}
		</div>
		<svg
			class="w-5 h-5 text-gray-500 transition-transform {expanded ? 'rotate-180' : ''}"
			fill="none"
			stroke="currentColor"
			viewBox="0 0 24 24"
		>
			<path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M19 9l-7 7-7-7" />
		</svg>
	</button>

	{#if expanded}
		<div class="px-4 pb-4 pt-2 border-t border-gray-100 space-y-4">
			<div class="grid grid-cols-1 gap-4 sm:grid-cols-3">
				<div>
					<div class="flex items-center">
						<label for="firstName-{member.tempId}" class="block text-sm font-medium text-gray-700">
							First Name <span class="text-red-500">*</span>
						</label>
						<Tooltip text="Legal first name" />
					</div>
					<input
						id="firstName-{member.tempId}"
						type="text"
						value={member.firstName}
						oninput={(e) => handleInput('firstName', e.currentTarget.value)}
						class="mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-blue-500 focus:ring-blue-500 sm:text-sm"
						placeholder="First name"
					/>
				</div>

				<div>
					<div class="flex items-center">
						<label for="middleName-{member.tempId}" class="block text-sm font-medium text-gray-700">
							Middle Name
						</label>
						<Tooltip text="Middle name (optional)" />
					</div>
					<input
						id="middleName-{member.tempId}"
						type="text"
						value={member.middleName}
						oninput={(e) => handleInput('middleName', e.currentTarget.value)}
						class="mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-blue-500 focus:ring-blue-500 sm:text-sm"
						placeholder="Middle name"
					/>
				</div>

				<div>
					<div class="flex items-center">
						<label for="lastName-{member.tempId}" class="block text-sm font-medium text-gray-700">
							Last Name <span class="text-red-500">*</span>
						</label>
						<Tooltip text="Legal last name / surname" />
					</div>
					<input
						id="lastName-{member.tempId}"
						type="text"
						value={member.lastName}
						oninput={(e) => handleInput('lastName', e.currentTarget.value)}
						class="mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-blue-500 focus:ring-blue-500 sm:text-sm"
						placeholder="Last name"
					/>
				</div>
			</div>

			<div class="grid grid-cols-1 gap-4 sm:grid-cols-2">
				<div>
					<div class="flex items-center">
						<label
							for="dateOfBirth-{member.tempId}"
							class="block text-sm font-medium text-gray-700"
						>
							Date of Birth
						</label>
						<Tooltip text="Used to calculate age and for sacrament eligibility" />
					</div>
					<input
						id="dateOfBirth-{member.tempId}"
						type="date"
						value={member.dateOfBirth}
						oninput={(e) => handleInput('dateOfBirth', e.currentTarget.value)}
						class="mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-blue-500 focus:ring-blue-500 sm:text-sm"
					/>
				</div>

				<div>
					<div class="flex items-center">
						<label for="gender-{member.tempId}" class="block text-sm font-medium text-gray-700">
							Gender
						</label>
						<Tooltip text="Optional demographic information" />
					</div>
					<select
						id="gender-{member.tempId}"
						value={member.gender}
						onchange={(e) => handleInput('gender', e.currentTarget.value)}
						class="mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-blue-500 focus:ring-blue-500 sm:text-sm"
					>
						<option value="">Select gender</option>
						<option value="male">Male</option>
						<option value="female">Female</option>
					</select>
				</div>
			</div>

			<div class="grid grid-cols-1 gap-4 sm:grid-cols-2">
				<div>
					<div class="flex items-center">
						<label for="phone-{member.tempId}" class="block text-sm font-medium text-gray-700">
							Phone Number
						</label>
						<Tooltip text="Personal phone number (optional)" />
					</div>
					<input
						id="phone-{member.tempId}"
						type="tel"
						value={member.phone}
						oninput={(e) => handleInput('phone', e.currentTarget.value)}
						class="mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-blue-500 focus:ring-blue-500 sm:text-sm"
						placeholder="(555) 123-4567"
					/>
				</div>

				<div>
					<div class="flex items-center">
						<label for="email-{member.tempId}" class="block text-sm font-medium text-gray-700">
							Email Address
						</label>
						<Tooltip text="Personal email address (optional)" />
					</div>
					<input
						id="email-{member.tempId}"
						type="email"
						value={member.email}
						oninput={(e) => handleInput('email', e.currentTarget.value)}
						class="mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-blue-500 focus:ring-blue-500 sm:text-sm"
						placeholder="email@example.com"
					/>
				</div>
			</div>

			{#if externalErrors.length > 0}
				<div class="p-3 bg-red-50 border border-red-200 rounded-md">
					<p class="text-sm font-medium text-red-800">Please fix the following:</p>
					<ul class="mt-1 text-sm text-red-600 list-disc list-inside">
						{#each externalErrors as error}
							<li>{error}</li>
						{/each}
					</ul>
				</div>
			{/if}

			<div class="flex items-center justify-between pt-2">
				{#if member.familyRole !== 'child'}
					<label class="flex items-center gap-2 cursor-pointer">
						<input
							type="checkbox"
							checked={member.isHeadOfHousehold}
							onchange={(e) => handleHeadOfHousehold(e.currentTarget.checked)}
							class="rounded border-gray-300 text-blue-600 focus:ring-blue-500"
						/>
						<span class="text-sm text-gray-700">Head of Household</span>
						<Tooltip text="Only one person can be the head of household" />
					</label>
				{:else}
					<label class="flex items-center gap-2 cursor-pointer">
						<input
							type="checkbox"
							checked={member.livesInHousehold}
							onchange={(e) => handleInput('livesInHousehold', e.currentTarget.checked)}
							class="rounded border-gray-300 text-blue-600 focus:ring-blue-500"
						/>
						<span class="text-sm text-gray-700">Lives in household</span>
						<Tooltip text="Uncheck if this child has moved out or lives elsewhere" />
					</label>
				{/if}

				{#if showDeleteConfirm}
					<div class="flex items-center gap-2">
						<span class="text-sm text-gray-600">Remove this member?</span>
						<button
							type="button"
							onclick={executeDelete}
							class="px-3 py-1 text-sm font-medium text-white bg-red-600 rounded hover:bg-red-700 focus:outline-none focus:ring-2 focus:ring-red-500"
						>
							Yes, Remove
						</button>
						<button
							type="button"
							onclick={cancelDelete}
							class="px-3 py-1 text-sm font-medium text-gray-700 bg-gray-100 rounded hover:bg-gray-200 focus:outline-none focus:ring-2 focus:ring-gray-500"
						>
							Cancel
						</button>
					</div>
				{:else}
					<button
						type="button"
						onclick={confirmDelete}
						class="text-sm text-red-600 hover:text-red-800 focus:outline-none focus:underline"
					>
						Remove Member
					</button>
				{/if}
			</div>
		</div>
	{/if}
</div>
