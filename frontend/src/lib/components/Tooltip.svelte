<script lang="ts">
	interface Props {
		text: string;
	}

	let { text }: Props = $props();
	let showTooltip = $state(false);
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
			class="absolute z-10 px-3 py-2 text-sm text-white bg-gray-800 rounded-md shadow-lg -top-2 left-6 w-48"
			role="tooltip"
		>
			{text}
			<div
				class="absolute w-2 h-2 bg-gray-800 transform rotate-45 -left-1 top-3"
			></div>
		</div>
	{/if}
</div>
