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

	function getHouseholdAddress(p: PersonWithRelations): {
		address: string;
		householdName: string;
	} | null {
		const membership =
			p.household_memberships?.find((m) => m.is_primary_household && m.household) ??
			p.household_memberships?.[0];
		if (!membership?.household) return null;
		const h = membership.household;
		const parts = [h.address_line1, h.address_line2, h.city, h.postal_code].filter(Boolean);
		if (parts.length === 0) return null;
		return { address: parts.join(', '), householdName: h.name };
	}

	function hasPersonAddress(p: PersonWithRelations): boolean {
		return !!(p.address_line1 || p.city || p.postal_code);
	}

	const age = $derived(calculateAge(person.date_of_birth));
</script>

<div class="bg-white rounded-lg shadow">
	<div class="px-6 py-4 border-b border-brand-border">
		<h2 class="text-lg font-medium text-brand-primary">Personal Information</h2>
	</div>
	<div class="px-6 py-4">
		{#if isEditing}
			<!-- Edit form -->
			<div class="space-y-4">
				<div class="grid grid-cols-1 sm:grid-cols-3 gap-4">
					<div>
						<label for="first_name" class="block text-sm font-medium text-brand-primary">
							First Name *
						</label>
						<input
							type="text"
							id="first_name"
							bind:value={editForm.first_name}
							required
							class="mt-1 block w-full rounded-sm border-brand-border shadow-sm focus:border-blue-500 focus:ring-blue-500 sm:text-sm"
						/>
					</div>
					<div>
						<label for="middle_name" class="block text-sm font-medium text-brand-primary">
							Middle Name
						</label>
						<input
							type="text"
							id="middle_name"
							bind:value={editForm.middle_name}
							class="mt-1 block w-full rounded-sm border-brand-border shadow-sm focus:border-blue-500 focus:ring-blue-500 sm:text-sm"
						/>
					</div>
					<div>
						<label for="last_name" class="block text-sm font-medium text-brand-primary">
							Last Name *
						</label>
						<input
							type="text"
							id="last_name"
							bind:value={editForm.last_name}
							required
							class="mt-1 block w-full rounded-sm border-brand-border shadow-sm focus:border-blue-500 focus:ring-blue-500 sm:text-sm"
						/>
					</div>
				</div>

				<div class="grid grid-cols-1 sm:grid-cols-2 gap-4">
					<div>
						<label for="date_of_birth" class="block text-sm font-medium text-brand-primary">
							Date of Birth
						</label>
						<input
							type="date"
							id="date_of_birth"
							bind:value={editForm.date_of_birth}
							class="mt-1 block w-full rounded-sm border-brand-border shadow-sm focus:border-blue-500 focus:ring-blue-500 sm:text-sm"
						/>
					</div>
					<div>
						<label for="gender" class="block text-sm font-medium text-brand-primary">Gender</label>
						<select
							id="gender"
							bind:value={editForm.gender}
							class="mt-1 block w-full rounded-sm border-brand-border shadow-sm focus:border-blue-500 focus:ring-blue-500 sm:text-sm"
						>
							<option value={null}>Not specified</option>
							<option value="male">Male</option>
							<option value="female">Female</option>
						</select>
					</div>
				</div>

				<div class="grid grid-cols-1 sm:grid-cols-2 gap-4">
					<div>
						<label for="email" class="block text-sm font-medium text-brand-primary">Email</label>
						<input
							type="email"
							id="email"
							bind:value={editForm.email}
							class="mt-1 block w-full rounded-sm border-brand-border shadow-sm focus:border-blue-500 focus:ring-blue-500 sm:text-sm"
						/>
					</div>
					<div>
						<label for="phone" class="block text-sm font-medium text-brand-primary">Phone</label>
						<input
							type="tel"
							id="phone"
							bind:value={editForm.phone}
							class="mt-1 block w-full rounded-sm border-brand-border shadow-sm focus:border-blue-500 focus:ring-blue-500 sm:text-sm"
						/>
					</div>
				</div>

				<div>
					<label for="address_line1" class="block text-sm font-medium text-brand-primary">
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
					<label for="address_line2" class="block text-sm font-medium text-brand-primary">
						Address Line 2
					</label>
					<input
						type="text"
						id="address_line2"
						bind:value={editForm.address_line2}
						class="mt-1 block w-full rounded-sm border-brand-border shadow-sm focus:border-blue-500 focus:ring-blue-500 sm:text-sm"
					/>
				</div>

				<div class="grid grid-cols-1 sm:grid-cols-2 gap-4">
					<div>
						<label for="city" class="block text-sm font-medium text-brand-primary">City</label>
						<input
							type="text"
							id="city"
							bind:value={editForm.city}
							class="mt-1 block w-full rounded-sm border-brand-border shadow-sm focus:border-blue-500 focus:ring-blue-500 sm:text-sm"
						/>
					</div>
					<div>
						<label for="postal_code" class="block text-sm font-medium text-brand-primary">
							Postal Code
						</label>
						<input
							type="text"
							id="postal_code"
							bind:value={editForm.postal_code}
							class="mt-1 block w-full rounded-sm border-brand-border shadow-sm focus:border-blue-500 focus:ring-blue-500 sm:text-sm"
						/>
					</div>
				</div>

				<div>
					<label for="notes" class="block text-sm font-medium text-brand-primary">Notes</label>
					<textarea
						id="notes"
						bind:value={editForm.notes}
						rows="3"
						class="mt-1 block w-full rounded-sm border-brand-border shadow-sm focus:border-blue-500 focus:ring-blue-500 sm:text-sm"
					></textarea>
				</div>
			</div>
		{:else}
			<!-- Display mode -->
			<dl class="grid grid-cols-1 sm:grid-cols-2 gap-x-4 gap-y-4">
				<div>
					<dt class="text-sm font-medium text-brand-text-secondary">Date of Birth</dt>
					<dd class="mt-1 text-sm text-brand-primary">
						{formatDate(person.date_of_birth)}
						{#if age !== null}
							<span class="text-brand-text-secondary">(Age {age})</span>
						{/if}
					</dd>
				</div>
				<div>
					<dt class="text-sm font-medium text-brand-text-secondary">Gender</dt>
					<dd class="mt-1 text-sm text-brand-primary">{formatGender(person.gender)}</dd>
				</div>
				<div>
					<dt class="text-sm font-medium text-brand-text-secondary">Email</dt>
					<dd class="mt-1 text-sm text-brand-primary">
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
					<dt class="text-sm font-medium text-brand-text-secondary">Phone</dt>
					<dd class="mt-1 text-sm text-brand-primary">
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
					<dt class="text-sm font-medium text-brand-text-secondary">Address</dt>
					<dd class="mt-1 text-sm text-brand-primary">
						{#if hasPersonAddress(person)}
							{formatAddress(person)}
						{:else if getHouseholdAddress(person)}
							{@const hAddr = getHouseholdAddress(person)!}
							<span class="inline-flex items-center gap-1">
								<svg
									class="w-3.5 h-3.5 text-brand-text-muted"
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
								{hAddr.address}
							</span>
							<span class="text-xs text-brand-text-secondary block mt-0.5"
								>from household: {hAddr.householdName}</span
							>
						{:else}
							-
						{/if}
					</dd>
				</div>
				{#if person.notes}
					<div class="sm:col-span-2">
						<dt class="text-sm font-medium text-brand-text-secondary">Notes</dt>
						<dd class="mt-1 text-sm text-brand-primary whitespace-pre-wrap">{person.notes}</dd>
					</div>
				{/if}
			</dl>
		{/if}
	</div>
</div>
