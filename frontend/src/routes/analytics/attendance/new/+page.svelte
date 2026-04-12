<script lang="ts">
	import { onMount } from 'svelte';
	import { goto } from '$app/navigation';
	import { attendanceApi, massTimesApi, type MassAttendanceCreate, type MassTime } from '$lib/api';
	import { addToast } from '$lib/stores/toast';

	let date = $state('');
	let massEntries = $state([
		{ mass_time_id: null as number | null, mass_time: '', attendance_count: 0, customTime: false }
	]);
	let notes = $state('');
	let submitting = $state(false);
	let massTimeOptions: MassTime[] = $state([]);

	onMount(async () => {
		try {
			massTimeOptions = await massTimesApi.list(true);
		} catch {
			// Fallback to text input if API fails
		}
	});

	// Set default date to previous Sunday
	$effect(() => {
		if (!date) {
			const today = new Date();
			const dayOfWeek = today.getDay();
			// eslint-disable-next-line svelte/prefer-svelte-reactivity
			const previousSunday = new Date(today);
			previousSunday.setDate(today.getDate() - dayOfWeek - (dayOfWeek === 0 ? 7 : 0));
			date = previousSunday.toISOString().split('T')[0];
		}
	});

	function formatTime(timeStr: string): string {
		const [hours, minutes] = timeStr.split(':');
		const h = parseInt(hours, 10);
		const suffix = h >= 12 ? 'PM' : 'AM';
		const h12 = h % 12 || 12;
		return `${h12}:${minutes} ${suffix}`;
	}

	function handleMassTimeChange(index: number, value: string) {
		if (value === '__other__') {
			massEntries[index].customTime = true;
			massEntries[index].mass_time_id = null;
			massEntries[index].mass_time = '';
		} else if (value) {
			massEntries[index].customTime = false;
			massEntries[index].mass_time_id = parseInt(value, 10);
			const mt = massTimeOptions.find((m) => m.id === massEntries[index].mass_time_id);
			massEntries[index].mass_time = mt?.name ?? '';
		} else {
			massEntries[index].customTime = false;
			massEntries[index].mass_time_id = null;
			massEntries[index].mass_time = '';
		}
	}

	function addMassEntry() {
		massEntries = [
			...massEntries,
			{ mass_time_id: null, mass_time: '', attendance_count: 0, customTime: false }
		];
	}

	function removeMassEntry(index: number) {
		massEntries = massEntries.filter((_, i) => i !== index);
	}

	async function handleSubmit() {
		if (!date) {
			addToast('Please select a date', 'error');
			return;
		}

		const validEntries = massEntries.filter((e) => e.mass_time_id && e.attendance_count > 0);
		if (validEntries.length === 0) {
			addToast('Please select a mass time and enter a count', 'error');
			return;
		}

		submitting = true;
		try {
			for (const entry of validEntries) {
				const data: MassAttendanceCreate = {
					date,
					mass_time_id: entry.mass_time_id || undefined,
					attendance_count: entry.attendance_count,
					notes: notes || null
				};
				await attendanceApi.create(data);
			}

			addToast('Attendance recorded successfully', 'success');
			goto('/analytics');
		} catch {
			addToast('Failed to record attendance', 'error');
		} finally {
			submitting = false;
		}
	}
</script>

<svelte:head>
	<title>Record Attendance - Parish Database</title>
</svelte:head>

<div class="max-w-2xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
	<div class="flex items-center gap-4 mb-8">
		<a href="/analytics" class="text-brand-text-muted hover:text-brand-text-secondary">
			<svg class="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
				<path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M15 19l-7-7 7-7" />
			</svg>
		</a>
		<h1 class="text-2xl font-bold text-brand-primary">Record Mass Attendance</h1>
	</div>

	<form
		onsubmit={(e) => {
			e.preventDefault();
			handleSubmit();
		}}
		class="bg-white rounded-lg shadow p-6 space-y-6"
	>
		<div>
			<label for="date" class="block text-sm font-medium text-brand-text-secondary mb-1">Date</label
			>
			<input
				type="date"
				id="date"
				bind:value={date}
				required
				class="w-full px-3 py-2 border border-brand-border rounded-lg focus:ring-2 focus:ring-brand-accent focus:border-transparent"
			/>
		</div>

		<div class="space-y-4">
			<p class="text-sm text-brand-text-muted">Enter attendance for each Mass time:</p>
			{#each massEntries as entry, index}
				<div class="flex gap-4 items-end">
					<div class="flex-1">
						<label class="block text-sm font-medium text-brand-text-secondary mb-1">Mass Time</label
						>
						{#if massTimeOptions.length > 0 && !entry.customTime}
							<select
								value={entry.mass_time_id ?? ''}
								onchange={(e) => handleMassTimeChange(index, (e.target as HTMLSelectElement).value)}
								class="w-full px-3 py-2 border border-brand-border rounded-lg focus:ring-2 focus:ring-brand-accent focus:border-transparent"
							>
								<option value="">Select mass time...</option>
								{#each massTimeOptions as mt (mt.id)}
									<option value={mt.id}>{mt.name} ({formatTime(mt.time)})</option>
								{/each}
								<option value="__other__">Other (specify)</option>
							</select>
						{:else}
							<div class="flex gap-2">
								<input
									type="text"
									placeholder="e.g., 8:00 AM"
									bind:value={entry.mass_time}
									class="flex-1 px-3 py-2 border border-brand-border rounded-lg focus:ring-2 focus:ring-brand-accent focus:border-transparent"
								/>
								{#if massTimeOptions.length > 0 && entry.customTime}
									<button
										type="button"
										onclick={() => {
											entry.customTime = false;
											entry.mass_time = '';
										}}
										class="px-3 py-2 text-brand-text-muted hover:bg-brand-bg-muted rounded-lg text-sm"
										title="Back to dropdown"
									>
										<svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
											<path
												stroke-linecap="round"
												stroke-linejoin="round"
												stroke-width="2"
												d="M4 4v5h.582m15.356 2A8.001 8.001 0 004.582 9m0 0H9m11 11v-5h-.581m0 0a8.003 8.003 0 01-15.357-2m15.357 2H15"
											/>
										</svg>
									</button>
								{/if}
							</div>
						{/if}
					</div>
					<div class="w-32">
						<label class="block text-sm font-medium text-brand-text-secondary mb-1">Count</label>
						<input
							type="number"
							min="0"
							bind:value={entry.attendance_count}
							class="w-full px-3 py-2 border border-brand-border rounded-lg focus:ring-2 focus:ring-brand-accent focus:border-transparent"
						/>
					</div>
					{#if massEntries.length > 1}
						<button
							type="button"
							onclick={() => removeMassEntry(index)}
							class="px-3 py-2 text-brand-error hover:bg-brand-error/10 rounded-lg"
						>
							<svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
								<path
									stroke-linecap="round"
									stroke-linejoin="round"
									stroke-width="2"
									d="M6 18L18 6M6 6l12 12"
								/>
							</svg>
						</button>
					{/if}
				</div>
			{/each}
			<button
				type="button"
				onclick={addMassEntry}
				class="text-brand-accent hover:text-brand-accent/90 text-sm font-medium"
			>
				+ Add Another Mass Time
			</button>
			{#if massTimeOptions.length === 0}
				<p class="text-xs text-brand-text-muted">
					<a href="/settings/mass-times" class="text-brand-accent hover:underline"
						>Configure mass times</a
					> to use a dropdown instead of free text.
				</p>
			{/if}
		</div>

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

		<div class="flex gap-4">
			<button
				type="submit"
				disabled={submitting}
				class="flex-1 px-6 py-3 bg-brand-accent text-white rounded-lg hover:bg-brand-accent/90 transition-colors disabled:opacity-50"
			>
				{submitting ? 'Saving...' : 'Record Attendance'}
			</button>
			<a
				href="/analytics"
				class="px-6 py-3 border border-gray-300 text-brand-text-secondary rounded-lg hover:bg-gray-50 transition-colors text-center"
			>
				Cancel
			</a>
		</div>
	</form>
</div>
