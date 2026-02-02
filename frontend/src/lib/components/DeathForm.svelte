<script lang="ts">
	import type { DeathCreate, DeathWithPerson } from '$lib/api';
	import PersonSearchInput from './PersonSearchInput.svelte';

	interface Props {
		death: DeathWithPerson | null;
		personId: number;
		onSave: (data: DeathCreate) => void;
		onClose: () => void;
	}

	let { death, personId, onSave, onClose }: Props = $props();

	const isEditing = $derived(death !== null);

	let dateOfDeath = $state(death?.date_of_death ?? '');
	let placeOfDeath = $state(death?.place_of_death ?? '');
	let causeOfDeath = $state(death?.cause_of_death ?? '');
	let burialDate = $state(death?.burial_date ?? '');
	let burialLocation = $state(death?.burial_location ?? '');
	let funeralDate = $state(death?.funeral_date ?? '');
	let funeralLocation = $state(death?.funeral_location ?? '');
	let officiatingPriestId = $state<number | null>(death?.officiating_priest_id ?? null);
	let officiatingPriestName = $state(
		death?.officiating_priest
			? `${death.officiating_priest.first_name} ${death.officiating_priest.last_name}`
			: ''
	);
	let notes = $state(death?.notes ?? '');
	let isSaving = $state(false);

	function handleSubmit(e: SubmitEvent) {
		e.preventDefault();
		if (!dateOfDeath) return;

		isSaving = true;
		onSave({
			person_id: personId,
			date_of_death: dateOfDeath,
			place_of_death: placeOfDeath || null,
			cause_of_death: causeOfDeath || null,
			burial_date: burialDate || null,
			burial_location: burialLocation || null,
			funeral_date: funeralDate || null,
			funeral_location: funeralLocation || null,
			officiating_priest_id: officiatingPriestId,
			notes: notes || null
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
			class="relative transform overflow-hidden rounded-lg bg-white text-left shadow-xl transition-all sm:my-8 sm:w-full sm:max-w-2xl"
			role="document"
			onclick={(e) => e.stopPropagation()}
		>
			<form onsubmit={handleSubmit}>
				<div class="bg-white px-4 pb-4 pt-5 sm:p-6 sm:pb-4">
					<div class="flex items-center justify-between mb-4">
						<h3 class="text-lg font-semibold text-gray-900" id="modal-title">
							{isEditing ? 'Edit Death Record' : 'Record Death'}
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

					<div class="grid grid-cols-1 md:grid-cols-2 gap-4">
						<!-- Date of Death -->
						<div class="col-span-1">
							<label for="date_of_death" class="block text-sm font-medium text-gray-700">
								Date of Death <span aria-hidden="true">*</span><span class="sr-only"
									>(required)</span
								>
							</label>
							<input
								type="date"
								id="date_of_death"
								name="date_of_death"
								bind:value={dateOfDeath}
								required
								aria-required="true"
								class="mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-red-500 focus:ring-red-500 sm:text-sm"
							/>
						</div>

						<!-- Place of Death -->
						<div class="col-span-1">
							<label for="place_of_death" class="block text-sm font-medium text-gray-700">
								Place of Death
							</label>
							<input
								type="text"
								id="place_of_death"
								bind:value={placeOfDeath}
								placeholder="e.g. Wellington Hospital"
								class="mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-red-500 focus:ring-red-500 sm:text-sm"
							/>
						</div>

						<!-- Cause of Death -->
						<div class="col-span-full">
							<label for="cause_of_death" class="block text-sm font-medium text-gray-700">
								Cause of Death
							</label>
							<input
								type="text"
								id="cause_of_death"
								bind:value={causeOfDeath}
								placeholder="Optional cause of death"
								class="mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-red-500 focus:ring-red-500 sm:text-sm"
							/>
						</div>

						<div class="col-span-full border-t border-gray-100 my-2 pt-2">
							<h4 class="text-sm font-medium text-gray-900 mb-3">Funeral & Burial</h4>
						</div>

						<!-- Funeral Date -->
						<div class="col-span-1">
							<label for="funeral_date" class="block text-sm font-medium text-gray-700">
								Funeral Date
							</label>
							<input
								type="date"
								id="funeral_date"
								bind:value={funeralDate}
								class="mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-blue-500 focus:ring-blue-500 sm:text-sm"
							/>
						</div>

						<!-- Funeral Location -->
						<div class="col-span-1">
							<label for="funeral_location" class="block text-sm font-medium text-gray-700">
								Funeral Location
							</label>
							<input
								type="text"
								id="funeral_location"
								bind:value={funeralLocation}
								placeholder="e.g. Parish Church"
								class="mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-blue-500 focus:ring-blue-500 sm:text-sm"
							/>
						</div>

						<!-- Burial Date -->
						<div class="col-span-1">
							<label for="burial_date" class="block text-sm font-medium text-gray-700">
								Burial Date
							</label>
							<input
								type="date"
								id="burial_date"
								bind:value={burialDate}
								class="mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-blue-500 focus:ring-blue-500 sm:text-sm"
							/>
						</div>

						<!-- Burial Location -->
						<div class="col-span-1">
							<label for="burial_location" class="block text-sm font-medium text-gray-700">
								Burial Location
							</label>
							<input
								type="text"
								id="burial_location"
								bind:value={burialLocation}
								placeholder="e.g. Karori Cemetery"
								class="mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-blue-500 focus:ring-blue-500 sm:text-sm"
							/>
						</div>

						<!-- Officiating Priest -->
						<div class="col-span-full">
							<label class="block text-sm font-medium text-gray-700">Officiating Priest</label>
							<PersonSearchInput
								value={officiatingPriestId
									? { id: officiatingPriestId, name: officiatingPriestName }
									: null}
								placeholder="Search for a priest..."
								onSelect={(selection) => {
									if (selection && 'id' in selection) {
										officiatingPriestId = selection.id;
										officiatingPriestName = selection.name;
									} else {
										officiatingPriestId = null;
										officiatingPriestName = '';
									}
								}}
							/>
						</div>

						<!-- Notes -->
						<div class="col-span-full">
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
						disabled={isSaving || !dateOfDeath}
						class="inline-flex w-full justify-center rounded-md bg-red-600 px-3 py-2 text-sm font-semibold text-white shadow-sm hover:bg-red-500 sm:w-auto disabled:opacity-50"
					>
						{#if isSaving}
							Saving...
						{:else}
							{isEditing ? 'Save Changes' : 'Record Death'}
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
