<script lang="ts">
	import { goto } from '$app/navigation';
	import { deathsApi, type DeathCreate } from '$lib/api';
	import { toasts } from '$lib/stores/toast';
	import PersonSearchInput from '$lib/components/PersonSearchInput.svelte';

	let personId = $state<number | null>(null);
	let personName = $state('');
	let dateOfDeath = $state('');
	let placeOfDeath = $state('');
	let causeOfDeath = $state('');
	let burialDate = $state('');
	let burialLocation = $state('');
	let funeralDate = $state('');
	let funeralLocation = $state('');
	let officiatingPriestId = $state<number | null>(null);
	let officiatingPriestName = $state('');
	let notes = $state('');
	let submitting = $state(false);

	async function handleSubmit() {
		if (!personId || !dateOfDeath) {
			toasts.error('Please fill in all required fields');
			return;
		}

		submitting = true;
		try {
			const data: DeathCreate = {
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
			};
			await deathsApi.create(data);
			toasts.success('Death recorded successfully');
			goto('/analytics');
		} catch (err) {
			toasts.error(err instanceof Error ? err.message : 'Failed to record death');
		} finally {
			submitting = false;
		}
	}
</script>

<svelte:head>
	<title>Record Death - Parish Database</title>
</svelte:head>

<div class="max-w-2xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
	<div class="flex items-center gap-4 mb-8">
		<a href="/analytics" class="text-brand-text-muted hover:text-brand-text-secondary">
			<svg class="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
				<path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M15 19l-7-7 7-7" />
			</svg>
		</a>
		<h1 class="text-2xl font-bold text-brand-primary">Record Death</h1>
	</div>

	<form
		onsubmit={(e) => {
			e.preventDefault();
			handleSubmit();
		}}
		class="bg-white rounded-lg shadow p-6 space-y-6"
	>
		<!-- Person Selection -->
		<div>
			<label class="block text-sm font-medium text-brand-text-secondary mb-1">
				Deceased Person <span class="text-brand-error">*</span>
			</label>
			<PersonSearchInput
				value={personId ? { id: personId, name: personName } : null}
				placeholder="Search for the person..."
				onSelect={(selection) => {
					if (selection && 'id' in selection) {
						personId = selection.id;
						personName = selection.name;
					} else {
						personId = null;
						personName = '';
					}
				}}
			/>
		</div>

		<div class="grid grid-cols-1 md:grid-cols-2 gap-4">
			<!-- Date of Death -->
			<div>
				<label for="date_of_death" class="block text-sm font-medium text-brand-text-secondary mb-1">
					Date of Death <span class="text-brand-error">*</span>
				</label>
				<input
					type="date"
					id="date_of_death"
					bind:value={dateOfDeath}
					required
					class="w-full px-3 py-2 border border-brand-border rounded-lg focus:ring-2 focus:ring-brand-error focus:border-transparent"
				/>
			</div>

			<!-- Place of Death -->
			<div>
				<label
					for="place_of_death"
					class="block text-sm font-medium text-brand-text-secondary mb-1"
				>
					Place of Death
				</label>
				<input
					type="text"
					id="place_of_death"
					bind:value={placeOfDeath}
					placeholder="e.g. Hospital name or City"
					class="w-full px-3 py-2 border border-brand-border rounded-lg focus:ring-2 focus:ring-brand-error focus:border-transparent"
				/>
			</div>
		</div>

		<!-- Cause of Death -->
		<div>
			<label for="cause_of_death" class="block text-sm font-medium text-brand-text-secondary mb-1">
				Cause of Death (optional)
			</label>
			<input
				type="text"
				id="cause_of_death"
				bind:value={causeOfDeath}
				class="w-full px-3 py-2 border border-brand-border rounded-lg focus:ring-2 focus:ring-brand-error focus:border-transparent"
			/>
		</div>

		<div class="border-t border-brand-border pt-4">
			<h3 class="text-lg font-medium text-brand-primary mb-4">Funeral & Burial</h3>
			<div class="grid grid-cols-1 md:grid-cols-2 gap-4">
				<div>
					<label
						for="funeral_date"
						class="block text-sm font-medium text-brand-text-secondary mb-1"
					>
						Funeral Date
					</label>
					<input
						type="date"
						id="funeral_date"
						bind:value={funeralDate}
						class="w-full px-3 py-2 border border-brand-border rounded-lg focus:ring-2 focus:ring-brand-accent focus:border-transparent"
					/>
				</div>
				<div>
					<label
						for="funeral_location"
						class="block text-sm font-medium text-brand-text-secondary mb-1"
					>
						Funeral Location
					</label>
					<input
						type="text"
						id="funeral_location"
						bind:value={funeralLocation}
						class="w-full px-3 py-2 border border-brand-border rounded-lg focus:ring-2 focus:ring-brand-accent focus:border-transparent"
					/>
				</div>
				<div>
					<label for="burial_date" class="block text-sm font-medium text-brand-text-secondary mb-1">
						Burial Date
					</label>
					<input
						type="date"
						id="burial_date"
						bind:value={burialDate}
						class="w-full px-3 py-2 border border-brand-border rounded-lg focus:ring-2 focus:ring-brand-accent focus:border-transparent"
					/>
				</div>
				<div>
					<label
						for="burial_location"
						class="block text-sm font-medium text-brand-text-secondary mb-1"
					>
						Burial Location
					</label>
					<input
						type="text"
						id="burial_location"
						bind:value={burialLocation}
						class="w-full px-3 py-2 border border-brand-border rounded-lg focus:ring-2 focus:ring-brand-accent focus:border-transparent"
					/>
				</div>
			</div>
		</div>

		<!-- Officiating Priest -->
		<div>
			<label class="block text-sm font-medium text-brand-text-secondary mb-1"
				>Officiating Priest</label
			>
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
		<div>
			<label for="notes" class="block text-sm font-medium text-brand-text-secondary mb-1"
				>Notes (optional)</label
			>
			<textarea
				id="notes"
				bind:value={notes}
				rows="3"
				class="w-full px-3 py-2 border border-brand-border rounded-lg focus:ring-2 focus:ring-brand-accent focus:border-transparent"
				placeholder="Any additional notes..."
			></textarea>
		</div>

		<!-- Actions -->
		<div class="flex gap-4">
			<button
				type="submit"
				disabled={submitting || !personId || !dateOfDeath}
				class="flex-1 px-6 py-3 bg-brand-error text-white rounded-lg hover:bg-brand-error/90 transition-colors disabled:opacity-50 font-medium"
			>
				{submitting ? 'Saving...' : 'Record Death'}
			</button>
			<a
				href="/analytics"
				class="px-6 py-3 border border-brand-border text-brand-text-secondary rounded-lg hover:bg-brand-bg-subtle transition-colors text-center font-medium"
			>
				Cancel
			</a>
		</div>
	</form>
</div>
