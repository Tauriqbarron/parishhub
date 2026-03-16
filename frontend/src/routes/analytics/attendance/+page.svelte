<script lang="ts">
	import { onMount } from 'svelte';
	import { attendanceApi, type MassAttendance } from '$lib/api';
	import { addToast } from '$lib/stores/toast';

	let records: MassAttendance[] = $state([]);
	let loading = $state(true);
	let page = $state(1);
	let perPage = $state(20);
	let totalPages = $state(0);
	let total = $state(0);
	let startDate = $state('');
	let endDate = $state('');

	// Edit state
	let editingRecord: MassAttendance | null = $state(null);
	let editForm = $state({
		date: '',
		mass_time: '',
		attendance_count: 0,
		notes: ''
	});
	let saving = $state(false);
	let showDeleteConfirm = $state(false);
	let deletingId: number | null = $state(null);

	onMount(() => {
		loadRecords();
	});

	async function loadRecords() {
		loading = true;
		try {
			const filters: { page?: number; per_page?: number; start_date?: string; end_date?: string } =
				{
					page,
					per_page: perPage
				};
			if (startDate) filters.start_date = startDate;
			if (endDate) filters.end_date = endDate;

			const response = await attendanceApi.list(filters);
			records = response.items;
			total = response.total;
			totalPages = response.pages;
		} catch {
			addToast('Failed to load attendance records', 'error');
		} finally {
			loading = false;
		}
	}

	function handlePageChange(newPage: number) {
		page = newPage;
		loadRecords();
	}

	function handleFilter() {
		page = 1;
		loadRecords();
	}

	function clearFilters() {
		startDate = '';
		endDate = '';
		page = 1;
		loadRecords();
	}

	function formatDate(dateStr: string): string {
		return new Date(dateStr).toLocaleDateString('en-US', {
			year: 'numeric',
			month: 'short',
			day: 'numeric'
		});
	}

	function startEdit(record: MassAttendance) {
		editingRecord = record;
		editForm = {
			date: record.date,
			mass_time: record.mass_time || '',
			attendance_count: record.attendance_count,
			notes: record.notes || ''
		};
	}

	function cancelEdit() {
		editingRecord = null;
		showDeleteConfirm = false;
	}

	async function handleSave() {
		if (!editingRecord) return;
		saving = true;
		try {
			await attendanceApi.update(editingRecord.id, {
				date: editForm.date,
				mass_time: editForm.mass_time || null,
				attendance_count: editForm.attendance_count,
				notes: editForm.notes || null
			});
			addToast('Attendance record updated', 'success');
			editingRecord = null;
			await loadRecords();
		} catch {
			addToast('Failed to update record', 'error');
		} finally {
			saving = false;
		}
	}

	async function handleDelete() {
		if (!deletingId) return;
		try {
			await attendanceApi.delete(deletingId);
			addToast('Attendance record deleted', 'success');
			deletingId = null;
			showDeleteConfirm = false;
			editingRecord = null;
			await loadRecords();
		} catch {
			addToast('Failed to delete record', 'error');
		}
	}

	function confirmDelete(id: number) {
		deletingId = id;
		showDeleteConfirm = true;
	}
</script>

<svelte:head>
	<title>Attendance Records - Parish Database</title>
</svelte:head>

<div class="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
	<div class="flex justify-between items-center mb-6">
		<h1 class="text-2xl font-bold text-gray-900">Attendance Records</h1>
		<a
			href="/analytics/attendance/new"
			class="px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition-colors text-sm font-medium"
		>
			Record Attendance
		</a>
	</div>

	<!-- Filters -->
	<div class="bg-white rounded-lg shadow p-4 mb-6">
		<div class="flex flex-wrap items-end gap-4">
			<div>
				<label for="start-date" class="block text-sm font-medium text-gray-700 mb-1">From</label>
				<input
					id="start-date"
					type="date"
					bind:value={startDate}
					class="px-3 py-2 border border-gray-300 rounded-md text-sm focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
				/>
			</div>
			<div>
				<label for="end-date" class="block text-sm font-medium text-gray-700 mb-1">To</label>
				<input
					id="end-date"
					type="date"
					bind:value={endDate}
					class="px-3 py-2 border border-gray-300 rounded-md text-sm focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
				/>
			</div>
			<button
				onclick={handleFilter}
				class="px-4 py-2 bg-blue-600 text-white rounded-md text-sm hover:bg-blue-700 transition-colors"
			>
				Filter
			</button>
			{#if startDate || endDate}
				<button onclick={clearFilters} class="px-4 py-2 text-gray-600 hover:text-gray-800 text-sm">
					Clear
				</button>
			{/if}
		</div>
	</div>

	<!-- Table -->
	<div class="bg-white rounded-lg shadow overflow-hidden">
		{#if loading}
			<div class="flex items-center justify-center h-64">
				<div class="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600"></div>
			</div>
		{:else if records.length === 0}
			<div class="text-center py-12">
				<p class="text-gray-500">No attendance records found</p>
			</div>
		{:else}
			<div class="overflow-x-auto">
				<table class="min-w-full divide-y divide-gray-200">
					<thead class="bg-gray-50">
						<tr>
							<th
								class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider"
							>
								Date
							</th>
							<th
								class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider"
							>
								Mass Time
							</th>
							<th
								class="px-6 py-3 text-right text-xs font-medium text-gray-500 uppercase tracking-wider"
							>
								Attendance
							</th>
							<th
								class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider"
							>
								Notes
							</th>
							<th
								class="px-6 py-3 text-right text-xs font-medium text-gray-500 uppercase tracking-wider"
							>
								Actions
							</th>
						</tr>
					</thead>
					<tbody class="bg-white divide-y divide-gray-200">
						{#each records as record (record.id)}
							<tr class="hover:bg-gray-50">
								<td class="px-6 py-4 whitespace-nowrap text-sm text-gray-900">
									{formatDate(record.date)}
								</td>
								<td class="px-6 py-4 whitespace-nowrap text-sm text-gray-600">
									{record.mass_time || 'Total'}
								</td>
								<td
									class="px-6 py-4 whitespace-nowrap text-sm text-gray-900 text-right font-medium"
								>
									{record.attendance_count}
								</td>
								<td class="px-6 py-4 text-sm text-gray-500 max-w-xs truncate">
									{record.notes || '—'}
								</td>
								<td class="px-6 py-4 whitespace-nowrap text-right text-sm">
									<button
										onclick={() => startEdit(record)}
										class="text-blue-600 hover:text-blue-800 font-medium"
									>
										Edit
									</button>
								</td>
							</tr>
						{/each}
					</tbody>
				</table>
			</div>

			<!-- Pagination -->
			{#if totalPages > 1}
				<div class="px-6 py-4 border-t border-gray-200">
					<div class="flex items-center justify-between">
						<p class="text-sm text-gray-700">
							Showing {(page - 1) * perPage + 1} to {Math.min(page * perPage, total)} of {total} records
						</p>
						<div class="flex gap-2">
							<button
								onclick={() => handlePageChange(page - 1)}
								disabled={page <= 1}
								class="px-3 py-1 text-sm border rounded-md {page <= 1
									? 'text-gray-400 cursor-not-allowed'
									: 'text-gray-700 hover:bg-gray-50'}"
							>
								Previous
							</button>
							<button
								onclick={() => handlePageChange(page + 1)}
								disabled={page >= totalPages}
								class="px-3 py-1 text-sm border rounded-md {page >= totalPages
									? 'text-gray-400 cursor-not-allowed'
									: 'text-gray-700 hover:bg-gray-50'}"
							>
								Next
							</button>
						</div>
					</div>
				</div>
			{/if}
		{/if}
	</div>

	<!-- Summary -->
	{#if !loading && total > 0}
		<p class="mt-4 text-sm text-gray-500">Total records: {total}</p>
	{/if}
</div>

<!-- Edit Modal -->
{#if editingRecord}
	<div class="fixed inset-0 bg-black/50 z-50 flex items-center justify-center p-4">
		<div class="bg-white rounded-lg shadow-xl max-w-md w-full p-6">
			<h2 class="text-lg font-semibold text-gray-900 mb-4">Edit Attendance Record</h2>

			<div class="space-y-4">
				<div>
					<label for="edit-date" class="block text-sm font-medium text-gray-700 mb-1">Date</label>
					<input
						id="edit-date"
						type="date"
						bind:value={editForm.date}
						class="w-full px-3 py-2 border border-gray-300 rounded-md text-sm focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
					/>
				</div>

				<div>
					<label for="edit-mass-time" class="block text-sm font-medium text-gray-700 mb-1"
						>Mass Time</label
					>
					<input
						id="edit-mass-time"
						type="text"
						bind:value={editForm.mass_time}
						placeholder="e.g., 08:00 AM or leave empty for total"
						class="w-full px-3 py-2 border border-gray-300 rounded-md text-sm focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
					/>
				</div>

				<div>
					<label for="edit-count" class="block text-sm font-medium text-gray-700 mb-1"
						>Attendance Count</label
					>
					<input
						id="edit-count"
						type="number"
						min="0"
						bind:value={editForm.attendance_count}
						class="w-full px-3 py-2 border border-gray-300 rounded-md text-sm focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
					/>
				</div>

				<div>
					<label for="edit-notes" class="block text-sm font-medium text-gray-700 mb-1">Notes</label>
					<textarea
						id="edit-notes"
						bind:value={editForm.notes}
						rows="3"
						maxlength="2000"
						class="w-full px-3 py-2 border border-gray-300 rounded-md text-sm focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
					></textarea>
				</div>
			</div>

			<div class="flex items-center justify-between mt-6">
				<button
					onclick={() => confirmDelete(editingRecord!.id)}
					class="px-3 py-2 text-sm text-red-600 hover:text-red-800 hover:bg-red-50 rounded-md transition-colors"
				>
					Delete Record
				</button>
				<div class="flex gap-3">
					<button
						onclick={cancelEdit}
						class="px-4 py-2 text-sm text-gray-700 hover:bg-gray-100 rounded-md transition-colors"
					>
						Cancel
					</button>
					<button
						onclick={handleSave}
						disabled={saving || editForm.attendance_count < 0}
						class="px-4 py-2 text-sm bg-blue-600 text-white rounded-md hover:bg-blue-700 transition-colors disabled:opacity-50 disabled:cursor-not-allowed"
					>
						{saving ? 'Saving...' : 'Save Changes'}
					</button>
				</div>
			</div>
		</div>
	</div>
{/if}

<!-- Delete Confirmation Modal -->
{#if showDeleteConfirm}
	<div class="fixed inset-0 bg-black/50 z-[60] flex items-center justify-center p-4">
		<div class="bg-white rounded-lg shadow-xl max-w-sm w-full p-6">
			<h3 class="text-lg font-semibold text-gray-900 mb-2">Delete Record?</h3>
			<p class="text-sm text-gray-600 mb-6">
				This action cannot be undone. The attendance record will be permanently removed.
			</p>
			<div class="flex justify-end gap-3">
				<button
					onclick={() => {
						showDeleteConfirm = false;
						deletingId = null;
					}}
					class="px-4 py-2 text-sm text-gray-700 hover:bg-gray-100 rounded-md transition-colors"
				>
					Cancel
				</button>
				<button
					onclick={handleDelete}
					class="px-4 py-2 text-sm bg-red-600 text-white rounded-md hover:bg-red-700 transition-colors"
				>
					Delete
				</button>
			</div>
		</div>
	</div>
{/if}
