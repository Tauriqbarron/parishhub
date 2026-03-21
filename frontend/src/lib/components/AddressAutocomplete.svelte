<script lang="ts">
	import { api } from '$lib/api';

	interface AddressResult {
		id: number;
		full_address: string;
		address_number: string | null;
		road_name: string | null;
		road_type_name: string | null;
		suburb_locality: string | null;
		town_city: string | null;
		postcode: string | null;
	}

	interface StructuredAddress {
		address_line1: string;
		address_line2: string;
		city: string;
		postal_code: string;
	}

	interface Props {
		value: string;
		onSelect: (address: StructuredAddress) => void;
		onInput: (value: string) => void;
		id?: string;
		placeholder?: string;
		required?: boolean;
		error?: string;
		disabled?: boolean;
	}

	let {
		value = '',
		onSelect,
		onInput,
		id = 'address',
		placeholder = 'Start typing an address...',
		required = false,
		error = '',
		disabled = false
	}: Props = $props();

	let inputValue = $state(value);
	let searchResults = $state<AddressResult[]>([]);
	let isSearching = $state(false);
	let showDropdown = $state(false);
	let highlightedIndex = $state(-1);
	let searchTimeout: ReturnType<typeof setTimeout>;
	let inputEl: HTMLInputElement;
	let lastPropValue = value; // non-reactive — tracks last seen prop to detect external changes

	// Sync local state only when parent changes value externally (e.g. form reset)
	$effect(() => {
		if (value !== lastPropValue) {
			inputValue = value;
			lastPropValue = value;
		}
	});

	function buildAddressLine1(result: AddressResult): string {
		const parts = [result.address_number, result.road_name, result.road_type_name].filter(Boolean);
		return parts.join(' ') || result.full_address;
	}

	function mapToStructured(result: AddressResult): StructuredAddress {
		return {
			address_line1: buildAddressLine1(result),
			address_line2: result.suburb_locality || '',
			city: result.town_city || '',
			postal_code: result.postcode || ''
		};
	}

	function handleSearchInput() {
		onInput(inputValue);
		showDropdown = true;
		highlightedIndex = -1;

		clearTimeout(searchTimeout);

		if (inputValue.length < 3) {
			searchResults = [];
			return;
		}

		searchTimeout = setTimeout(async () => {
			isSearching = true;
			try {
				searchResults = await api.get<AddressResult[]>(
					`/addresses/search?q=${encodeURIComponent(inputValue)}`
				);
			} catch {
				searchResults = [];
			} finally {
				isSearching = false;
			}
		}, 300);
	}

	function selectAddress(result: AddressResult) {
		const line1 = buildAddressLine1(result);
		inputValue = line1;
		lastPropValue = line1;
		onSelect(mapToStructured(result));
		onInput(line1);
		searchResults = [];
		showDropdown = false;
		highlightedIndex = -1;
	}

	function handleBlur() {
		setTimeout(() => {
			showDropdown = false;
		}, 200);
	}

	function handleKeydown(e: KeyboardEvent) {
		if (!showDropdown || searchResults.length === 0) return;

		if (e.key === 'ArrowDown') {
			e.preventDefault();
			highlightedIndex = (highlightedIndex + 1) % searchResults.length;
		} else if (e.key === 'ArrowUp') {
			e.preventDefault();
			highlightedIndex = highlightedIndex <= 0 ? searchResults.length - 1 : highlightedIndex - 1;
		} else if (e.key === 'Enter' && highlightedIndex >= 0) {
			e.preventDefault();
			selectAddress(searchResults[highlightedIndex]);
		} else if (e.key === 'Escape') {
			showDropdown = false;
			highlightedIndex = -1;
		}
	}
</script>

<div class="relative">
	<input
		type="text"
		{id}
		bind:value={inputValue}
		bind:this={inputEl}
		{required}
		{disabled}
		oninput={handleSearchInput}
		onblur={handleBlur}
		onkeydown={handleKeydown}
		{placeholder}
		aria-label="Address search"
		aria-autocomplete="list"
		role="combobox"
		aria-haspopup="listbox"
		aria-expanded={showDropdown && searchResults.length > 0}
		class="mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-blue-500 focus:ring-blue-500 sm:text-sm
			{error ? 'border-red-500' : ''}"
	/>
	{#if isSearching}
		<div class="absolute right-3 top-3.5" aria-hidden="true">
			<svg class="animate-spin h-5 w-5 text-gray-400" fill="none" viewBox="0 0 24 24" role="img">
				<circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4"
				></circle>
				<path
					class="opacity-75"
					fill="currentColor"
					d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"
				></path>
			</svg>
		</div>
	{/if}

	{#if showDropdown && searchResults.length > 0}
		<div
			class="absolute z-10 mt-1 w-full border border-gray-200 rounded-md shadow-lg bg-white max-h-60 overflow-y-auto"
			role="listbox"
		>
			{#each searchResults as result, i (result.id)}
				<button
					type="button"
					onmousedown={(e) => {
						e.preventDefault();
						selectAddress(result);
					}}
					class="w-full px-4 py-2.5 text-left hover:bg-blue-50 border-b border-gray-100 last:border-b-0 transition-colors
						{i === highlightedIndex ? 'bg-blue-50' : ''}"
					role="option"
					aria-selected={i === highlightedIndex}
				>
					<div class="flex items-start gap-2">
						<svg
							class="w-4 h-4 text-gray-400 flex-shrink-0 mt-0.5"
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
								d="M17.657 16.657L13.414 20.9a1.998 1.998 0 01-2.827 0l-4.244-4.243a8 8 0 1111.314 0z"
							/>
							<path
								stroke-linecap="round"
								stroke-linejoin="round"
								stroke-width="2"
								d="M15 11a3 3 0 11-6 0 3 3 0 016 0z"
							/>
						</svg>
						<span class="text-sm text-gray-900">{result.full_address}</span>
					</div>
				</button>
			{/each}
		</div>
	{/if}
</div>
