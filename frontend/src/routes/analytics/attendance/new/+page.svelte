<script lang="ts">
	import { onMount } from 'svelte';
	import { goto } from '$app/navigation';
	import { attendanceApi, massTimesApi, type MassAttendanceCreate, type MassTime } from '$lib/api';
	import { addToast } from '$lib/stores/toast';

	let date = $state('');
	let breakdownByMassTime = $state(false);
	let massEntries = $state([{ mass_time: '', attendance_count: 0, customTime: false }]);
	let singleAttendanceCount = $state(0);
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
			massEntries[index].mass_time = '';
		} else {
			massEntries[index].customTime = false;
			massEntries[index].mass_time = value;
		}
	}

	function addMassEntry() {
		massEntries = [...massEntries, { mass_time: '', attendance_count: 0, customTime: false }];
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
							{#if massTimeOptions.length > 0 && !entry.customTime}
								<select
									value={entry.mass_time}
									onchange={(e) => handleMassTimeChange(index, (e.target as HTMLSelectElement).value)}
									class="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
								>
									<option value="">Select mass time...</option>
									{#each massTimeOptions as mt (mt.id)}
										<option value={mt.name}>{mt.name} ({formatTime(mt.time)})</option>
									{/each}
									<option value="__other__">Other (specify)</option>
								</select>
							{:else}
								<div class="flex gap-2">
									<input
										type="text"
										placeholder="e.g., 8:00 AM"
										bind:value={entry.mass_time}
										class="flex-1 px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
									/>
									{#if massTimeOptions.length > 0 && entry.customTime}
										<button
											type="button"
											onclick={() => { entry.customTime = false; entry.mass_time = ''; }}
											class="px-3 py-2 text-gray-500 hover:bg-gray-100 rounded-lg text-sm"
											title="Back to dropdown"
										>
											<svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
												<path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M4 4v5h.582m15.356 2A8.001 8.001 0 004.582 9m0 0H9m11 11v-5h-.581m0 0a8.003 8.003 0 01-15.357-2m15.357 2H15" />
											</svg>
										</button>
									{/if}
								</div>
							{/if}
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
				{#if massTimeOptions.length === 0}
					<p class="text-xs text-gray-400">
						<a href="/settings/mass-times" class="text-blue-600 hover:underline">Configure mass times</a> to use a dropdown instead of free text.
					</p>
				{/if}
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
