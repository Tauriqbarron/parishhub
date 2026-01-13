<script lang="ts">
	import { goto } from '$app/navigation';
	import {
		personApi,
		householdApi,
		type Person,
		type Gender,
		type Household,
		type HouseholdRole,
		type PaginatedResponse
	} from '$lib/api';
	import { toasts } from '$lib/stores/toast';

	// Form state
	let firstName = $state('');
	let lastName = $state('');
	let middleName = $state('');
	let dateOfBirth = $state('');
	let gender = $state<Gender | null>(null);
	let email = $state('');
	let phone = $state('');
	let addressLine1 = $state('');
	let addressLine2 = $state('');
	let city = $state('');
	let postalCode = $state('');
	let notes = $state('');

	// Expanded section state
	let showMoreDetails = $state(false);

	// Household state
	let addToHousehold = $state(false);
	let availableHouseholds = $state<Household[]>([]);
	let selectedHouseholdId = $state<number | null>(null);
	let householdRole = $state<HouseholdRole>('other');
	let loadingHouseholds = $state(false);

	// Form state
	let isSaving = $state(false);
	let errors = $state<Record<string, string>>({});

	const roleLabels: Record<HouseholdRole, string> = {
		head: 'Head',
		spouse: 'Spouse',
		child: 'Child',
		other: 'Other'
	};

	function validateForm(): boolean {
		const newErrors: Record<string, string> = {};

		if (!firstName.trim()) {
			newErrors.first_name = 'First name is required';
		}
		if (!lastName.trim()) {
			newErrors.last_name = 'Last name is required';
		}
		if (email && !/^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(email)) {
			newErrors.email = 'Please enter a valid email address';
		}

		errors = newErrors;
		return Object.keys(newErrors).length === 0;
	}

	function resetForm() {
		firstName = '';
		lastName = '';
		middleName = '';
		dateOfBirth = '';
		gender = null;
		email = '';
		phone = '';
		addressLine1 = '';
		addressLine2 = '';
		city = '';
		postalCode = '';
		notes = '';
		addToHousehold = false;
		selectedHouseholdId = null;
		householdRole = 'other';
		errors = {};
	}

	function getFormData(): Omit<Person, 'id' | 'created_at' | 'updated_at'> {
		return {
			first_name: firstName.trim(),
			last_name: lastName.trim(),
			middle_name: middleName.trim() || null,
			date_of_birth: dateOfBirth || null,
			gender: gender,
			email: email.trim() || null,
			phone: phone.trim() || null,
			address_line1: addressLine1.trim() || null,
			address_line2: addressLine2.trim() || null,
			city: city.trim() || null,
			postal_code: postalCode.trim() || null,
			notes: notes.trim() || null
		};
	}

	async function loadHouseholds() {
		if (availableHouseholds.length > 0) return;

		loadingHouseholds = true;
		try {
			const response: PaginatedResponse<Household> = await householdApi.list();
			availableHouseholds = response.items;
		} catch (err) {
			toasts.error('Failed to load households');
		} finally {
			loadingHouseholds = false;
		}
	}

	function handleAddToHouseholdChange() {
		if (addToHousehold) {
			loadHouseholds();
		}
	}

	function applyHouseholdAddress() {
		if (!selectedHouseholdId) return;

		const household = availableHouseholds.find((h) => h.id === selectedHouseholdId);
		if (household) {
			addressLine1 = household.address_line1 || '';
			addressLine2 = household.address_line2 || '';
			city = household.city || '';
			postalCode = household.postal_code || '';
			if (!showMoreDetails) {
				showMoreDetails = true;
			}
		}
	}

	async function savePerson(): Promise<Person | null> {
		if (!validateForm()) return null;

		isSaving = true;
		try {
			const person = await personApi.create(getFormData());

			// Add to household if selected
			if (addToHousehold && selectedHouseholdId) {
				try {
					await householdApi.addMember(selectedHouseholdId, person.id, householdRole);
				} catch (err) {
					toasts.warning('Person created but failed to add to household');
				}
			}

			return person;
		} catch (err) {
			toasts.error(err instanceof Error ? err.message : 'Failed to create person');
			return null;
		} finally {
			isSaving = false;
		}
	}

	async function handleSaveAndAddAnother() {
		const person = await savePerson();
		if (person) {
			toasts.success(`${person.first_name} ${person.last_name} added successfully`);
			resetForm();
		}
	}

	async function handleSaveAndView() {
		const person = await savePerson();
		if (person) {
			toasts.success(`${person.first_name} ${person.last_name} added successfully`);
			goto(`/people/${person.id}`);
		}
	}

	function handleCancel() {
		goto('/people');
	}

	$effect(() => {
		handleAddToHouseholdChange();
	});
</script>

<div>
	<!-- Back link -->
	<div class="mb-4">
		<a
			href="/people"
			class="inline-flex items-center text-sm text-gray-500 hover:text-gray-700 transition-colors"
		>
			<svg class="w-4 h-4 mr-1" fill="none" stroke="currentColor" viewBox="0 0 24 24">
				<path
					stroke-linecap="round"
					stroke-linejoin="round"
					stroke-width="2"
					d="M15 19l-7-7 7-7"
				/>
			</svg>
			Back to list
		</a>
	</div>

	<!-- Header -->
	<div class="mb-6">
		<h1 class="text-2xl font-bold text-gray-900">Add New Person</h1>
		<p class="text-gray-600 mt-1">Add a new parishioner to the database</p>
	</div>

	<!-- Form -->
	<div class="bg-white rounded-lg shadow">
		<form
			onsubmit={(e) => {
				e.preventDefault();
				handleSaveAndView();
			}}
		>
			<!-- Required Section -->
			<div class="px-6 py-4 border-b border-gray-200">
				<h2 class="text-lg font-medium text-gray-900 mb-4">Basic Information</h2>
				<div class="grid grid-cols-1 sm:grid-cols-2 gap-4">
					<div>
						<label for="first_name" class="block text-sm font-medium text-gray-700">
							First Name <span class="text-red-500">*</span>
						</label>
						<input
							type="text"
							id="first_name"
							bind:value={firstName}
							class="mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-blue-500 focus:ring-blue-500 sm:text-sm {errors.first_name
								? 'border-red-300 focus:border-red-500 focus:ring-red-500'
								: ''}"
							placeholder="Enter first name"
						/>
						{#if errors.first_name}
							<p class="mt-1 text-sm text-red-600">{errors.first_name}</p>
						{/if}
					</div>
					<div>
						<label for="last_name" class="block text-sm font-medium text-gray-700">
							Last Name <span class="text-red-500">*</span>
						</label>
						<input
							type="text"
							id="last_name"
							bind:value={lastName}
							class="mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-blue-500 focus:ring-blue-500 sm:text-sm {errors.last_name
								? 'border-red-300 focus:border-red-500 focus:ring-red-500'
								: ''}"
							placeholder="Enter last name"
						/>
						{#if errors.last_name}
							<p class="mt-1 text-sm text-red-600">{errors.last_name}</p>
						{/if}
					</div>
				</div>

				<!-- Toggle for more details -->
				<button
					type="button"
					onclick={() => (showMoreDetails = !showMoreDetails)}
					class="mt-4 inline-flex items-center text-sm font-medium text-blue-600 hover:text-blue-800 transition-colors"
				>
					<svg
						class="w-4 h-4 mr-1 transform transition-transform {showMoreDetails
							? 'rotate-90'
							: ''}"
						fill="none"
						stroke="currentColor"
						viewBox="0 0 24 24"
					>
						<path
							stroke-linecap="round"
							stroke-linejoin="round"
							stroke-width="2"
							d="M9 5l7 7-7 7"
						/>
					</svg>
					{showMoreDetails ? 'Hide additional details' : 'Add more details'}
				</button>
			</div>

			<!-- Expanded Section -->
			{#if showMoreDetails}
				<div class="px-6 py-4 border-b border-gray-200 bg-gray-50">
					<h3 class="text-md font-medium text-gray-900 mb-4">Additional Details</h3>

					<div class="space-y-4">
						<!-- Middle Name -->
						<div>
							<label for="middle_name" class="block text-sm font-medium text-gray-700">
								Middle Name
							</label>
							<input
								type="text"
								id="middle_name"
								bind:value={middleName}
								class="mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-blue-500 focus:ring-blue-500 sm:text-sm"
								placeholder="Enter middle name"
							/>
						</div>

						<!-- Date of Birth and Gender -->
						<div class="grid grid-cols-1 sm:grid-cols-2 gap-4">
							<div>
								<label for="date_of_birth" class="block text-sm font-medium text-gray-700">
									Date of Birth
								</label>
								<input
									type="date"
									id="date_of_birth"
									bind:value={dateOfBirth}
									class="mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-blue-500 focus:ring-blue-500 sm:text-sm"
								/>
							</div>
							<div>
								<label for="gender" class="block text-sm font-medium text-gray-700">Gender</label>
								<select
									id="gender"
									bind:value={gender}
									class="mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-blue-500 focus:ring-blue-500 sm:text-sm"
								>
									<option value={null}>Select gender...</option>
									<option value="male">Male</option>
									<option value="female">Female</option>
									<option value="other">Other</option>
								</select>
							</div>
						</div>

						<!-- Email and Phone -->
						<div class="grid grid-cols-1 sm:grid-cols-2 gap-4">
							<div>
								<label for="email" class="block text-sm font-medium text-gray-700">Email</label>
								<input
									type="email"
									id="email"
									bind:value={email}
									class="mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-blue-500 focus:ring-blue-500 sm:text-sm {errors.email
										? 'border-red-300 focus:border-red-500 focus:ring-red-500'
										: ''}"
									placeholder="email@example.com"
								/>
								{#if errors.email}
									<p class="mt-1 text-sm text-red-600">{errors.email}</p>
								{/if}
							</div>
							<div>
								<label for="phone" class="block text-sm font-medium text-gray-700">Phone</label>
								<input
									type="tel"
									id="phone"
									bind:value={phone}
									class="mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-blue-500 focus:ring-blue-500 sm:text-sm"
									placeholder="(555) 123-4567"
								/>
							</div>
						</div>

						<!-- Address -->
						<div>
							<label for="address_line1" class="block text-sm font-medium text-gray-700">
								Address Line 1
							</label>
							<input
								type="text"
								id="address_line1"
								bind:value={addressLine1}
								class="mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-blue-500 focus:ring-blue-500 sm:text-sm"
								placeholder="Street address"
							/>
						</div>

						<div>
							<label for="address_line2" class="block text-sm font-medium text-gray-700">
								Address Line 2
							</label>
							<input
								type="text"
								id="address_line2"
								bind:value={addressLine2}
								class="mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-blue-500 focus:ring-blue-500 sm:text-sm"
								placeholder="Apartment, suite, etc."
							/>
						</div>

						<div class="grid grid-cols-1 sm:grid-cols-2 gap-4">
							<div>
								<label for="city" class="block text-sm font-medium text-gray-700">City</label>
								<input
									type="text"
									id="city"
									bind:value={city}
									class="mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-blue-500 focus:ring-blue-500 sm:text-sm"
									placeholder="City"
								/>
							</div>
							<div>
								<label for="postal_code" class="block text-sm font-medium text-gray-700">
									Postal Code
								</label>
								<input
									type="text"
									id="postal_code"
									bind:value={postalCode}
									class="mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-blue-500 focus:ring-blue-500 sm:text-sm"
									placeholder="12345"
								/>
							</div>
						</div>

						<!-- Notes -->
						<div>
							<label for="notes" class="block text-sm font-medium text-gray-700">Notes</label>
							<textarea
								id="notes"
								bind:value={notes}
								rows="3"
								class="mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-blue-500 focus:ring-blue-500 sm:text-sm"
								placeholder="Any additional notes..."
							></textarea>
						</div>
					</div>
				</div>
			{/if}

			<!-- Household Section -->
			<div class="px-6 py-4 border-b border-gray-200">
				<div class="flex items-center">
					<input
						type="checkbox"
						id="add_to_household"
						bind:checked={addToHousehold}
						class="h-4 w-4 rounded border-gray-300 text-blue-600 focus:ring-blue-500"
					/>
					<label for="add_to_household" class="ml-2 block text-sm font-medium text-gray-700">
						Add to existing household
					</label>
				</div>

				{#if addToHousehold}
					<div class="mt-4 p-4 bg-gray-50 rounded-lg border border-gray-200">
						{#if loadingHouseholds}
							<div class="flex items-center justify-center py-4">
								<svg
									class="animate-spin h-5 w-5 text-blue-600"
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
								<span class="ml-2 text-sm text-gray-600">Loading households...</span>
							</div>
						{:else if availableHouseholds.length === 0}
							<p class="text-sm text-gray-500 text-center py-2">
								No households available. You can add to a household later.
							</p>
						{:else}
							<div class="space-y-4">
								<div>
									<label for="household" class="block text-sm font-medium text-gray-700">
										Select Household
									</label>
									<select
										id="household"
										bind:value={selectedHouseholdId}
										class="mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-blue-500 focus:ring-blue-500 sm:text-sm"
									>
										<option value={null}>Choose a household...</option>
										{#each availableHouseholds as household (household.id)}
											<option value={household.id}>{household.name}</option>
										{/each}
									</select>
								</div>

								{#if selectedHouseholdId}
									<div>
										<label for="household_role" class="block text-sm font-medium text-gray-700">
											Role in Household
										</label>
										<select
											id="household_role"
											bind:value={householdRole}
											class="mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-blue-500 focus:ring-blue-500 sm:text-sm"
										>
											{#each Object.entries(roleLabels) as [value, label]}
												<option {value}>{label}</option>
											{/each}
										</select>
									</div>

									<!-- Apply household address button -->
									{@const household = availableHouseholds.find(
										(h) => h.id === selectedHouseholdId
									)}
									{#if household && (household.address_line1 || household.city)}
										<button
											type="button"
											onclick={applyHouseholdAddress}
											class="inline-flex items-center text-sm font-medium text-blue-600 hover:text-blue-800 transition-colors"
										>
											<svg
												class="w-4 h-4 mr-1"
												fill="none"
												stroke="currentColor"
												viewBox="0 0 24 24"
											>
												<path
													stroke-linecap="round"
													stroke-linejoin="round"
													stroke-width="2"
													d="M17.657 16.657L13.414 20.9a1.998 1.998 0 01-2.827 0l-4.244-4.243a8 8 0 1111.314 0z"
												/>
												<path
													stroke-linecap="round"
													stroke-linejoin="round"
													stroke-width="2"
													d="M15 11a3 3 0 11-6 0 3 3 0 016 0z"
												/>
											</svg>
											Use household address
										</button>
									{/if}
								{/if}
							</div>
						{/if}
					</div>
				{/if}
			</div>

			<!-- Actions -->
			<div class="px-6 py-4 bg-gray-50 rounded-b-lg flex flex-col sm:flex-row sm:justify-end gap-3">
				<button
					type="button"
					onclick={handleCancel}
					disabled={isSaving}
					class="inline-flex justify-center items-center px-4 py-2 border border-gray-300 text-sm font-medium rounded-md shadow-sm text-gray-700 bg-white hover:bg-gray-50 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-blue-500 disabled:opacity-50"
				>
					Cancel
				</button>
				<button
					type="button"
					onclick={handleSaveAndAddAnother}
					disabled={isSaving}
					class="inline-flex justify-center items-center px-4 py-2 border border-blue-600 text-sm font-medium rounded-md shadow-sm text-blue-600 bg-white hover:bg-blue-50 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-blue-500 disabled:opacity-50"
				>
					{#if isSaving}
						<svg class="animate-spin -ml-1 mr-2 h-4 w-4 text-blue-600" fill="none" viewBox="0 0 24 24">
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
					{/if}
					Save & Add Another
				</button>
				<button
					type="submit"
					disabled={isSaving}
					class="inline-flex justify-center items-center px-4 py-2 border border-transparent text-sm font-medium rounded-md shadow-sm text-white bg-blue-600 hover:bg-blue-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-blue-500 disabled:opacity-50"
				>
					{#if isSaving}
						<svg class="animate-spin -ml-1 mr-2 h-4 w-4 text-white" fill="none" viewBox="0 0 24 24">
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
					{/if}
					Save & View
				</button>
			</div>
		</form>
	</div>
</div>
