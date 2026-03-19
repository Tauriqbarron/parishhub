<script lang="ts">
	import type { PersonWithRelations, Person, Gender } from '$lib/api';
	import AddressAutocomplete from '$lib/components/AddressAutocomplete.svelte';

	interface Props {
		person: PersonWithRelations;
		isEditing: boolean;
		editForm: Partial<Person>;
	}

	let { person, isEditing, editForm = $bindable() }: Props = $props();

	function calculateAge(dateOfBirth: string | null): number | null {
		if (!dateOfBirth) return null;
		const today = new Date();
		const birthDate = new Date(dateOfBirth);
		let age = today.getFullYear() - birthDate.getFullYear();
		const monthDiff = today.getMonth() - birthDate.getMonth();
		if (monthDiff < 0 || (monthDiff === 0 && today.getDate() < birthDate.getDate())) {
			age--;
		}
		return age;
	}

	function formatDate(date: string | null): string {
		if (!date) return '-';
		return new Date(date).toLocaleDateString('en-NZ', {
			year: 'numeric',
			month: 'long',
			day: 'numeric'
		});
	}

	function formatGender(gender: Gender | null): string {
		if (!gender) return '-';
		return gender.charAt(0).toUpperCase() + gender.slice(1);
	}

	function formatAddress(p: PersonWithRelations): string {
		const parts = [p.address_line1, p.address_line2, p.city, p.postal_code].filter(Boolean);
		return parts.length > 0 ? parts.join(', ') : '-';
	}

	const age = $derived(calculateAge(person.date_of_birth));
</script>

<div class="bg-white rounded-lg shadow">
	<div class="px-6 py-4 border-b border-gray-200">
		<h2 class="text-lg font-medium text-gray-900">Personal Information</h2>
	</div>
	<div class="px-6 py-4">
		{#if isEditing}
			<!-- Edit form -->
			<div class="space-y-4">
				<div class="grid grid-cols-1 sm:grid-cols-3 gap-4">
					<div>
						<label for="first_name" class="block text-sm font-medium text-gray-700">
							First Name *
						</label>
						<input
							type="text"
							id="first_name"
							bind:value={editForm.first_name}
							required
							class="mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-blue-500 focus:ring-blue-500 sm:text-sm"
						/>
					</div>
					<div>
						<label for="middle_name" class="block text-sm font-medium text-gray-700">
							Middle Name
						</label>
						<input
							type="text"
							id="middle_name"
							bind:value={editForm.middle_name}
							class="mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-blue-500 focus:ring-blue-500 sm:text-sm"
						/>
					</div>
					<div>
						<label for="last_name" class="block text-sm font-medium text-gray-700">
							Last Name *
						</label>
						<input
							type="text"
							id="last_name"
							bind:value={editForm.last_name}
							required
							class="mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-blue-500 focus:ring-blue-500 sm:text-sm"
						/>
					</div>
				</div>

				<div class="grid grid-cols-1 sm:grid-cols-2 gap-4">
					<div>
						<label for="date_of_birth" class="block text-sm font-medium text-gray-700">
							Date of Birth
						</label>
						<input
							type="date"
							id="date_of_birth"
							bind:value={editForm.date_of_birth}
							class="mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-blue-500 focus:ring-blue-500 sm:text-sm"
						/>
					</div>
					<div>
						<label for="gender" class="block text-sm font-medium text-gray-700">Gender</label>
						<select
							id="gender"
							bind:value={editForm.gender}
							class="mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-blue-500 focus:ring-blue-500 sm:text-sm"
						>
							<option value={null}>Not specified</option>
							<option value="male">Male</option>
							<option value="female">Female</option>
						</select>
					</div>
				</div>

				<div class="grid grid-cols-1 sm:grid-cols-2 gap-4">
					<div>
						<label for="email" class="block text-sm font-medium text-gray-700">Email</label>
						<input
							type="email"
							id="email"
							bind:value={editForm.email}
							class="mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-blue-500 focus:ring-blue-500 sm:text-sm"
						/>
					</div>
					<div>
						<label for="phone" class="block text-sm font-medium text-gray-700">Phone</label>
						<input
							type="tel"
							id="phone"
							bind:value={editForm.phone}
							class="mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-blue-500 focus:ring-blue-500 sm:text-sm"
						/>
					</div>
				</div>

				<div>
					<label for="address_line1" class="block text-sm font-medium text-gray-700">
						Address Line 1
					</label>
					<AddressAutocomplete
						id="address_line1"
						value={editForm.address_line1 ?? ''}
						onSelect={(address) => {
							editForm.address_line1 = address.address_line1;
							editForm.address_line2 = address.address_line2 || null;
							editForm.city = address.city || null;
							editForm.postal_code = address.postal_code || null;
						}}
						onInput={(val) => (editForm.address_line1 = val || null)}
						placeholder="Start typing an address..."
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

				<div class="grid grid-cols-1 sm:grid-cols-2 gap-4">
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

				<div>
					<label for="notes" class="block text-sm font-medium text-gray-700">Notes</label>
					<textarea
						id="notes"
						bind:value={editForm.notes}
						rows="3"
						class="mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-blue-500 focus:ring-blue-500 sm:text-sm"
					></textarea>
				</div>
			</div>
		{:else}
			<!-- Display mode -->
			<dl class="grid grid-cols-1 sm:grid-cols-2 gap-x-4 gap-y-4">
				<div>
					<dt class="text-sm font-medium text-gray-500">Date of Birth</dt>
					<dd class="mt-1 text-sm text-gray-900">
						{formatDate(person.date_of_birth)}
						{#if age !== null}
							<span class="text-gray-500">(Age {age})</span>
						{/if}
					</dd>
				</div>
				<div>
					<dt class="text-sm font-medium text-gray-500">Gender</dt>
					<dd class="mt-1 text-sm text-gray-900">{formatGender(person.gender)}</dd>
				</div>
				<div>
					<dt class="text-sm font-medium text-gray-500">Email</dt>
					<dd class="mt-1 text-sm text-gray-900">
						{#if person.email}
							<a href="mailto:{person.email}" class="text-blue-600 hover:text-blue-800">
								{person.email}
							</a>
						{:else}
							-
						{/if}
					</dd>
				</div>
				<div>
					<dt class="text-sm font-medium text-gray-500">Phone</dt>
					<dd class="mt-1 text-sm text-gray-900">
						{#if person.phone}
							<a href="tel:{person.phone}" class="text-blue-600 hover:text-blue-800">
								{person.phone}
							</a>
						{:else}
							-
						{/if}
					</dd>
				</div>
				<div class="sm:col-span-2">
					<dt class="text-sm font-medium text-gray-500">Address</dt>
					<dd class="mt-1 text-sm text-gray-900">{formatAddress(person)}</dd>
				</div>
				{#if person.notes}
					<div class="sm:col-span-2">
						<dt class="text-sm font-medium text-gray-500">Notes</dt>
						<dd class="mt-1 text-sm text-gray-900 whitespace-pre-wrap">{person.notes}</dd>
					</div>
				{/if}
			</dl>
		{/if}
	</div>
</div>
