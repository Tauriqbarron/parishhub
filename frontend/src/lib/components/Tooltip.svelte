<script lang="ts">
	interface Props {
		text: string;
		position?: 'top' | 'bottom' | 'left' | 'right';
	}

	let { text, position = 'right' }: Props = $props();
	let showTooltip = $state(false);

	const positionClasses = $derived({
		top: 'bottom-full left-1/2 -translate-x-1/2 mb-2',
		bottom: 'top-full left-1/2 -translate-x-1/2 mt-2',
		left: 'right-full top-1/2 -translate-y-1/2 mr-2',
		right: 'left-full top-1/2 -translate-y-1/2 ml-2'
	}[position]);

	const arrowClasses = $derived({
		top: 'top-full left-1/2 -translate-x-1/2 -mt-1 border-t-gray-800 border-x-transparent border-b-transparent border-4',
		bottom: 'bottom-full left-1/2 -translate-x-1/2 -mb-1 border-b-gray-800 border-x-transparent border-t-transparent border-4',
		left: 'left-full top-1/2 -translate-y-1/2 -ml-1 border-l-gray-800 border-y-transparent border-r-transparent border-4',
		right: 'right-full top-1/2 -translate-y-1/2 -mr-1 border-r-gray-800 border-y-transparent border-l-transparent border-4'
	}[position]);
</script>

<div class="relative inline-block ml-1">
	<button
		type="button"
		class="w-4 h-4 rounded-full bg-gray-200 text-gray-600 text-xs flex items-center justify-center hover:bg-gray-300 focus:outline-none focus:ring-2 focus:ring-blue-500"
		onmouseenter={() => (showTooltip = true)}
		onmouseleave={() => (showTooltip = false)}
		onfocus={() => (showTooltip = true)}
		onblur={() => (showTooltip = false)}
		aria-label="More information"
	>
		?
	</button>
	{#if showTooltip}
		<div
			class="absolute z-10 px-3 py-2 text-sm text-white bg-gray-800 rounded-md shadow-lg w-48 {positionClasses}"
			role="tooltip"
		>
			{text}
			<div class="absolute w-0 h-0 {arrowClasses}"></div>
		</div>
	{/if}
</div>
