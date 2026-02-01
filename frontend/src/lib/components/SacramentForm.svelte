<script lang="ts">
	import type { Sacrament, SacramentType } from '$lib/api';
	import PersonSearchInput from './PersonSearchInput.svelte';

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
			(type) =>
				type === 'marriage' || !receivedTypes.has(type) || sacrament?.sacrament_type === type
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
	tabindex="-1"
	onclick={handleBackdropClick}
>
	<div class="flex min-h-full items-end justify-center p-4 text-center sm:items-center sm:p-0">
		<!-- Backdrop -->
		<div class="fixed inset-0 bg-gray-500 bg-opacity-75 transition-opacity"></div>

		<!-- Modal panel -->
		<div
			class="relative transform overflow-hidden rounded-lg bg-white text-left shadow-xl transition-all sm:my-8 sm:w-full sm:max-w-lg"
			role="document"
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
							aria-label="Close modal"
						>
							<svg
								class="h-6 w-6"
								fill="none"
								stroke="currentColor"
								viewBox="0 0 24 24"
								aria-hidden="true"
								role="img"
							>
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
								Sacrament Type <span aria-hidden="true">*</span><span class="sr-only"
									>(required)</span
								>
							</label>
							<select
								id="sacrament_type"
								name="sacrament_type"
								bind:value={sacramentType}
								disabled={isEditing}
								required
								aria-required="true"
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
								Date Received <span aria-hidden="true">*</span><span class="sr-only"
									>(required)</span
								>
							</label>
							<input
								type="date"
								id="date_received"
								name="date_received"
								bind:value={dateReceived}
								required
								aria-required="true"
								class="mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-blue-500 focus:ring-blue-500 sm:text-sm"
							/>
						</div>

						<!-- Type-specific fields -->
						{#if sacramentType === 'baptism'}
							<div>
								<label class="block text-sm font-medium text-gray-700">Godfather</label>
								<PersonSearchInput
									value={additionalData.godfather_id
										? {
												id: additionalData.godfather_id as number,
												name: (additionalData.godfather as string) ?? ''
											}
										: additionalData.godfather
											? { name: additionalData.godfather as string }
											: null}
									placeholder="Search or enter godfather name"
									onSelect={(selection) => {
										if (selection && 'id' in selection) {
											additionalData = {
												...additionalData,
												godfather_id: selection.id,
												godfather: selection.name
											};
										} else if (selection) {
											additionalData = {
												...additionalData,
												godfather_id: null,
												godfather: selection.name
											};
										} else {
											additionalData = { ...additionalData, godfather_id: null, godfather: null };
										}
									}}
								/>
							</div>
							<div>
								<label class="block text-sm font-medium text-gray-700">Godmother</label>
								<PersonSearchInput
									value={additionalData.godmother_id
										? {
												id: additionalData.godmother_id as number,
												name: (additionalData.godmother as string) ?? ''
											}
										: additionalData.godmother
											? { name: additionalData.godmother as string }
											: null}
									placeholder="Search or enter godmother name"
									onSelect={(selection) => {
										if (selection && 'id' in selection) {
											additionalData = {
												...additionalData,
												godmother_id: selection.id,
												godmother: selection.name
											};
										} else if (selection) {
											additionalData = {
												...additionalData,
												godmother_id: null,
												godmother: selection.name
											};
										} else {
											additionalData = { ...additionalData, godmother_id: null, godmother: null };
										}
									}}
								/>
							</div>
							<div>
								<label class="block text-sm font-medium text-gray-700">Minister</label>
								<PersonSearchInput
									value={additionalData.minister_id
										? {
												id: additionalData.minister_id as number,
												name: (additionalData.minister as string) ?? ''
											}
										: additionalData.minister
											? { name: additionalData.minister as string }
											: null}
									placeholder="Search or enter minister name"
									onSelect={(selection) => {
										if (selection && 'id' in selection) {
											additionalData = {
												...additionalData,
												minister_id: selection.id,
												minister: selection.name
											};
										} else if (selection) {
											additionalData = {
												...additionalData,
												minister_id: null,
												minister: selection.name
											};
										} else {
											additionalData = { ...additionalData, minister_id: null, minister: null };
										}
									}}
								/>
							</div>
						{:else if sacramentType === 'first_communion'}
							<div>
								<label class="block text-sm font-medium text-gray-700">Sponsor</label>
								<PersonSearchInput
									value={additionalData.sponsor_id
										? {
												id: additionalData.sponsor_id as number,
												name: (additionalData.sponsor as string) ?? ''
											}
										: additionalData.sponsor
											? { name: additionalData.sponsor as string }
											: null}
									placeholder="Search or enter sponsor name"
									onSelect={(selection) => {
										if (selection && 'id' in selection) {
											additionalData = {
												...additionalData,
												sponsor_id: selection.id,
												sponsor: selection.name
											};
										} else if (selection) {
											additionalData = {
												...additionalData,
												sponsor_id: null,
												sponsor: selection.name
											};
										} else {
											additionalData = { ...additionalData, sponsor_id: null, sponsor: null };
										}
									}}
								/>
							</div>
						{:else if sacramentType === 'confirmation'}
							<div>
								<label class="block text-sm font-medium text-gray-700">Sponsor</label>
								<PersonSearchInput
									value={additionalData.sponsor_id
										? {
												id: additionalData.sponsor_id as number,
												name: (additionalData.sponsor as string) ?? ''
											}
										: additionalData.sponsor
											? { name: additionalData.sponsor as string }
											: null}
									placeholder="Search or enter sponsor name"
									onSelect={(selection) => {
										if (selection && 'id' in selection) {
											additionalData = {
												...additionalData,
												sponsor_id: selection.id,
												sponsor: selection.name
											};
										} else if (selection) {
											additionalData = {
												...additionalData,
												sponsor_id: null,
												sponsor: selection.name
											};
										} else {
											additionalData = { ...additionalData, sponsor_id: null, sponsor: null };
										}
									}}
								/>
							</div>
							<div>
								<label class="block text-sm font-medium text-gray-700">Bishop</label>
								<PersonSearchInput
									value={additionalData.bishop_id
										? {
												id: additionalData.bishop_id as number,
												name: (additionalData.bishop as string) ?? ''
											}
										: additionalData.bishop
											? { name: additionalData.bishop as string }
											: null}
									placeholder="Search or enter bishop name"
									onSelect={(selection) => {
										if (selection && 'id' in selection) {
											additionalData = {
												...additionalData,
												bishop_id: selection.id,
												bishop: selection.name
											};
										} else if (selection) {
											additionalData = {
												...additionalData,
												bishop_id: null,
												bishop: selection.name
											};
										} else {
											additionalData = { ...additionalData, bishop_id: null, bishop: null };
										}
									}}
								/>
							</div>
							<div>
								<label for="confirmation_name" class="block text-sm font-medium text-gray-700">
									Confirmation Name
								</label>
								<input
									type="text"
									id="confirmation_name"
									value={additionalData.confirmation_name ?? ''}
									oninput={(e) =>
										(additionalData = {
											...additionalData,
											confirmation_name: e.currentTarget.value
										})}
									placeholder="Confirmation name (if different)"
									class="mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-blue-500 focus:ring-blue-500 sm:text-sm"
								/>
							</div>
						{:else if sacramentType === 'marriage'}
							<div>
								<label class="block text-sm font-medium text-gray-700">Spouse</label>
								<PersonSearchInput
									value={additionalData.spouse_id
										? {
												id: additionalData.spouse_id as number,
												name: (additionalData.spouse_name as string) ?? ''
											}
										: additionalData.spouse_name
											? { name: additionalData.spouse_name as string }
											: null}
									placeholder="Search or enter spouse name"
									onSelect={(selection) => {
										if (selection && 'id' in selection) {
											additionalData = {
												...additionalData,
												spouse_id: selection.id,
												spouse_name: selection.name
											};
										} else if (selection) {
											additionalData = {
												...additionalData,
												spouse_id: null,
												spouse_name: selection.name
											};
										} else {
											additionalData = { ...additionalData, spouse_id: null, spouse_name: null };
										}
									}}
								/>
							</div>
							<div>
								<label class="block text-sm font-medium text-gray-700">Witness 1</label>
								<PersonSearchInput
									value={additionalData.witness1_id
										? {
												id: additionalData.witness1_id as number,
												name: (additionalData.witness1 as string) ?? ''
											}
										: additionalData.witness1
											? { name: additionalData.witness1 as string }
											: null}
									placeholder="Search or enter witness name"
									onSelect={(selection) => {
										if (selection && 'id' in selection) {
											additionalData = {
												...additionalData,
												witness1_id: selection.id,
												witness1: selection.name
											};
										} else if (selection) {
											additionalData = {
												...additionalData,
												witness1_id: null,
												witness1: selection.name
											};
										} else {
											additionalData = { ...additionalData, witness1_id: null, witness1: null };
										}
									}}
								/>
							</div>
							<div>
								<label class="block text-sm font-medium text-gray-700">Witness 2</label>
								<PersonSearchInput
									value={additionalData.witness2_id
										? {
												id: additionalData.witness2_id as number,
												name: (additionalData.witness2 as string) ?? ''
											}
										: additionalData.witness2
											? { name: additionalData.witness2 as string }
											: null}
									placeholder="Search or enter witness name"
									onSelect={(selection) => {
										if (selection && 'id' in selection) {
											additionalData = {
												...additionalData,
												witness2_id: selection.id,
												witness2: selection.name
											};
										} else if (selection) {
											additionalData = {
												...additionalData,
												witness2_id: null,
												witness2: selection.name
											};
										} else {
											additionalData = { ...additionalData, witness2_id: null, witness2: null };
										}
									}}
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
								name="notes"
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
