<script lang="ts">
	import type { Sacrament, SacramentType } from '$lib/api';

	interface Props {
		sacraments: Sacrament[];
		onAdd: () => void;
		onEdit: (sacrament: Sacrament) => void;
		onDelete: (sacrament: Sacrament) => void;
	}

	let { sacraments, onAdd, onEdit, onDelete }: Props = $props();

	const sacramentOrder: SacramentType[] = [
		'baptism',
		'first_communion',
		'confirmation',
		'marriage',
		'holy_orders'
	];

	const sacramentLabels: Record<SacramentType, string> = {
		baptism: 'Baptism',
		first_communion: 'First Communion',
		confirmation: 'Confirmation',
		marriage: 'Marriage',
		holy_orders: 'Holy Orders'
	};

	const sacramentColors: Record<SacramentType, { bg: string; text: string; border: string }> = {
		baptism: { bg: 'bg-blue-50', text: 'text-blue-700', border: 'border-blue-200' },
		first_communion: { bg: 'bg-purple-50', text: 'text-purple-700', border: 'border-purple-200' },
		confirmation: { bg: 'bg-green-50', text: 'text-green-700', border: 'border-green-200' },
		marriage: { bg: 'bg-pink-50', text: 'text-pink-700', border: 'border-pink-200' },
		holy_orders: { bg: 'bg-amber-50', text: 'text-amber-700', border: 'border-amber-200' }
	};

	function formatDate(date: string): string {
		return new Date(date).toLocaleDateString('en-NZ', {
			year: 'numeric',
			month: 'short',
			day: 'numeric'
		});
	}

	function getSacramentByType(type: SacramentType): Sacrament | undefined {
		return sacraments.find((s) => s.sacrament_type === type);
	}

	const receivedTypes = $derived(new Set(sacraments.map((s) => s.sacrament_type)));
</script>

<div class="bg-white rounded-lg shadow">
	<div class="px-6 py-4 border-b border-gray-200 flex items-center justify-between">
		<h2 class="text-lg font-medium text-gray-900">Sacraments</h2>
		<button
			onclick={onAdd}
			class="inline-flex items-center px-3 py-1.5 text-sm font-medium text-blue-600 bg-blue-50 rounded-md hover:bg-blue-100 transition-colors"
		>
			<svg class="w-4 h-4 mr-1" fill="none" stroke="currentColor" viewBox="0 0 24 24">
				<path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 4v16m8-8H4" />
			</svg>
			Add
		</button>
	</div>
	<div class="px-6 py-4">
		<div class="space-y-3">
			{#each sacramentOrder as type (type)}
				{@const sacrament = getSacramentByType(type)}
				{@const colors = sacramentColors[type]}
				<div
					class="flex items-center justify-between p-3 rounded-lg border {sacrament
						? colors.bg + ' ' + colors.border
						: 'bg-gray-50 border-gray-200'}"
				>
					<div class="flex items-center gap-3">
						<!-- Status indicator -->
						<div
							class="w-6 h-6 rounded-full flex items-center justify-center {sacrament
								? colors.bg + ' ' + colors.text
								: 'bg-gray-200 text-gray-400'}"
						>
							{#if sacrament}
								<svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
									<path
										stroke-linecap="round"
										stroke-linejoin="round"
										stroke-width="2"
										d="M5 13l4 4L19 7"
									/>
								</svg>
							{:else}
								<svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
									<path
										stroke-linecap="round"
										stroke-linejoin="round"
										stroke-width="2"
										d="M20 12H4"
									/>
								</svg>
							{/if}
						</div>

						<div>
							<div class="font-medium {sacrament ? colors.text : 'text-gray-500'}">
								{sacramentLabels[type]}
							</div>
							{#if sacrament}
								<div class="text-sm {colors.text} opacity-75">
									{formatDate(sacrament.date_received)}
									{#if sacrament.notes}
										<span class="mx-1">-</span>
										<span class="italic">{sacrament.notes}</span>
									{/if}
								</div>
							{:else}
								<div class="text-sm text-gray-400">Not received</div>
							{/if}
						</div>
					</div>

					{#if sacrament}
						<div class="flex items-center gap-1">
							<button
								onclick={() => onEdit(sacrament)}
								class="p-1.5 rounded hover:bg-white/50 {colors.text} transition-colors"
								title="Edit"
							>
								<svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
									<path
										stroke-linecap="round"
										stroke-linejoin="round"
										stroke-width="2"
										d="M11 5H6a2 2 0 00-2 2v11a2 2 0 002 2h11a2 2 0 002-2v-5m-1.414-9.414a2 2 0 112.828 2.828L11.828 15H9v-2.828l8.586-8.586z"
									/>
								</svg>
							</button>
							<button
								onclick={() => onDelete(sacrament)}
								class="p-1.5 rounded hover:bg-red-100 text-red-600 transition-colors"
								title="Delete"
							>
								<svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
									<path
										stroke-linecap="round"
										stroke-linejoin="round"
										stroke-width="2"
										d="M19 7l-.867 12.142A2 2 0 0116.138 21H7.862a2 2 0 01-1.995-1.858L5 7m5 4v6m4-6v6m1-10V4a1 1 0 00-1-1h-4a1 1 0 00-1 1v3M4 7h16"
									/>
								</svg>
							</button>
						</div>
					{/if}
				</div>
			{/each}
		</div>
	</div>
</div>
