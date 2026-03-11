<script lang="ts">
	import type { DeathWithPerson } from '$lib/api';

	interface Props {
		death: DeathWithPerson;
		onEdit: () => void;
		onDelete: () => void;
	}

	let { death, onEdit, onDelete }: Props = $props();

	function formatDate(dateStr: string): string {
		return new Date(dateStr).toLocaleDateString('en-NZ', {
			year: 'numeric',
			month: 'long',
			day: 'numeric'
		});
	}
</script>

<div class="bg-white rounded-lg shadow border border-red-100 overflow-hidden">
	<div class="px-6 py-4 bg-red-50 border-b border-red-100 flex items-center justify-between">
		<div class="flex items-center gap-2">
			<svg
				class="w-5 h-5 text-red-600"
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
					d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-3L13.732 4c-.77-1.333-2.694-1.333-3.464 0L3.34 16c-.77 1.333.192 3 1.732 3z"
				/>
			</svg>
			<h2 class="text-lg font-semibold text-red-900">Death Record</h2>
		</div>
		<div class="flex items-center gap-2">
			<button
				onclick={onEdit}
				class="p-1.5 rounded text-red-600 hover:bg-red-100 transition-colors"
				aria-label="Edit death record"
			>
				<svg
					class="w-4 h-4"
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
						d="M11 5H6a2 2 0 00-2 2v11a2 2 0 002 2h11a2 2 0 002-2v-5m-1.414-9.414a2 2 0 112.828 2.828L11.828 15H9v-2.828l8.586-8.586z"
					/>
				</svg>
			</button>
			<button
				onclick={onDelete}
				class="p-1.5 rounded text-red-600 hover:bg-red-200 transition-colors"
				aria-label="Delete death record"
			>
				<svg
					class="w-4 h-4"
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
						d="M19 7l-.867 12.142A2 2 0 0116.138 21H7.862a2 2 0 01-1.995-1.858L5 7m5 4v6m4-6v6m1-10V4a1 1 0 00-1-1h-4a1 1 0 00-1 1v3M4 7h16"
					/>
				</svg>
			</button>
		</div>
	</div>

	<div class="px-6 py-6 grid grid-cols-1 md:grid-cols-2 gap-y-6 gap-x-12">
		<!-- Main Death Info -->
		<div class="space-y-4">
			<div>
				<h3 class="text-xs font-semibold text-gray-500 uppercase tracking-wider">Date of Death</h3>
				<p class="mt-1 text-base text-gray-900 font-medium">
					{formatDate(death.date_of_death)}
				</p>
			</div>

			{#if death.place_of_death}
				<div>
					<h3 class="text-xs font-semibold text-gray-500 uppercase tracking-wider">
						Place of Death
					</h3>
					<p class="mt-1 text-base text-gray-900">{death.place_of_death}</p>
				</div>
			{/if}

			{#if death.cause_of_death}
				<div>
					<h3 class="text-xs font-semibold text-gray-500 uppercase tracking-wider">
						Cause of Death
					</h3>
					<p class="mt-1 text-base text-gray-900">{death.cause_of_death}</p>
				</div>
			{/if}
		</div>

		<!-- Funeral & Burial Info -->
		<div class="space-y-4">
			{#if death.funeral_date || death.funeral_location}
				<div>
					<h3 class="text-xs font-semibold text-gray-500 uppercase tracking-wider">Funeral</h3>
					<p class="mt-1 text-base text-gray-900">
						{#if death.funeral_date}
							{formatDate(death.funeral_date)}
						{/if}
						{#if death.funeral_location}
							{#if death.funeral_date}<br />{/if}
							{death.funeral_location}
						{/if}
					</p>
				</div>
			{/if}

			{#if death.burial_date || death.burial_location}
				<div>
					<h3 class="text-xs font-semibold text-gray-500 uppercase tracking-wider">Burial</h3>
					<p class="mt-1 text-base text-gray-900">
						{#if death.burial_date}
							{formatDate(death.burial_date)}
						{/if}
						{#if death.burial_location}
							{#if death.burial_date}<br />{/if}
							{death.burial_location}
						{/if}
					</p>
				</div>
			{/if}

			{#if death.officiating_priest}
				<div>
					<h3 class="text-xs font-semibold text-gray-500 uppercase tracking-wider">
						Officiating Priest
					</h3>
					<p class="mt-1 text-base text-gray-900">
						<a href="/people/{death.officiating_priest.id}" class="text-blue-600 hover:underline">
							{death.officiating_priest.first_name} {death.officiating_priest.last_name}
						</a>
					</p>
				</div>
			{:else if death.officiating_priest_id}
				<div>
					<h3 class="text-xs font-semibold text-gray-500 uppercase tracking-wider">
						Officiating Priest
					</h3>
					<p class="mt-1 text-base text-gray-900 italic text-gray-500">
						Priest ID: {death.officiating_priest_id}
					</p>
				</div>
			{/if}
		</div>

		<!-- Notes -->
		{#if death.notes}
			<div class="col-span-full pt-4 border-t border-gray-100">
				<h3 class="text-xs font-semibold text-gray-500 uppercase tracking-wider">Notes</h3>
				<p class="mt-1 text-sm text-gray-700 whitespace-pre-line">{death.notes}</p>
			</div>
		{/if}
	</div>
</div>
