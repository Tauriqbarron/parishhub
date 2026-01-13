<script lang="ts">
	import { goto } from '$app/navigation';
	import { attendanceApi, type MassAttendanceCreate } from '$lib/api';
	import { addToast } from '$lib/stores/toast';

	let date = $state('');
	let breakdownByMassTime = $state(false);
	let massEntries = $state([{ mass_time: '', attendance_count: 0 }]);
	let singleAttendanceCount = $state(0);
	let notes = $state('');
	let submitting = $state(false);

	// Set default date to previous Sunday
	$effect(() => {
		if (!date) {
			const today = new Date();
			const dayOfWeek = today.getDay();
			const previousSunday = new Date(today);
			previousSunday.setDate(today.getDate() - dayOfWeek - (dayOfWeek === 0 ? 7 : 0));
			date = previousSunday.toISOString().split('T')[0];
		}
	});

	function addMassEntry() {
		massEntries = [...massEntries, { mass_time: '', attendance_count: 0 }];
	}

	function removeMassEntry(index: number) {
		massEntries = massEntries.filter((_, i) => i !== index);
	}

	async function handleSubmit() {
		if (!date) {
			addToast('Please select a date', 'error');
			return;
		}

		submitting = true;
		try {
			if (breakdownByMassTime) {
				// Submit multiple entries, one per mass time
				for (const entry of massEntries) {
					if (entry.attendance_count > 0) {
						const data: MassAttendanceCreate = {
							date,
							mass_time: entry.mass_time || null,
							attendance_count: entry.attendance_count,
							notes: notes || null
						};
						await attendanceApi.create(data);
					}
				}
			} else {
				if (singleAttendanceCount <= 0) {
					addToast('Please enter an attendance count', 'error');
					submitting = false;
					return;
				}
				const data: MassAttendanceCreate = {
					date,
					attendance_count: singleAttendanceCount,
					notes: notes || null
				};
				await attendanceApi.create(data);
			}

			addToast('Attendance recorded successfully', 'success');
			goto('/analytics');
		} catch (e) {
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
		<a href="/analytics" class="text-gray-500 hover:text-gray-700">
			<svg class="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
				<path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M15 19l-7-7 7-7" />
			</svg>
		</a>
		<h1 class="text-2xl font-bold text-gray-900">Record Mass Attendance</h1>
	</div>

	<form onsubmit={(e) => { e.preventDefault(); handleSubmit(); }} class="bg-white rounded-lg shadow p-6 space-y-6">
		<div>
			<label for="date" class="block text-sm font-medium text-gray-700 mb-1">Date</label>
			<input
				type="date"
				id="date"
				bind:value={date}
				required
				class="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
			/>
		</div>

		<div class="flex items-center gap-2">
			<input
				type="checkbox"
				id="breakdown"
				bind:checked={breakdownByMassTime}
				class="rounded border-gray-300 text-blue-600 focus:ring-blue-500"
			/>
			<label for="breakdown" class="text-sm font-medium text-gray-700">
				Breakdown by Mass Time
			</label>
		</div>

		{#if breakdownByMassTime}
			<div class="space-y-4">
				<p class="text-sm text-gray-500">Enter attendance for each Mass time:</p>
				{#each massEntries as entry, index}
					<div class="flex gap-4 items-end">
						<div class="flex-1">
							<label class="block text-sm font-medium text-gray-700 mb-1">Mass Time</label>
							<input
								type="text"
								placeholder="e.g., 8:00 AM"
								bind:value={entry.mass_time}
								class="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
							/>
						</div>
						<div class="w-32">
							<label class="block text-sm font-medium text-gray-700 mb-1">Count</label>
							<input
								type="number"
								min="0"
								bind:value={entry.attendance_count}
								class="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
							/>
						</div>
						{#if massEntries.length > 1}
							<button
								type="button"
								onclick={() => removeMassEntry(index)}
								class="px-3 py-2 text-red-600 hover:bg-red-50 rounded-lg"
							>
								<svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
									<path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12" />
								</svg>
							</button>
						{/if}
					</div>
				{/each}
				<button
					type="button"
					onclick={addMassEntry}
					class="text-blue-600 hover:text-blue-700 text-sm font-medium"
				>
					+ Add Another Mass Time
				</button>
			</div>
		{:else}
			<div>
				<label for="count" class="block text-sm font-medium text-gray-700 mb-1">Attendance Count</label>
				<input
					type="number"
					id="count"
					min="0"
					bind:value={singleAttendanceCount}
					required
					class="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
				/>
			</div>
		{/if}

		<div>
			<label for="notes" class="block text-sm font-medium text-gray-700 mb-1">Notes (optional)</label>
			<textarea
				id="notes"
				bind:value={notes}
				rows="3"
				class="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
				placeholder="Any additional notes..."
			></textarea>
		</div>

		<div class="flex gap-4">
			<button
				type="submit"
				disabled={submitting}
				class="flex-1 px-6 py-3 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition-colors disabled:opacity-50"
			>
				{submitting ? 'Saving...' : 'Record Attendance'}
			</button>
			<a
				href="/analytics"
				class="px-6 py-3 border border-gray-300 text-gray-700 rounded-lg hover:bg-gray-50 transition-colors text-center"
			>
				Cancel
			</a>
		</div>
	</form>
</div>
