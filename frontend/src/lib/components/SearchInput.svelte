<script lang="ts">
	interface Props {
		value: string;
		placeholder?: string;
		onSearch: (value: string) => void;
		debounceMs?: number;
	}

	let { value = '', placeholder = 'Search...', onSearch, debounceMs = 300 }: Props = $props();

	let inputValue = $state(value);
	let timeoutId: ReturnType<typeof setTimeout> | null = null;

	function handleInput(event: Event) {
		const target = event.target as HTMLInputElement;
		inputValue = target.value;

		if (timeoutId) {
			clearTimeout(timeoutId);
		}

		timeoutId = setTimeout(() => {
			onSearch(inputValue);
		}, debounceMs);
	}

	function handleClear() {
		inputValue = '';
		onSearch('');
	}

	$effect(() => {
		inputValue = value;
	});
</script>

<div class="relative">
	<div class="absolute inset-y-0 left-0 pl-3 flex items-center pointer-events-none">
		<svg
			class="h-5 w-5 text-brand-text-muted"
			fill="none"
			stroke="currentColor"
			viewBox="0 0 24 24"
		>
			<path
				stroke-linecap="round"
				stroke-linejoin="round"
				stroke-width="2"
				d="M21 21l-6-6m2-5a7 7 0 11-14 0 7 7 0 0114 0z"
			/>
		</svg>
	</div>
	<input
		type="text"
		value={inputValue}
		oninput={handleInput}
		{placeholder}
		class="block w-full pl-10 pr-10 py-2 border border-brand-border rounded-sm leading-5 bg-white placeholder-brand-text-muted focus:outline-none focus:ring-1 focus:ring-brand-accent focus:border-brand-accent sm:text-sm"
	/>
	{#if inputValue}
		<button
			type="button"
			onclick={handleClear}
			aria-label="Clear search"
			class="absolute inset-y-0 right-0 pr-3 flex items-center text-brand-text-muted hover:text-brand-text-secondary"
		>
			<svg class="h-5 w-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
				<path
					stroke-linecap="round"
					stroke-linejoin="round"
					stroke-width="2"
					d="M6 18L18 6M6 6l12 12"
				/>
			</svg>
		</button>
	{/if}
</div>
