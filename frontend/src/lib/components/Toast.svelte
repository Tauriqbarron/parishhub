<script lang="ts">
	import { toasts, type Toast } from '$stores/toast';
	import { fly, fade } from 'svelte/transition';

	const iconPaths: Record<Toast['type'], string> = {
		success: 'M5 13l4 4L19 7',
		error: 'M6 18L18 6M6 6l12 12',
		warning:
			'M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-3L13.732 4c-.77-1.333-2.694-1.333-3.464 0L3.34 16c-.77 1.333.192 3 1.732 3z',
		info: 'M13 16h-1v-4h-1m1-4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z'
	};

	const bgColors: Record<Toast['type'], string> = {
		success: 'bg-green-50 border-green-200',
		error: 'bg-red-50 border-red-200',
		warning: 'bg-yellow-50 border-yellow-200',
		info: 'bg-blue-50 border-blue-200'
	};

	const iconColors: Record<Toast['type'], string> = {
		success: 'text-green-600',
		error: 'text-red-600',
		warning: 'text-yellow-600',
		info: 'text-blue-600'
	};

	const textColors: Record<Toast['type'], string> = {
		success: 'text-green-800',
		error: 'text-red-800',
		warning: 'text-yellow-800',
		info: 'text-blue-800'
	};
</script>

<div class="fixed bottom-4 right-4 z-50 flex flex-col gap-2 max-w-sm w-full pointer-events-none">
	{#each $toasts as toast (toast.id)}
		<div
			class="pointer-events-auto flex items-start gap-3 p-4 rounded-lg border shadow-lg {bgColors[
				toast.type
			]}"
			in:fly={{ x: 100, duration: 300 }}
			out:fade={{ duration: 200 }}
		>
			<svg
				class="w-5 h-5 flex-shrink-0 {iconColors[toast.type]}"
				fill="none"
				stroke="currentColor"
				viewBox="0 0 24 24"
			>
				<path
					stroke-linecap="round"
					stroke-linejoin="round"
					stroke-width="2"
					d={iconPaths[toast.type]}
				/>
			</svg>
			<p class="flex-1 text-sm {textColors[toast.type]}">{toast.message}</p>
			{#if toast.actions?.length}
				<div class="flex gap-2 mt-1">
					{#each toast.actions as action}
						<button
							class="text-sm font-medium underline hover:no-underline"
							onclick={() => {
								action.onClick();
								toasts.remove(toast.id);
							}}
						>
							{action.label}
						</button>
					{/each}
				</div>
			{/if}
			<button
				onclick={() => toasts.remove(toast.id)}
				class="flex-shrink-0 p-1 -m-1 rounded hover:bg-black/5 transition-colors"
				aria-label="Dismiss notification"
			>
				<svg class="w-4 h-4 text-gray-500" fill="none" stroke="currentColor" viewBox="0 0 24 24">
					<path
						stroke-linecap="round"
						stroke-linejoin="round"
						stroke-width="2"
						d="M6 18L18 6M6 6l12 12"
					/>
				</svg>
			</button>
		</div>
	{/each}
</div>
