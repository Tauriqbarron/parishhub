<script lang="ts">
	import { onMount } from 'svelte';
	import { massTimesApi, type MassTime, type MassTimeCreate } from '$lib/api';
	import { addToast } from '$lib/stores/toast';

	const DAYS_OF_WEEK = [
		'Monday',
		'Tuesday',
		'Wednesday',
		'Thursday',
		'Friday',
		'Saturday',
		'Sunday'
	];

	let massTimes: MassTime[] = $state([]);
	let loading = $state(true);
	let showModal = $state(false);
	let editingId: number | null = $state(null);

	let formData = $state<MassTimeCreate>({
		name: '',
		time: '',
		day_of_week: null,
		is_active: true
	});

	onMount(async () => {
		await loadMassTimes();
	});

	async function loadMassTimes() {
		loading = true;
		try {
			massTimes = await massTimesApi.list(false);
		} catch {
			addToast('Failed to load mass times', 'error');
		} finally {
			loading = false;
		}
	}

	function openCreateModal() {
		editingId = null;
		formData = { name: '', time: '', day_of_week: null, is_active: true };
		showModal = true;
	}

	function openEditModal(mt: MassTime) {
		editingId = mt.id;
		formData = {
			name: mt.name,
			time: mt.time,
			day_of_week: mt.day_of_week,
			is_active: mt.is_active
		};
		showModal = true;
	}

	function closeModal() {
		showModal = false;
		editingId = null;
	}

	async function handleSubmit(e: Event) {
		e.preventDefault();
		try {
			if (editingId) {
				await massTimesApi.update(editingId, formData);
				addToast('Mass time updated', 'success');
			} else {
				await massTimesApi.create(formData);
				addToast('Mass time created', 'success');
			}
			closeModal();
			await loadMassTimes();
		} catch {
			addToast('Failed to save mass time', 'error');
		}
	}

	async function handleDelete(id: number) {
		if (!confirm('Deactivate this mass time?')) return;
		try {
			await massTimesApi.delete(id);
			addToast('Mass time deactivated', 'success');
			await loadMassTimes();
		} catch {
			addToast('Failed to deactivate mass time', 'error');
		}
	}

	async function toggleActive(mt: MassTime) {
		try {
			await massTimesApi.update(mt.id, { is_active: !mt.is_active });
			await loadMassTimes();
		} catch {
			addToast('Failed to update mass time', 'error');
		}
	}

	function formatTime(timeStr: string): string {
		const [hours, minutes] = timeStr.split(':');
		const h = parseInt(hours, 10);
		const suffix = h >= 12 ? 'PM' : 'AM';
		const h12 = h % 12 || 12;
		return `${h12}:${minutes} ${suffix}`;
	}
</script>

<div>
	<div class="mb-6 flex flex-col sm:flex-row sm:items-center sm:justify-between gap-4">
		<div>
			<h1 class="text-2xl font-bold text-brand-primary">Mass Times</h1>
			<p class="text-brand-text-secondary mt-1">Configure mass times for attendance tracking</p>
		</div>
		<button
			onclick={openCreateModal}
			class="inline-flex items-center justify-center px-4 py-2 border border-transparent text-sm font-medium rounded-sm text-white bg-brand-accent text-white hover:bg-brand-accent/90 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-brand-accent"
		>
			<svg class="w-5 h-5 mr-2 -ml-1" fill="none" stroke="currentColor" viewBox="0 0 24 24">
				<path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 4v16m8-8H4" />
			</svg>
			Add Mass Time
		</button>
	</div>

	<div class="bg-white rounded-lg border border-brand-border overflow-hidden">
		{#if loading}
			<div class="animate-pulse p-6">
				{#each Array.from({ length: 3 }, (_, i) => i) as i (i)}
					<div class="h-12 bg-brand-bg-muted rounded mb-4"></div>
				{/each}
			</div>
		{:else if massTimes.length === 0}
			<div class="p-6 text-center">
				<svg
					class="mx-auto h-12 w-12 text-brand-text-muted"
					fill="none"
					stroke="currentColor"
					viewBox="0 0 24 24"
				>
					<path
						stroke-linecap="round"
						stroke-linejoin="round"
						stroke-width="2"
						d="M12 8v4l3 3m6-3a9 9 0 11-18 0 9 9 0 0118 0z"
					/>
				</svg>
				<h3 class="mt-2 text-sm font-medium text-brand-primary">No mass times configured</h3>
				<p class="mt-1 text-sm text-brand-text-muted">
					Add mass times to use in attendance tracking.
				</p>
			</div>
		{:else}
			<table class="min-w-full divide-y divide-brand-border">
				<thead class="bg-brand-bg-subtle">
					<tr>
						<th
							class="px-6 py-3 text-left text-xs font-medium text-brand-text-muted uppercase tracking-wider"
							>Name</th
						>
						<th
							class="px-6 py-3 text-left text-xs font-medium text-brand-text-muted uppercase tracking-wider"
							>Time</th
						>
						<th
							class="px-6 py-3 text-left text-xs font-medium text-brand-text-muted uppercase tracking-wider"
							>Day</th
						>
						<th
							class="px-6 py-3 text-left text-xs font-medium text-brand-text-muted uppercase tracking-wider"
							>Status</th
						>
						<th
							class="px-6 py-3 text-right text-xs font-medium text-brand-text-muted uppercase tracking-wider"
							>Actions</th
						>
					</tr>
				</thead>
				<tbody class="bg-white divide-y divide-brand-border">
					{#each massTimes as mt (mt.id)}
						<tr class={mt.is_active ? '' : 'bg-brand-bg-subtle opacity-60'}>
							<td class="px-6 py-4 whitespace-nowrap text-sm font-medium text-brand-primary"
								>{mt.name}</td
							>
							<td class="px-6 py-4 whitespace-nowrap text-sm text-brand-text-muted"
								>{formatTime(mt.time)}</td
							>
							<td class="px-6 py-4 whitespace-nowrap text-sm text-brand-text-muted">
								{mt.day_of_week !== null ? DAYS_OF_WEEK[mt.day_of_week] : 'Any'}
							</td>
							<td class="px-6 py-4 whitespace-nowrap">
								<button
									onclick={() => toggleActive(mt)}
									class="inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium {mt.is_active
										? 'bg-green-100 text-green-800'
										: 'bg-brand-bg-muted text-brand-primary'}"
								>
									{mt.is_active ? 'Active' : 'Inactive'}
								</button>
							</td>
							<td class="px-6 py-4 whitespace-nowrap text-right text-sm font-medium">
								<button
									onclick={() => openEditModal(mt)}
									class="text-blue-600 hover:text-blue-900 mr-4">Edit</button
								>
								{#if mt.is_active}
									<button
										onclick={() => handleDelete(mt.id)}
										class="text-red-600 hover:text-red-900">Deactivate</button
									>
								{/if}
							</td>
						</tr>
					{/each}
				</tbody>
			</table>
		{/if}
	</div>
</div>

{#if showModal}
	<div class="fixed inset-0 z-50 overflow-y-auto">
		<div class="flex min-h-full items-center justify-center p-4">
			<div class="fixed inset-0 bg-brand-bg-subtle0 bg-opacity-75" onclick={closeModal}></div>
			<div class="relative bg-white rounded-lg shadow-xl max-w-md w-full p-6">
				<h3 class="text-lg font-medium text-brand-primary mb-4">
					{editingId ? 'Edit Mass Time' : 'Add Mass Time'}
				</h3>
				<form onsubmit={handleSubmit}>
					<div class="space-y-4">
						<div>
							<label for="name" class="block text-sm font-medium text-brand-text-secondary"
								>Name</label
							>
							<input
								type="text"
								id="name"
								bind:value={formData.name}
								required
								maxlength="100"
								placeholder="e.g., 8:00 AM Sunday Mass"
								class="mt-1 block w-full rounded-sm border-brand-border shadow-sm focus:border-blue-500 focus:ring-blue-500 sm:text-sm"
							/>
						</div>
						<div>
							<label for="time" class="block text-sm font-medium text-brand-text-secondary"
								>Time</label
							>
							<input
								type="time"
								id="time"
								bind:value={formData.time}
								required
								class="mt-1 block w-full rounded-sm border-brand-border shadow-sm focus:border-blue-500 focus:ring-blue-500 sm:text-sm"
							/>
						</div>
						<div>
							<label for="day" class="block text-sm font-medium text-brand-text-secondary"
								>Day of Week</label
							>
							<select
								id="day"
								bind:value={formData.day_of_week}
								class="mt-1 block w-full rounded-sm border-brand-border shadow-sm focus:border-blue-500 focus:ring-blue-500 sm:text-sm"
							>
								<option value={null}>Any day</option>
								{#each DAYS_OF_WEEK as day, i (i)}
									<option value={i}>{day}</option>
								{/each}
							</select>
						</div>
						{#if editingId}
							<div class="flex items-center">
								<input
									type="checkbox"
									id="is_active"
									bind:checked={formData.is_active}
									class="h-4 w-4 text-blue-600 focus:ring-blue-500 border-brand-border rounded"
								/>
								<label for="is_active" class="ml-2 block text-sm text-brand-primary">Active</label>
							</div>
						{/if}
					</div>
					<div class="mt-6 flex justify-end gap-3">
						<button
							type="button"
							onclick={closeModal}
							class="px-4 py-2 text-sm font-medium text-brand-text-secondary bg-white border border-brand-border rounded-sm hover:bg-brand-bg-subtle"
						>
							Cancel
						</button>
						<button
							type="submit"
							class="px-4 py-2 text-sm font-medium text-white bg-blue-600 border border-transparent rounded-sm hover:bg-blue-700"
						>
							{editingId ? 'Update' : 'Create'}
						</button>
					</div>
				</form>
			</div>
		</div>
	</div>
{/if}
