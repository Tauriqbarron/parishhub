<script lang="ts">
	import type { Sacrament, SacramentType } from '$lib/api';

	interface Props {
		sacrament: Sacrament | null;
		existingSacraments: Sacrament[];
		onSave: (data: {
			sacrament_type: SacramentType;
			date_received: string;
			notes: string | null;
			additional_data: Record<string, unknown> | null;
		}) => void;
		onClose: () => void;
	}

	let { sacrament, existingSacraments, onSave, onClose }: Props = $props();

	const isEditing = $derived(sacrament !== null);

	let sacramentType = $state<SacramentType>(sacrament?.sacrament_type ?? 'baptism');
	let dateReceived = $state(sacrament?.date_received ?? '');
	let notes = $state(sacrament?.notes ?? '');
	let additionalData = $state<Record<string, unknown>>(sacrament?.additional_data ?? {});
	let isSaving = $state(false);

	const sacramentLabels: Record<SacramentType, string> = {
		baptism: 'Baptism',
		first_communion: 'First Communion',
		confirmation: 'Confirmation',
		marriage: 'Marriage',
		holy_orders: 'Holy Orders'
	};

	// Get sacrament types that are already received (excluding the one being edited)
	const receivedTypes = $derived(
		new Set(
			existingSacraments
				.filter((s) => !sacrament || s.id !== sacrament.id)
				.map((s) => s.sacrament_type)
		)
	);

	// Available types for selection (marriage can be received multiple times)
	const availableTypes = $derived(
		(Object.keys(sacramentLabels) as SacramentType[]).filter(
			(type) => type === 'marriage' || !receivedTypes.has(type) || sacrament?.sacrament_type === type
		)
	);

	function handleSubmit(e: SubmitEvent) {
		e.preventDefault();
		if (!dateReceived) return;

		isSaving = true;
		onSave({
			sacrament_type: sacramentType,
			date_received: dateReceived,
			notes: notes || null,
			additional_data: Object.keys(additionalData).length > 0 ? additionalData : null
		});
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
		<!-- Backdrop -->
		<div class="fixed inset-0 bg-gray-500 bg-opacity-75 transition-opacity"></div>

		<!-- Modal panel -->
		<div
			class="relative transform overflow-hidden rounded-lg bg-white text-left shadow-xl transition-all sm:my-8 sm:w-full sm:max-w-lg"
			onclick={(e) => e.stopPropagation()}
		>
			<form onsubmit={handleSubmit}>
				<div class="bg-white px-4 pb-4 pt-5 sm:p-6 sm:pb-4">
					<div class="flex items-center justify-between mb-4">
						<h3 class="text-lg font-semibold text-gray-900" id="modal-title">
							{isEditing ? 'Edit Sacrament' : 'Add Sacrament'}
						</h3>
						<button
							type="button"
							onclick={onClose}
							class="text-gray-400 hover:text-gray-500"
						>
							<svg class="h-6 w-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
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
						<!-- Sacrament Type -->
						<div>
							<label for="sacrament_type" class="block text-sm font-medium text-gray-700">
								Sacrament Type *
							</label>
							<select
								id="sacrament_type"
								bind:value={sacramentType}
								disabled={isEditing}
								required
								class="mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-blue-500 focus:ring-blue-500 sm:text-sm disabled:bg-gray-100"
							>
								{#each availableTypes as type (type)}
									<option value={type}>{sacramentLabels[type]}</option>
								{/each}
							</select>
							{#if isEditing}
								<p class="mt-1 text-xs text-gray-500">Sacrament type cannot be changed</p>
							{/if}
						</div>

						<!-- Date Received -->
						<div>
							<label for="date_received" class="block text-sm font-medium text-gray-700">
								Date Received *
							</label>
							<input
								type="date"
								id="date_received"
								bind:value={dateReceived}
								required
								class="mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-blue-500 focus:ring-blue-500 sm:text-sm"
							/>
						</div>

						<!-- Type-specific fields -->
						{#if sacramentType === 'baptism'}
							<div>
								<label for="godparents" class="block text-sm font-medium text-gray-700">
									Godparents
								</label>
								<input
									type="text"
									id="godparents"
									value={additionalData.godparents ?? ''}
									oninput={(e) =>
										(additionalData = { ...additionalData, godparents: e.currentTarget.value })}
									placeholder="Names of godparents"
									class="mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-blue-500 focus:ring-blue-500 sm:text-sm"
								/>
							</div>
						{:else if sacramentType === 'first_communion' || sacramentType === 'confirmation'}
							<div>
								<label for="sponsor" class="block text-sm font-medium text-gray-700">
									Sponsor
								</label>
								<input
									type="text"
									id="sponsor"
									value={additionalData.sponsor ?? ''}
									oninput={(e) =>
										(additionalData = { ...additionalData, sponsor: e.currentTarget.value })}
									placeholder="Name of sponsor"
									class="mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-blue-500 focus:ring-blue-500 sm:text-sm"
								/>
							</div>
						{:else if sacramentType === 'marriage'}
							<div>
								<label for="spouse_name" class="block text-sm font-medium text-gray-700">
									Spouse Name
								</label>
								<input
									type="text"
									id="spouse_name"
									value={additionalData.spouse_name ?? ''}
									oninput={(e) =>
										(additionalData = { ...additionalData, spouse_name: e.currentTarget.value })}
									placeholder="Name of spouse"
									class="mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-blue-500 focus:ring-blue-500 sm:text-sm"
								/>
							</div>
							<div>
								<label for="witnesses" class="block text-sm font-medium text-gray-700">
									Witnesses
								</label>
								<input
									type="text"
									id="witnesses"
									value={additionalData.witnesses ?? ''}
									oninput={(e) =>
										(additionalData = { ...additionalData, witnesses: e.currentTarget.value })}
									placeholder="Names of witnesses"
									class="mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-blue-500 focus:ring-blue-500 sm:text-sm"
								/>
							</div>
						{:else if sacramentType === 'holy_orders'}
							<div>
								<label for="ordaining_bishop" class="block text-sm font-medium text-gray-700">
									Ordaining Bishop
								</label>
								<input
									type="text"
									id="ordaining_bishop"
									value={additionalData.ordaining_bishop ?? ''}
									oninput={(e) =>
										(additionalData = {
											...additionalData,
											ordaining_bishop: e.currentTarget.value
										})}
									placeholder="Name of ordaining bishop"
									class="mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-blue-500 focus:ring-blue-500 sm:text-sm"
								/>
							</div>
						{/if}

						<!-- Notes -->
						<div>
							<label for="notes" class="block text-sm font-medium text-gray-700">Notes</label>
							<textarea
								id="notes"
								bind:value={notes}
								rows="3"
								placeholder="Additional notes..."
								class="mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-blue-500 focus:ring-blue-500 sm:text-sm"
							></textarea>
						</div>
					</div>
				</div>

				<div class="bg-gray-50 px-4 py-3 sm:flex sm:flex-row-reverse sm:px-6 gap-2">
					<button
						type="submit"
						disabled={isSaving || !dateReceived}
						class="inline-flex w-full justify-center rounded-md bg-blue-600 px-3 py-2 text-sm font-semibold text-white shadow-sm hover:bg-blue-500 sm:w-auto disabled:opacity-50"
					>
						{#if isSaving}
							Saving...
						{:else}
							{isEditing ? 'Save Changes' : 'Add Sacrament'}
						{/if}
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
