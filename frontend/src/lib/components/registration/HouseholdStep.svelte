<script lang="ts">
	import { registrationSessionStore } from '$lib/stores/registrationSession';
	import Tooltip from '$lib/components/Tooltip.svelte';
	import { get } from 'svelte/store';

	let household = $derived(get(registrationSessionStore).household);

	$effect(() => {
		const unsubscribe = registrationSessionStore.subscribe((session) => {
			household = session.household;
		});
		return unsubscribe;
	});

	let errors = $state<Record<string, string>>({});

	function validateEmail(email: string): boolean {
		if (!email) return true;
		const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
		return emailRegex.test(email);
	}

	function validate(): boolean {
		const newErrors: Record<string, string> = {};

		if (!household.name.trim()) {
			newErrors.name = 'Household name is required';
		}

		if (!household.address.trim()) {
			newErrors.address = 'Street address is required';
		}

		if (!household.city.trim()) {
			newErrors.city = 'City is required';
		}

		if (household.email && !validateEmail(household.email)) {
			newErrors.email = 'Please enter a valid email address';
		}

		errors = newErrors;
		return Object.keys(newErrors).length === 0;
	}

	function handleInput(field: string, value: string): void {
		registrationSessionStore.updateHousehold({ [field]: value });
		if (errors[field]) {
			errors = { ...errors, [field]: '' };
		}
	}

	export function isValid(): boolean {
		return validate();
	}
</script>

<div class="space-y-6">
	<div>
		<div class="flex items-center">
			<label for="household-name" class="block text-sm font-medium text-gray-700">
				Household Name <span class="text-red-500">*</span>
			</label>
			<Tooltip text="Usually your family surname, e.g., 'The Smith Family'" />
		</div>
		<input
			id="household-name"
			type="text"
			value={household.name}
			oninput={(e) => handleInput('name', e.currentTarget.value)}
			class="mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-blue-500 focus:ring-blue-500 sm:text-sm
				{errors.name ? 'border-red-500' : ''}"
			placeholder="e.g., The Smith Family"
		/>
		{#if errors.name}
			<p class="mt-1 text-sm text-red-600">{errors.name}</p>
		{/if}
	</div>

	<div>
		<div class="flex items-center">
			<label for="address" class="block text-sm font-medium text-gray-700">
				Street Address <span class="text-red-500">*</span>
			</label>
			<Tooltip text="Your primary residence street address" />
		</div>
		<input
			id="address"
			type="text"
			value={household.address}
			oninput={(e) => handleInput('address', e.currentTarget.value)}
			class="mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-blue-500 focus:ring-blue-500 sm:text-sm
				{errors.address ? 'border-red-500' : ''}"
			placeholder="123 Main Street"
		/>
		{#if errors.address}
			<p class="mt-1 text-sm text-red-600">{errors.address}</p>
		{/if}
	</div>

	<div class="grid grid-cols-1 gap-6 sm:grid-cols-2">
		<div>
			<div class="flex items-center">
				<label for="city" class="block text-sm font-medium text-gray-700">
					City <span class="text-red-500">*</span>
				</label>
				<Tooltip text="City or town name" />
			</div>
			<input
				id="city"
				type="text"
				value={household.city}
				oninput={(e) => handleInput('city', e.currentTarget.value)}
				class="mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-blue-500 focus:ring-blue-500 sm:text-sm
					{errors.city ? 'border-red-500' : ''}"
				placeholder="City"
			/>
			{#if errors.city}
				<p class="mt-1 text-sm text-red-600">{errors.city}</p>
			{/if}
		</div>

		<div>
			<div class="flex items-center">
				<label for="state" class="block text-sm font-medium text-gray-700">
					State/Province
				</label>
				<Tooltip text="State, province, or region" />
			</div>
			<input
				id="state"
				type="text"
				value={household.state}
				oninput={(e) => handleInput('state', e.currentTarget.value)}
				class="mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-blue-500 focus:ring-blue-500 sm:text-sm"
				placeholder="State/Province"
			/>
		</div>
	</div>

	<div class="grid grid-cols-1 gap-6 sm:grid-cols-2">
		<div>
			<div class="flex items-center">
				<label for="zipCode" class="block text-sm font-medium text-gray-700">
					Postal Code
				</label>
				<Tooltip text="ZIP code or postal code" />
			</div>
			<input
				id="zipCode"
				type="text"
				value={household.zipCode}
				oninput={(e) => handleInput('zipCode', e.currentTarget.value)}
				class="mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-blue-500 focus:ring-blue-500 sm:text-sm"
				placeholder="12345"
			/>
		</div>

		<div>
			<div class="flex items-center">
				<label for="phone" class="block text-sm font-medium text-gray-700">
					Phone Number
				</label>
				<Tooltip text="Primary contact number for the household (optional)" />
			</div>
			<input
				id="phone"
				type="tel"
				value={household.phone}
				oninput={(e) => handleInput('phone', e.currentTarget.value)}
				class="mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-blue-500 focus:ring-blue-500 sm:text-sm"
				placeholder="(555) 123-4567"
			/>
		</div>
	</div>

	<div>
		<div class="flex items-center">
			<label for="email" class="block text-sm font-medium text-gray-700">
				Email Address
			</label>
			<Tooltip text="Primary email for household communications (optional)" />
		</div>
		<input
			id="email"
			type="email"
			value={household.email}
			oninput={(e) => handleInput('email', e.currentTarget.value)}
			class="mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-blue-500 focus:ring-blue-500 sm:text-sm
				{errors.email ? 'border-red-500' : ''}"
			placeholder="family@example.com"
		/>
		{#if errors.email}
			<p class="mt-1 text-sm text-red-600">{errors.email}</p>
		{/if}
	</div>
</div>
