<script lang="ts">
	import { toasts, type Toast } from '$stores/toast';
	import { fly, fade } from 'svelte/transition';
	import { CheckCircle2, XCircle, AlertTriangle, Info, X } from 'lucide-svelte';
	import type { Component } from 'svelte';

	const icons: Record<Toast['type'], Component> = {
		success: CheckCircle2,
		error: XCircle,
		warning: AlertTriangle,
		info: Info
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
			<svelte:component
				this={icons[toast.type]}
				class="w-5 h-5 flex-shrink-0 {iconColors[toast.type]}"
			/>
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
				<X class="w-4 h-4 text-gray-500" />
			</button>
		</div>
	{/each}
</div>
