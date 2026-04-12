<script lang="ts">
	import { registrationSessionStore } from '$lib/stores/registrationSession';
	import type {
		RegistrationSession,
		RegistrationMember,
		RegistrationType
	} from '$lib/stores/registrationSession';
	import { registrationApi } from '$lib/api';
	import { createEventDispatcher } from 'svelte';
	import { get } from 'svelte/store';

	const dispatch = createEventDispatcher<{ complete: void; goToStep: number }>();

	let session = $state<RegistrationSession>(get(registrationSessionStore));
	let registrationType = $state<RegistrationType>(get(registrationSessionStore).registrationType);
	let submitting = $state(false);
	let error = $state('');
	let submitted = $state(false);

	$effect(() => {
		const unsubscribe = registrationSessionStore.subscribe((s) => {
			session = s;
			registrationType = s.registrationType;
		});
		return unsubscribe;
	});

	let allRelationships = $derived(
		session.members.flatMap((m) =>
			m.relationships.map((r) => ({
				from: m,
				to: getMemberByTempId(r.targetTempId),
				type: r.relationshipType
			}))
		)
	);

	let membersWithSacraments = $derived(session.members.filter((m) => m.sacraments.length > 0));

	const sacramentLabels: Record<string, string> = {
		baptism: 'Baptism',
		first_communion: 'First Communion',
		confirmation: 'Confirmation',
		marriage: 'Marriage',
		holy_orders: 'Holy Orders',
		anointing: 'Anointing of the Sick'
	};

	const relationshipLabels: Record<string, string> = {
		parent: 'Parent',
		child: 'Child',
		spouse: 'Spouse',
		sibling: 'Sibling'
	};

	function getMemberName(member: RegistrationMember): string {
		return `${member.firstName} ${member.lastName}`.trim() || 'Unnamed Member';
	}

	function getMemberByTempId(tempId: string): RegistrationMember | undefined {
		return session.members.find((m) => m.tempId === tempId);
	}

	function formatDate(date: string): string {
		if (!date) return '';
		return new Date(date).toLocaleDateString('en-NZ', {
			year: 'numeric',
			month: 'short',
			day: 'numeric'
		});
	}

	function formatGender(gender: string): string {
		const labels: Record<string, string> = {
			male: 'Male',
			female: 'Female'
		};
		return labels[gender] || gender;
	}

	function goToStep(step: number): void {
		dispatch('goToStep', step);
	}

	async function handleSubmit(): Promise<void> {
		submitting = true;
		error = '';
		try {
			if (registrationType === 'individual') {
				await registrationApi.submitIndividual(session);
			} else {
				await registrationApi.submit(session);
			}
			registrationSessionStore.clearSession();
			submitted = true;
			dispatch('complete');
		} catch (e) {
			const raw = e instanceof Error ? e.message : '';
			// Never show raw/technical errors to the user
			if (raw && !raw.includes('<') && !raw.includes('token') && !raw.includes('JSON')) {
				error = raw;
			} else {
				error =
					'Unable to submit your registration right now. Please try again later or contact the parish office.';
			}
		} finally {
			submitting = false;
		}
	}
</script>

{#if submitted}
	<div class="text-center py-12">
		<div
			class="mx-auto w-16 h-16 bg-brand-success/10 rounded-full flex items-center justify-center mb-4"
		>
			<svg class="w-8 h-8 text-brand-success" fill="none" stroke="currentColor" viewBox="0 0 24 24">
				<path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M5 13l4 4L19 7" />
			</svg>
		</div>
		<h2 class="text-2xl font-bold text-brand-primary mb-2">Registration Submitted!</h2>
		<p class="text-brand-text-secondary">
			Thank you for registering with our chaplaincy. We will review your information and contact you
			shortly.
		</p>
	</div>
{:else}
	<div class="space-y-6">
		<div class="text-center mb-6">
			<h2 class="text-xl font-semibold text-brand-primary">Review Your Information</h2>
			<p class="text-brand-text-secondary mt-1">Please review all details before submitting.</p>
		</div>

		{#if registrationType === 'household'}
			<!-- Household Summary -->
			<div class="border rounded-lg overflow-hidden">
				<div class="bg-brand-bg-subtle px-4 py-3 flex items-center justify-between border-b">
					<h3 class="font-medium text-brand-primary">Household Information</h3>
					<button
						type="button"
						onclick={() => goToStep(1)}
						class="text-sm text-brand-accent hover:text-brand-accent/80 flex items-center gap-1"
					>
						<svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
							<path
								stroke-linecap="round"
								stroke-linejoin="round"
								stroke-width="2"
								d="M11 5H6a2 2 0 00-2 2v11a2 2 0 002 2h11a2 2 0 002-2v-5m-1.414-9.414a2 2 0 112.828 2.828L11.828 15H9v-2.828l8.586-8.586z"
							/>
						</svg>
						Edit
					</button>
				</div>
				<div class="p-4">
					<dl class="grid grid-cols-1 sm:grid-cols-2 gap-x-4 gap-y-2">
						<div>
							<dt class="text-sm text-brand-text-muted">Household Name</dt>
							<dd class="text-sm font-medium text-brand-primary">
								{session.household.name || '—'}
							</dd>
						</div>
						<div>
							<dt class="text-sm text-brand-text-muted">Address</dt>
							<dd class="text-sm font-medium text-brand-primary">
								{#if session.household.address}
									{session.household.address}
									{#if session.household.city}, {session.household.city}{/if}
									{#if session.household.state}, {session.household.state}{/if}
									{#if session.household.zipCode}
										{session.household.zipCode}{/if}
								{:else}
									—
								{/if}
							</dd>
						</div>
						{#if session.household.phone}
							<div>
								<dt class="text-sm text-brand-text-muted">Phone</dt>
								<dd class="text-sm font-medium text-brand-primary">{session.household.phone}</dd>
							</div>
						{/if}
						{#if session.household.email}
							<div>
								<dt class="text-sm text-brand-text-muted">Email</dt>
								<dd class="text-sm font-medium text-brand-primary">{session.household.email}</dd>
							</div>
						{/if}
						{#if session.household.attendingSince}
							<div>
								<dt class="text-sm text-brand-text-muted">Attending Since</dt>
								<dd class="text-sm font-medium text-brand-primary">
									{formatDate(session.household.attendingSince)}
								</dd>
							</div>
						{/if}
					</dl>
				</div>
			</div>
		{/if}

		<!-- Family Members / Individual Info Summary -->
		<div class="border rounded-lg overflow-hidden">
			<div class="bg-brand-bg-subtle px-4 py-3 flex items-center justify-between border-b">
				<h3 class="font-medium text-brand-primary">
					{registrationType === 'individual'
						? 'Your Information'
						: `Family Members (${session.members.length})`}
				</h3>
				<button
					type="button"
					onclick={() => goToStep(registrationType === 'individual' ? 1 : 2)}
					class="text-sm text-brand-accent hover:text-brand-accent/80 flex items-center gap-1"
				>
					<svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
						<path
							stroke-linecap="round"
							stroke-linejoin="round"
							stroke-width="2"
							d="M11 5H6a2 2 0 00-2 2v11a2 2 0 002 2h11a2 2 0 002-2v-5m-1.414-9.414a2 2 0 112.828 2.828L11.828 15H9v-2.828l8.586-8.586z"
						/>
					</svg>
					Edit
				</button>
			</div>
			<div class="p-4">
				{#if session.members.length === 0}
					<p class="text-sm text-brand-text-muted italic">No family members added.</p>
				{:else}
					{@const parents = session.members.filter((m) => m.familyRole === 'parent')}
					{@const children = session.members.filter((m) => m.familyRole === 'child')}

					{#if registrationType === 'household' && (parents.length > 0 || children.length > 0)}
						{#if parents.length > 0}
							<div class="mb-4">
								<h4
									class="text-xs font-semibold text-brand-text-muted uppercase tracking-wide mb-2"
								>
									Parents / Guardians
								</h4>
								<div class="space-y-3">
									{#each parents as member}
										<div class="flex items-start gap-3 p-3 bg-brand-bg-subtle rounded-lg">
											<div
												class="flex-shrink-0 w-10 h-10 bg-brand-accent/10 rounded-full flex items-center justify-center"
											>
												<span class="text-brand-accent font-medium">
													{member.firstName.charAt(0)}{member.lastName.charAt(0)}
												</span>
											</div>
											<div class="flex-1 min-w-0">
												<div class="flex items-center gap-2">
													<p class="text-sm font-medium text-brand-primary">
														{getMemberName(member)}
													</p>
													{#if member.isHeadOfHousehold}
														<span
															class="text-xs bg-brand-accent/10 text-brand-primary px-2 py-0.5 rounded-full"
															>Head</span
														>
													{/if}
												</div>
												<p class="text-sm text-brand-text-muted">
													{#if member.dateOfBirth}{formatDate(member.dateOfBirth)}{/if}
													{#if member.dateOfBirth && member.gender}·{/if}
													{#if member.gender}{formatGender(member.gender)}{/if}
												</p>
												{#if member.email || member.phone}
													<p class="text-sm text-brand-text-muted">
														{member.email || ''}{member.email && member.phone
															? ' · '
															: ''}{member.phone || ''}
													</p>
												{/if}
											</div>
										</div>
									{/each}
								</div>
							</div>
						{/if}

						{#if children.length > 0}
							<div>
								<h4
									class="text-xs font-semibold text-brand-text-muted uppercase tracking-wide mb-2"
								>
									Children
								</h4>
								<div class="space-y-3">
									{#each children as member}
										<div class="flex items-start gap-3 p-3 bg-brand-bg-subtle rounded-lg">
											<div
												class="flex-shrink-0 w-10 h-10 bg-brand-accent/10 rounded-full flex items-center justify-center"
											>
												<span class="text-brand-accent font-medium">
													{member.firstName.charAt(0)}{member.lastName.charAt(0)}
												</span>
											</div>
											<div class="flex-1 min-w-0">
												<div class="flex items-center gap-2">
													<p class="text-sm font-medium text-brand-primary">
														{getMemberName(member)}
													</p>
													{#if !member.livesInHousehold}
														<span
															class="text-xs bg-amber-100 text-amber-800 px-2 py-0.5 rounded-full"
															>Not in household</span
														>
													{/if}
												</div>
												<p class="text-sm text-brand-text-muted">
													{#if member.dateOfBirth}{formatDate(member.dateOfBirth)}{/if}
													{#if member.dateOfBirth && member.gender}·{/if}
													{#if member.gender}{formatGender(member.gender)}{/if}
												</p>
												{#if member.email || member.phone}
													<p class="text-sm text-brand-text-muted">
														{member.email || ''}{member.email && member.phone
															? ' · '
															: ''}{member.phone || ''}
													</p>
												{/if}
											</div>
										</div>
									{/each}
								</div>
							</div>
						{/if}
					{:else}
						<div class="space-y-3">
							{#each session.members as member}
								<div class="flex items-start gap-3 p-3 bg-brand-bg-subtle rounded-lg">
									<div
										class="flex-shrink-0 w-10 h-10 bg-brand-accent/10 rounded-full flex items-center justify-center"
									>
										<span class="text-brand-accent font-medium">
											{member.firstName.charAt(0)}{member.lastName.charAt(0)}
										</span>
									</div>
									<div class="flex-1 min-w-0">
										<div class="flex items-center gap-2">
											<p class="text-sm font-medium text-brand-primary">
												{getMemberName(member)}
											</p>
										</div>
										<p class="text-sm text-brand-text-muted">
											{#if member.dateOfBirth}{formatDate(member.dateOfBirth)}{/if}
											{#if member.dateOfBirth && member.gender}·{/if}
											{#if member.gender}{formatGender(member.gender)}{/if}
										</p>
										{#if member.email || member.phone}
											<p class="text-sm text-brand-text-muted">
												{member.email || ''}{member.email && member.phone
													? ' · '
													: ''}{member.phone || ''}
											</p>
										{/if}
									</div>
								</div>
							{/each}
						</div>
					{/if}
				{/if}
			</div>
		</div>

		{#if registrationType === 'household'}
			<!-- Relationships Summary -->
			<div class="border rounded-lg overflow-hidden">
				<div class="bg-brand-bg-subtle px-4 py-3 flex items-center justify-between border-b">
					<h3 class="font-medium text-brand-primary">Family Relationships</h3>
					<button
						type="button"
						onclick={() => goToStep(3)}
						class="text-sm text-brand-accent hover:text-brand-accent/80 flex items-center gap-1"
					>
						<svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
							<path
								stroke-linecap="round"
								stroke-linejoin="round"
								stroke-width="2"
								d="M11 5H6a2 2 0 00-2 2v11a2 2 0 002 2h11a2 2 0 002-2v-5m-1.414-9.414a2 2 0 112.828 2.828L11.828 15H9v-2.828l8.586-8.586z"
							/>
						</svg>
						Edit
					</button>
				</div>
				<div class="p-4">
					{#if allRelationships.length === 0}
						<p class="text-sm text-brand-text-muted italic">No relationships defined.</p>
					{:else}
						<ul class="space-y-2">
							{#each allRelationships as rel}
								{#if rel.to}
									<li class="text-sm text-gray-700">
										<span class="font-medium">{getMemberName(rel.from)}</span>
										<span class="text-brand-text-muted"> is </span>
										<span class="font-medium text-brand-accent"
											>{relationshipLabels[rel.type] || rel.type}</span
										>
										<span class="text-brand-text-muted"> of </span>
										<span class="font-medium">{getMemberName(rel.to)}</span>
									</li>
								{/if}
							{/each}
						</ul>
					{/if}
				</div>
			</div>
		{/if}

		<!-- Sacraments Summary -->
		<div class="border rounded-lg overflow-hidden">
			<div class="bg-brand-bg-subtle px-4 py-3 flex items-center justify-between border-b">
				<h3 class="font-medium text-brand-primary">Sacraments</h3>
				<button
					type="button"
					onclick={() => goToStep(registrationType === 'individual' ? 2 : 4)}
					class="text-sm text-brand-accent hover:text-brand-accent/80 flex items-center gap-1"
				>
					<svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
						<path
							stroke-linecap="round"
							stroke-linejoin="round"
							stroke-width="2"
							d="M11 5H6a2 2 0 00-2 2v11a2 2 0 002 2h11a2 2 0 002-2v-5m-1.414-9.414a2 2 0 112.828 2.828L11.828 15H9v-2.828l8.586-8.586z"
						/>
					</svg>
					Edit
				</button>
			</div>
			<div class="p-4">
				{#if membersWithSacraments.length === 0}
					<p class="text-sm text-brand-text-muted italic">No sacraments recorded.</p>
				{:else}
					<div class="space-y-4">
						{#each membersWithSacraments as member}
							<div>
								<p class="text-sm font-medium text-brand-primary mb-2">{getMemberName(member)}</p>
								<div class="flex flex-wrap gap-2">
									{#each member.sacraments as sacrament}
										<span
											class="inline-flex items-center gap-1 px-2 py-1 bg-gray-100 text-gray-700 rounded text-sm"
										>
											<svg
												class="w-3 h-3 text-brand-success"
												fill="none"
												stroke="currentColor"
												viewBox="0 0 24 24"
											>
												<path
													stroke-linecap="round"
													stroke-linejoin="round"
													stroke-width="2"
													d="M5 13l4 4L19 7"
												/>
											</svg>
											{sacramentLabels[sacrament.type] || sacrament.type}
											{#if sacrament.date}
												<span class="text-brand-text-muted">({formatDate(sacrament.date)})</span>
											{/if}
										</span>
									{/each}
								</div>
							</div>
						{/each}
					</div>
				{/if}
			</div>
		</div>

		<!-- Consent & Preferences Summary -->
		<div class="border rounded-lg overflow-hidden">
			<div class="bg-brand-bg-subtle px-4 py-3 flex items-center justify-between border-b">
				<h3 class="font-medium text-brand-primary">Consent & Preferences</h3>
				<button
					type="button"
					onclick={() => goToStep(registrationType === 'individual' ? 3 : 5)}
					class="text-sm text-brand-accent hover:text-brand-accent/80 flex items-center gap-1"
				>
					<svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
						<path
							stroke-linecap="round"
							stroke-linejoin="round"
							stroke-width="2"
							d="M11 5H6a2 2 0 00-2 2v11a2 2 0 002 2h11a2 2 0 002-2v-5m-1.414-9.414a2 2 0 112.828 2.828L11.828 15H9v-2.828l8.586-8.586z"
						/>
					</svg>
					Edit
				</button>
			</div>
			<div class="p-4">
				<dl class="space-y-2">
					<div class="flex justify-between">
						<dt class="text-sm text-brand-text-muted">Data Privacy</dt>
						<dd
							class="text-sm font-medium {session.consent?.dataPrivacyConsent
								? 'text-brand-success'
								: 'text-brand-error'}"
						>
							{session.consent?.dataPrivacyConsent ? 'Granted' : 'Not granted'}
						</dd>
					</div>
					<div class="flex justify-between">
						<dt class="text-sm text-brand-text-muted">Photo/Media Release</dt>
						<dd class="text-sm font-medium text-brand-primary">
							{session.consent?.photoMediaRelease ? 'Yes' : 'No'}
						</dd>
					</div>
					<div class="flex justify-between">
						<dt class="text-sm text-brand-text-muted">Communication</dt>
						<dd class="text-sm font-medium text-brand-primary">
							{[
								session.consent?.commEmail && 'Email',
								session.consent?.commSms && 'SMS',
								session.consent?.commPhone && 'Phone'
							]
								.filter(Boolean)
								.join(', ') || 'None selected'}
						</dd>
					</div>
					<div class="flex justify-between">
						<dt class="text-sm text-brand-text-muted">Terms Acknowledged</dt>
						<dd
							class="text-sm font-medium {session.consent?.termsAcknowledged
								? 'text-brand-success'
								: 'text-brand-error'}"
						>
							{session.consent?.termsAcknowledged ? 'Yes' : 'No'}
						</dd>
					</div>
				</dl>
			</div>
		</div>

		<!-- Submit Section -->
		<div class="border-t pt-6">
			{#if error}
				<div class="mb-4 p-3 bg-brand-error/10 border-brand-error rounded-lg">
					<p class="text-sm text-brand-error">{error}</p>
				</div>
			{/if}

			<div class="flex items-center justify-end">
				<button
					type="button"
					onclick={handleSubmit}
					disabled={submitting}
					class="inline-flex items-center gap-2 bg-brand-accent text-white px-6 py-2 rounded-lg font-medium hover:bg-brand-accent/90 focus:outline-none focus:ring-2 focus:ring-brand-accent focus:ring-offset-2 disabled:opacity-50 disabled:cursor-not-allowed transition-colors"
				>
					{#if submitting}
						<svg class="animate-spin h-4 w-4" fill="none" viewBox="0 0 24 24">
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
						Submitting...
					{:else}
						Submit Registration
					{/if}
				</button>
			</div>
		</div>
	</div>
{/if}
