<script lang="ts">
	import { registrationSessionStore } from '$lib/stores/registrationSession';
	import { get } from 'svelte/store';

	// Initialize from session — individual stores their data as members[0]
	let session = $state(get(registrationSessionStore));

	$effect(() => {
		const unsubscribe = registrationSessionStore.subscribe((s) => {
			session = s;
		});
		return unsubscribe;
	});

	// Get or initialize the individual member (always members[0])
	let member = $derived(
		session.members[0] || {
			firstName: '',
			middleName: '',
			lastName: '',
			dateOfBirth: '',
			gender: '',
			phone: '',
			email: '',
			isHeadOfHousehold: false,
			sacraments: [],
			relationships: []
		}
	);

	let errors = $state<Record<string, string>>({});

	function handleInput(field: string, value: string) {
		if (errors[field]) {
			errors = { ...errors, [field]: '' };
		}

		// Store the individual as members[0]
		const updatedMember = { ...member, [field]: value };

		if (session.members.length === 0) {
			registrationSessionStore.addMember({
				firstName: updatedMember.firstName || '',
				middleName: updatedMember.middleName || '',
				lastName: updatedMember.lastName || '',
				dateOfBirth: updatedMember.dateOfBirth || '',
				gender: updatedMember.gender || '',
				phone: updatedMember.phone || '',
				email: updatedMember.email || '',
				isHeadOfHousehold: false,
				sacraments: updatedMember.sacraments || [],
				relationships: []
			});
		} else {
			registrationSessionStore.updateMember(session.members[0].tempId, { [field]: value });
		}
	}

	export function isValid(): boolean {
		const newErrors: Record<string, string> = {};

		if (!member.firstName?.trim()) {
			newErrors.firstName = 'First name is required';
		}
		if (!member.lastName?.trim()) {
			newErrors.lastName = 'Last name is required';
		}
		if (member.email && !/^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(member.email)) {
			newErrors.email = 'Please enter a valid email address';
		}

		errors = newErrors;
		return Object.keys(newErrors).length === 0;
	}
</script>

<div class="space-y-6">
	<div class="text-center mb-6">
		<h2 class="text-xl font-semibold text-gray-900">Your Information</h2>
		<p class="text-gray-600 mt-1">Please provide your personal details.</p>
	</div>

	<div class="grid grid-cols-1 sm:grid-cols-2 gap-4">
		<div>
			<label for="firstName" class="block text-sm font-medium text-gray-700">
				First Name <span class="text-red-500">*</span>
			</label>
			<input
				id="firstName"
				type="text"
				value={member.firstName || ''}
				oninput={(e) => handleInput('firstName', e.currentTarget.value)}
				class="mt-1 block w-full rounded-md shadow-sm focus:border-blue-500 focus:ring-blue-500 sm:text-sm
					{errors.firstName ? 'border-red-300' : 'border-gray-300'}"
			/>
			{#if errors.firstName}
				<p class="mt-1 text-sm text-red-600">{errors.firstName}</p>
			{/if}
		</div>

		<div>
			<label for="middleName" class="block text-sm font-medium text-gray-700">Middle Name</label>
			<input
				id="middleName"
				type="text"
				value={member.middleName || ''}
				oninput={(e) => handleInput('middleName', e.currentTarget.value)}
				class="mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-blue-500 focus:ring-blue-500 sm:text-sm"
			/>
		</div>

		<div>
			<label for="lastName" class="block text-sm font-medium text-gray-700">
				Last Name <span class="text-red-500">*</span>
			</label>
			<input
				id="lastName"
				type="text"
				value={member.lastName || ''}
				oninput={(e) => handleInput('lastName', e.currentTarget.value)}
				class="mt-1 block w-full rounded-md shadow-sm focus:border-blue-500 focus:ring-blue-500 sm:text-sm
					{errors.lastName ? 'border-red-300' : 'border-gray-300'}"
			/>
			{#if errors.lastName}
				<p class="mt-1 text-sm text-red-600">{errors.lastName}</p>
			{/if}
		</div>

		<div>
			<label for="dateOfBirth" class="block text-sm font-medium text-gray-700">Date of Birth</label>
			<input
				id="dateOfBirth"
				type="date"
				value={member.dateOfBirth || ''}
				oninput={(e) => handleInput('dateOfBirth', e.currentTarget.value)}
				class="mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-blue-500 focus:ring-blue-500 sm:text-sm"
			/>
		</div>

		<div>
			<label for="gender" class="block text-sm font-medium text-gray-700">Gender</label>
			<select
				id="gender"
				value={member.gender || ''}
				onchange={(e) => handleInput('gender', e.currentTarget.value)}
				class="mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-blue-500 focus:ring-blue-500 sm:text-sm"
			>
				<option value="">Select...</option>
				<option value="male">Male</option>
				<option value="female">Female</option>
			</select>
		</div>

		<div>
			<label for="phone" class="block text-sm font-medium text-gray-700">Phone</label>
			<input
				id="phone"
				type="tel"
				value={member.phone || ''}
				oninput={(e) => handleInput('phone', e.currentTarget.value)}
				class="mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-blue-500 focus:ring-blue-500 sm:text-sm"
			/>
		</div>

		<div class="sm:col-span-2">
			<label for="email" class="block text-sm font-medium text-gray-700">Email</label>
			<input
				id="email"
				type="email"
				value={member.email || ''}
				oninput={(e) => handleInput('email', e.currentTarget.value)}
				class="mt-1 block w-full rounded-md shadow-sm focus:border-blue-500 focus:ring-blue-500 sm:text-sm
					{errors.email ? 'border-red-300' : 'border-gray-300'}"
			/>
			{#if errors.email}
				<p class="mt-1 text-sm text-red-600">{errors.email}</p>
			{/if}
		</div>
	</div>
</div>
