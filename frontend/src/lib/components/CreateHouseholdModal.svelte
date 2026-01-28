<script lang="ts">
	import { householdApi, type HouseholdCreate, type HouseholdWithMembers } from '$lib/api';
	import { toasts } from '$lib/stores/toast';

	interface Props {
		onSave: (household: HouseholdWithMembers) => void;
		onClose: () => void;
	}

	let { onSave, onClose }: Props = $props();

	let isLoading = $state(false);
	let form = $state<HouseholdCreate>({
		name: '',
		address_line1: null,
		address_line2: null,
		city: null,
		postal_code: null
	});
	let errors = $state<Record<string, string>>({});

	function validate(): boolean {
		const newErrors: Record<string, string> = {};

		if (!form.name.trim()) {
			newErrors.name = 'Household name is required';
		}

		errors = newErrors;
		return Object.keys(newErrors).length === 0;
	}

	async function handleSubmit(e: Event) {
		e.preventDefault();

		if (!validate()) return;

		isLoading = true;
		try {
			const household = await householdApi.create(form);
			toasts.success('Household created successfully');
			onSave(household);
		} catch (err) {
			toasts.error(err instanceof Error ? err.message : 'Failed to create household');
		} finally {
			isLoading = false;
		}
	}

	function handleBackdropClick(e: MouseEvent) {
		if (e.target === e.currentTarget) {
			onClose();
		}
	}
</script>

<!-- svelte-ignore a11y_no_noninteractive_element_interactions -->
<!-- svelte-ignore a11y_click_events_have_key_events -->
<div
	class="fixed inset-0 z-50 overflow-y-auto"
	aria-labelledby="modal-title"
	role="dialog"
	aria-modal="true"
	onclick={handleBackdropClick}
>
	<div class="flex min-h-full items-end justify-center p-4 text-center sm:items-center sm:p-0">
		<div class="fixed inset-0 bg-gray-500 bg-opacity-75 transition-opacity"></div>

		<div
			class="relative transform overflow-hidden rounded-lg bg-white text-left shadow-xl transition-all sm:my-8 sm:w-full sm:max-w-lg"
			onclick={(e) => e.stopPropagation()}
		>
			<form onsubmit={handleSubmit}>
				<div class="bg-white px-4 pb-4 pt-5 sm:p-6 sm:pb-4">
					<div class="flex items-center justify-between mb-4">
						<h3 class="text-lg font-semibold text-gray-900" id="modal-title">Create Household</h3>
						<button type="button" onclick={onClose} class="text-gray-400 hover:text-gray-500" aria-label="Close modal">
							<svg class="h-6 w-6" fill="none" stroke="currentColor" viewBox="0 0 24 24" aria-hidden="true" role="img">
								<path
									stroke-linecap="round"
									stroke-linejoin="round"
									stroke-width="2"
									d="M6 18L18 6M6 6l12 12"
								/>
							</svg>
						</button>
					</div>

					<div class="space-y-4">
						<div>
							<label for="name" class="block text-sm font-medium text-gray-700">
								Household Name <span aria-hidden="true" class="text-red-500">*</span><span class="sr-only">(required)</span>
							</label>
							<input
								type="text"
								id="name"
								name="name"
								bind:value={form.name}
								placeholder="e.g., The Smith Family"
								aria-required="true"
								aria-invalid={errors.name ? 'true' : undefined}
								aria-describedby={errors.name ? 'name-error' : undefined}
								class="mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-blue-500 focus:ring-blue-500 sm:text-sm"
							/>
							{#if errors.name}
								<p id="name-error" class="mt-1 text-sm text-red-600" role="alert">{errors.name}</p>
							{/if}
						</div>

						<div>
							<label for="address_line1" class="block text-sm font-medium text-gray-700">
								Address Line 1
							</label>
							<input
								type="text"
								id="address_line1"
								name="address_line1"
								bind:value={form.address_line1}
								placeholder="Street address"
								class="mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-blue-500 focus:ring-blue-500 sm:text-sm"
							/>
						</div>

						<div>
							<label for="address_line2" class="block text-sm font-medium text-gray-700">
								Address Line 2
							</label>
							<input
								type="text"
								id="address_line2"
								name="address_line2"
								bind:value={form.address_line2}
								placeholder="Apartment, suite, etc."
								class="mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-blue-500 focus:ring-blue-500 sm:text-sm"
							/>
						</div>

						<div class="grid grid-cols-2 gap-4">
							<div>
								<label for="city" class="block text-sm font-medium text-gray-700">City</label>
								<input
									type="text"
									id="city"
									name="city"
									bind:value={form.city}
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
									name="postal_code"
									bind:value={form.postal_code}
									class="mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-blue-500 focus:ring-blue-500 sm:text-sm"
								/>
							</div>
						</div>
					</div>
				</div>

				<div class="bg-gray-50 px-4 py-3 sm:flex sm:flex-row-reverse sm:px-6 gap-2">
					<button
						type="submit"
						disabled={isLoading}
						class="inline-flex w-full justify-center rounded-md bg-blue-600 px-3 py-2 text-sm font-semibold text-white shadow-sm hover:bg-blue-500 sm:w-auto disabled:opacity-50"
					>
						{isLoading ? 'Creating...' : 'Create Household'}
					</button>
					<button
						type="button"
						onclick={onClose}
						class="mt-3 inline-flex w-full justify-center rounded-md bg-white px-3 py-2 text-sm font-semibold text-gray-900 shadow-sm ring-1 ring-inset ring-gray-300 hover:bg-gray-50 sm:mt-0 sm:w-auto"
					>
						Cancel
					</button>
				</div>
			</form>
		</div>
	</div>
</div>
