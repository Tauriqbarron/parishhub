<script lang="ts">
	import { personApi, type Person } from '$lib/api';

	type LinkedPerson = { id: number; name: string };
	type ManualPerson = { name: string };
	type PersonValue = LinkedPerson | ManualPerson | null;

	interface Props {
		value: PersonValue;
		placeholder?: string;
		excludeIds?: number[];
		onSelect: (selection: PersonValue) => void;
	}

	let { value = null, placeholder = 'Search for a person...', excludeIds = [], onSelect }: Props = $props();

	let searchQuery = $state('');
	let searchResults = $state<Person[]>([]);
	let isSearching = $state(false);
	let showDropdown = $state(false);
	let searchTimeout: ReturnType<typeof setTimeout>;

	function isLinkedPerson(v: PersonValue): v is LinkedPerson {
		return v !== null && 'id' in v;
	}

	function formatPersonName(person: Person): string {
		const middle = person.middle_name ? ` ${person.middle_name}` : '';
		return `${person.first_name}${middle} ${person.last_name}`;
	}

	function handleSearchInput(e: Event) {
		const inputValue = (e.target as HTMLInputElement).value;
		searchQuery = inputValue;
		showDropdown = true;

		clearTimeout(searchTimeout);

		if (inputValue.length < 2) {
			searchResults = [];
			return;
		}

		searchTimeout = setTimeout(async () => {
			isSearching = true;
			try {
				const response = await personApi.list({ search: inputValue, per_page: 10 });
				searchResults = response.items.filter((p) => !excludeIds.includes(p.id));
			} catch {
				searchResults = [];
			} finally {
				isSearching = false;
			}
		}, 300);
	}

	function selectPerson(person: Person) {
		const selection: LinkedPerson = { id: person.id, name: formatPersonName(person) };
		onSelect(selection);
		searchQuery = '';
		searchResults = [];
		showDropdown = false;
	}

	function useManualEntry() {
		if (searchQuery.trim()) {
			const selection: ManualPerson = { name: searchQuery.trim() };
			onSelect(selection);
			searchResults = [];
			showDropdown = false;
		}
	}

	function clearSelection() {
		onSelect(null);
		searchQuery = '';
		searchResults = [];
	}

	function handleBlur() {
		setTimeout(() => {
			showDropdown = false;
		}, 200);
	}

	function handleKeydown(e: KeyboardEvent) {
		if (e.key === 'Enter' && searchQuery.trim() && searchResults.length === 0) {
			e.preventDefault();
			useManualEntry();
		}
	}
</script>

{#if value}
	<div class="flex items-center justify-between p-3 rounded-lg border {isLinkedPerson(value) ? 'border-blue-200 bg-blue-50' : 'border-gray-200 bg-gray-50'}">
		<div class="flex items-center gap-3">
			<div class="p-2 bg-white rounded-lg shadow-sm">
				{#if isLinkedPerson(value)}
					<svg class="w-5 h-5 text-blue-600" fill="none" stroke="currentColor" viewBox="0 0 24 24" aria-hidden="true" role="img">
						<path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M13.828 10.172a4 4 0 00-5.656 0l-4 4a4 4 0 105.656 5.656l1.102-1.101m-.758-4.899a4 4 0 005.656 0l4-4a4 4 0 00-5.656-5.656l-1.1 1.1" />
					</svg>
				{:else}
					<svg class="w-5 h-5 text-gray-600" fill="none" stroke="currentColor" viewBox="0 0 24 24" aria-hidden="true" role="img">
						<path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M11 5H6a2 2 0 00-2 2v11a2 2 0 002 2h11a2 2 0 002-2v-5m-1.414-9.414a2 2 0 112.828 2.828L11.828 15H9v-2.828l8.586-8.586z" />
					</svg>
				{/if}
			</div>
			<div>
				<div class="font-medium text-gray-900">{value.name}</div>
				<div class="text-xs text-gray-500">
					{isLinkedPerson(value) ? 'Linked to database' : 'Manual entry'}
				</div>
			</div>
		</div>
		<button
			type="button"
			onclick={clearSelection}
			class="p-1.5 rounded hover:bg-gray-200 text-gray-600 transition-colors"
			aria-label="Clear selection"
		>
			<svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24" aria-hidden="true" role="img">
				<path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12" />
			</svg>
		</button>
	</div>
{:else}
	<div class="relative">
		<input
			type="text"
			value={searchQuery}
			oninput={handleSearchInput}
			onblur={handleBlur}
			onkeydown={handleKeydown}
			{placeholder}
			aria-label="Search for a person"
			aria-autocomplete="list"
			aria-expanded={showDropdown && (searchResults.length > 0 || searchQuery.length >= 2)}
			class="block w-full rounded-md border-gray-300 shadow-sm focus:border-blue-500 focus:ring-blue-500 sm:text-sm"
		/>
		{#if isSearching}
			<div class="absolute right-3 top-2.5" aria-hidden="true">
				<svg class="animate-spin h-5 w-5 text-gray-400" fill="none" viewBox="0 0 24 24" role="img">
					<circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4"></circle>
					<path class="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
				</svg>
			</div>
		{/if}

		{#if showDropdown && (searchResults.length > 0 || (searchQuery.length >= 2 && !isSearching))}
			<div class="absolute z-10 mt-1 w-full border border-gray-200 rounded-md shadow-lg bg-white max-h-48 overflow-y-auto" role="listbox">
				{#each searchResults as person (person.id)}
					<button
						type="button"
						onclick={() => selectPerson(person)}
						class="w-full px-4 py-2 text-left hover:bg-gray-50 border-b border-gray-100 last:border-b-0"
						role="option"
						aria-selected="false"
					>
						<div class="flex items-center gap-2">
							<svg class="w-4 h-4 text-blue-500 flex-shrink-0" fill="none" stroke="currentColor" viewBox="0 0 24 24" aria-hidden="true" role="img">
								<path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M13.828 10.172a4 4 0 00-5.656 0l-4 4a4 4 0 105.656 5.656l1.102-1.101m-.758-4.899a4 4 0 005.656 0l4-4a4 4 0 00-5.656-5.656l-1.1 1.1" />
							</svg>
							<div>
								<div class="font-medium text-gray-900">{formatPersonName(person)}</div>
								{#if person.email}
									<div class="text-sm text-gray-500">{person.email}</div>
								{/if}
							</div>
						</div>
					</button>
				{/each}
				{#if searchQuery.trim().length >= 2}
					<button
						type="button"
						onclick={useManualEntry}
						class="w-full px-4 py-2 text-left hover:bg-gray-50 border-t border-gray-200"
						role="option"
						aria-selected="false"
					>
						<div class="flex items-center gap-2">
							<svg class="w-4 h-4 text-gray-500 flex-shrink-0" fill="none" stroke="currentColor" viewBox="0 0 24 24" aria-hidden="true" role="img">
								<path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M11 5H6a2 2 0 00-2 2v11a2 2 0 002 2h11a2 2 0 002-2v-5m-1.414-9.414a2 2 0 112.828 2.828L11.828 15H9v-2.828l8.586-8.586z" />
							</svg>
							<div>
								<div class="text-gray-700">Use "<span class="font-medium">{searchQuery.trim()}</span>" as manual entry</div>
							</div>
						</div>
					</button>
				{/if}
			</div>
		{/if}
	</div>
{/if}
