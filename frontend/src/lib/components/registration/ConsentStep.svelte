<script lang="ts">
	import { registrationSessionStore } from '$lib/stores/registrationSession';
	import { get } from 'svelte/store';

	let consent = $state(get(registrationSessionStore).consent);

	$effect(() => {
		const unsubscribe = registrationSessionStore.subscribe((session) => {
			consent = session.consent;
		});
		return unsubscribe;
	});

	let errors = $state<Record<string, string>>({});

	function validate(): boolean {
		const newErrors: Record<string, string> = {};

		if (!consent.dataPrivacyConsent) {
			newErrors.dataPrivacyConsent = 'Data privacy consent is required to proceed';
		}

		if (!consent.termsAcknowledged) {
			newErrors.termsAcknowledged = 'You must acknowledge the terms to proceed';
		}

		errors = newErrors;
		return Object.keys(newErrors).length === 0;
	}

	function handleToggle(field: string, checked: boolean): void {
		const update: Record<string, boolean | string> = { [field]: checked };

		if (
			(field === 'dataPrivacyConsent' || field === 'termsAcknowledged') &&
			checked &&
			!consent.consentedAt
		) {
			update.consentedAt = new Date().toISOString();
		}

		registrationSessionStore.updateConsent(update);

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
		<h2 class="text-lg font-semibold text-gray-800">Consent & Preferences</h2>
		<p class="mt-1 text-sm text-gray-500">
			Please review and provide your consent for the following items.
		</p>
	</div>

	<!-- Data Privacy Consent (required) -->
	<div class="rounded-md border border-gray-200 p-4">
		<label class="flex items-start gap-3 cursor-pointer">
			<input
				type="checkbox"
				checked={consent.dataPrivacyConsent}
				onchange={(e) => handleToggle('dataPrivacyConsent', e.currentTarget.checked)}
				class="mt-1 h-4 w-4 rounded border-gray-300 text-blue-600 focus:ring-blue-500"
			/>
			<div>
				<span class="text-sm font-medium text-gray-700">
					Data Privacy Consent <span class="text-red-500">*</span>
				</span>
				<p class="mt-1 text-sm text-gray-500">
					I consent to the parish storing and processing my personal data for parish administration
					purposes. This includes names, contact information, sacramental records, and family
					relationships provided in this registration.
				</p>
			</div>
		</label>
		{#if errors.dataPrivacyConsent}
			<p class="mt-1 text-sm text-red-600">{errors.dataPrivacyConsent}</p>
		{/if}
	</div>

	<!-- Photo/Media Release (optional) -->
	<div class="rounded-md border border-gray-200 p-4">
		<label class="flex items-start gap-3 cursor-pointer">
			<input
				type="checkbox"
				checked={consent.photoMediaRelease}
				onchange={(e) => handleToggle('photoMediaRelease', e.currentTarget.checked)}
				class="mt-1 h-4 w-4 rounded border-gray-300 text-blue-600 focus:ring-blue-500"
			/>
			<div>
				<span class="text-sm font-medium text-gray-700">Photo/Media Release</span>
				<p class="mt-1 text-sm text-gray-500">
					I consent to photos and videos of myself and my family being used in parish
					communications, newsletters, website, and social media.
				</p>
			</div>
		</label>
	</div>

	<!-- Communication Preferences (optional) -->
	<div class="border-t border-gray-200 pt-4">
		<h3 class="text-sm font-medium text-gray-700 mb-3">Communication Preferences</h3>
		<p class="text-sm text-gray-500 mb-3">
			Select how you would like to receive communications from the parish.
		</p>
		<div class="space-y-3">
			<label class="flex items-center gap-3 cursor-pointer">
				<input
					type="checkbox"
					checked={consent.commEmail}
					onchange={(e) => handleToggle('commEmail', e.currentTarget.checked)}
					class="h-4 w-4 rounded border-gray-300 text-blue-600 focus:ring-blue-500"
				/>
				<span class="text-sm text-gray-700">Email communications (newsletter, announcements)</span>
			</label>
			<label class="flex items-center gap-3 cursor-pointer">
				<input
					type="checkbox"
					checked={consent.commSms}
					onchange={(e) => handleToggle('commSms', e.currentTarget.checked)}
					class="h-4 w-4 rounded border-gray-300 text-blue-600 focus:ring-blue-500"
				/>
				<span class="text-sm text-gray-700">SMS/text communications</span>
			</label>
			<label class="flex items-center gap-3 cursor-pointer">
				<input
					type="checkbox"
					checked={consent.commPhone}
					onchange={(e) => handleToggle('commPhone', e.currentTarget.checked)}
					class="h-4 w-4 rounded border-gray-300 text-blue-600 focus:ring-blue-500"
				/>
				<span class="text-sm text-gray-700">Phone call communications</span>
			</label>
		</div>
	</div>

	<!-- Terms Acknowledgment (required) -->
	<div class="rounded-md border border-gray-200 p-4">
		<label class="flex items-start gap-3 cursor-pointer">
			<input
				type="checkbox"
				checked={consent.termsAcknowledged}
				onchange={(e) => handleToggle('termsAcknowledged', e.currentTarget.checked)}
				class="mt-1 h-4 w-4 rounded border-gray-300 text-blue-600 focus:ring-blue-500"
			/>
			<div>
				<span class="text-sm font-medium text-gray-700">
					Terms Acknowledgment <span class="text-red-500">*</span>
				</span>
				<p class="mt-1 text-sm text-gray-500">
					I confirm that the information provided in this registration is accurate and complete to
					the best of my knowledge.
				</p>
			</div>
		</label>
		{#if errors.termsAcknowledged}
			<p class="mt-1 text-sm text-red-600">{errors.termsAcknowledged}</p>
		{/if}
	</div>
</div>
