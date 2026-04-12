<script lang="ts">
	import { goto } from '$app/navigation';
	import { birthsApi, personApi, type BirthCreate, type Person } from '$lib/api';
	import { addToast } from '$lib/stores/toast';

	let babyFirstName = $state('');
	let babyLastName = $state('');
	let dateOfBirth = $state('');
	let notes = $state('');
	let submitting = $state(false);

	// Parent search state
	let parent1Search = $state('');
	let parent2Search = $state('');
	let parent1Id: number | null = $state(null);
	let parent2Id: number | null = $state(null);
	let parent1Name = $state('');
	let parent2Name = $state('');
	let parent1Results: Person[] = $state([]);
	let parent2Results: Person[] = $state([]);
	let showParent1Dropdown = $state(false);
	let showParent2Dropdown = $state(false);

	async function searchParent1(query: string) {
		parent1Search = query;
		if (query.length < 2) {
			parent1Results = [];
			return;
		}
		try {
			const response = await personApi.list({ search: query, per_page: 5 });
			parent1Results = response.items;
			showParent1Dropdown = true;
		} catch {
			parent1Results = [];
		}
	}

	async function searchParent2(query: string) {
		parent2Search = query;
		if (query.length < 2) {
			parent2Results = [];
			return;
		}
		try {
			const response = await personApi.list({ search: query, per_page: 5 });
			parent2Results = response.items;
			showParent2Dropdown = true;
		} catch {
			parent2Results = [];
		}
	}

	function selectParent1(person: Person) {
		parent1Id = person.id;
		parent1Name = `${person.first_name} ${person.last_name}`;
		parent1Search = parent1Name;
		showParent1Dropdown = false;
		parent1Results = [];
	}

	function selectParent2(person: Person) {
		parent2Id = person.id;
		parent2Name = `${person.first_name} ${person.last_name}`;
		parent2Search = parent2Name;
		showParent2Dropdown = false;
		parent2Results = [];
	}

	function clearParent1() {
		parent1Id = null;
		parent1Name = '';
		parent1Search = '';
	}

	function clearParent2() {
		parent2Id = null;
		parent2Name = '';
		parent2Search = '';
	}

	async function handleSubmit() {
		if (!babyFirstName || !babyLastName || !dateOfBirth) {
			addToast('Please fill in all required fields', 'error');
			return;
		}

		submitting = true;
		try {
			const data: BirthCreate = {
				baby_first_name: babyFirstName,
				baby_last_name: babyLastName,
				date_of_birth: dateOfBirth,
				parent1_id: parent1Id,
				parent2_id: parent2Id,
				notes: notes || null
			};
			await birthsApi.create(data);
			addToast('Birth recorded successfully', 'success');
			goto('/analytics');
		} catch {
			addToast('Failed to record birth', 'error');
		} finally {
			submitting = false;
		}
	}
</script>

<svelte:head>
	<title>Record Birth - Parish Database</title>
</svelte:head>

<div class="max-w-2xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
	<div class="flex items-center gap-4 mb-8">
		<a href="/analytics" class="text-brand-text-muted hover:text-brand-text-secondary">
			<svg class="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
				<path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M15 19l-7-7 7-7" />
			</svg>
		</a>
		<h1 class="text-2xl font-bold text-brand-primary">Record Birth</h1>
	</div>

	<form
		onsubmit={(e) => {
			e.preventDefault();
			handleSubmit();
		}}
		class="bg-white rounded-lg shadow p-6 space-y-6"
	>
		<!-- Baby Name -->
		<div class="grid grid-cols-2 gap-4">
			<div>
				<label for="firstName" class="block text-sm font-medium text-brand-text-secondary mb-1">
					Baby First Name <span class="text-brand-error">*</span>
				</label>
				<input
					type="text"
					id="firstName"
					bind:value={babyFirstName}
					required
					class="w-full px-3 py-2 border border-brand-border rounded-lg focus:ring-2 focus:ring-brand-accent focus:border-transparent"
				/>
			</div>
			<div>
				<label for="lastName" class="block text-sm font-medium text-brand-text-secondary mb-1">
					Baby Last Name <span class="text-brand-error">*</span>
				</label>
				<input
					type="text"
					id="lastName"
					bind:value={babyLastName}
					required
					class="w-full px-3 py-2 border border-brand-border rounded-lg focus:ring-2 focus:ring-brand-accent focus:border-transparent"
				/>
			</div>
		</div>

		<!-- Date of Birth -->
		<div>
			<label for="dob" class="block text-sm font-medium text-brand-text-secondary mb-1">
				Date of Birth <span class="text-brand-error">*</span>
			</label>
			<input
				type="date"
				id="dob"
				bind:value={dateOfBirth}
				required
				class="w-full px-3 py-2 border border-brand-border rounded-lg focus:ring-2 focus:ring-brand-accent focus:border-transparent"
			/>
		</div>

		<!-- Parent 1 Search -->
		<div class="relative">
			<label for="parent1" class="block text-sm font-medium text-brand-text-secondary mb-1">
				Parent 1 (optional)
			</label>
			{#if parent1Id}
				<div
					class="flex items-center gap-2 px-3 py-2 bg-brand-bg-subtle border-brand-border rounded-lg"
				>
					<span class="flex-1">{parent1Name}</span>
					<button
						type="button"
						onclick={clearParent1}
						class="text-brand-text-muted hover:text-brand-text-secondary"
					>
						<svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
							<path
								stroke-linecap="round"
								stroke-linejoin="round"
								stroke-width="2"
								d="M6 18L18 6M6 6l12 12"
							/>
						</svg>
					</button>
				</div>
			{:else}
				<input
					type="text"
					id="parent1"
					value={parent1Search}
					oninput={(e) => searchParent1((e.target as HTMLInputElement).value)}
					onfocus={() => parent1Results.length > 0 && (showParent1Dropdown = true)}
					onblur={() => setTimeout(() => (showParent1Dropdown = false), 200)}
					placeholder="Search by name..."
					class="w-full px-3 py-2 border border-brand-border rounded-lg focus:ring-2 focus:ring-brand-accent focus:border-transparent"
				/>
				{#if showParent1Dropdown && parent1Results.length > 0}
					<div
						class="absolute z-10 w-full mt-1 bg-white border border-brand-border rounded-lg shadow-lg max-h-48 overflow-auto"
					>
						{#each parent1Results as person}
							<button
								type="button"
								onclick={() => selectParent1(person)}
								class="w-full px-4 py-2 text-left hover:bg-brand-bg-muted focus:bg-brand-bg-muted"
							>
								{person.first_name}
								{person.last_name}
							</button>
						{/each}
					</div>
				{/if}
			{/if}
		</div>

		<!-- Parent 2 Search -->
		<div class="relative">
			<label for="parent2" class="block text-sm font-medium text-brand-text-secondary mb-1">
				Parent 2 (optional)
			</label>
			{#if parent2Id}
				<div
					class="flex items-center gap-2 px-3 py-2 bg-brand-bg-subtle border-brand-border rounded-lg"
				>
					<span class="flex-1">{parent2Name}</span>
					<button
						type="button"
						onclick={clearParent2}
						class="text-brand-text-muted hover:text-brand-text-secondary"
					>
						<svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
							<path
								stroke-linecap="round"
								stroke-linejoin="round"
								stroke-width="2"
								d="M6 18L18 6M6 6l12 12"
							/>
						</svg>
					</button>
				</div>
			{:else}
				<input
					type="text"
					id="parent2"
					value={parent2Search}
					oninput={(e) => searchParent2((e.target as HTMLInputElement).value)}
					onfocus={() => parent2Results.length > 0 && (showParent2Dropdown = true)}
					onblur={() => setTimeout(() => (showParent2Dropdown = false), 200)}
					placeholder="Search by name..."
					class="w-full px-3 py-2 border border-brand-border rounded-lg focus:ring-2 focus:ring-brand-accent focus:border-transparent"
				/>
				{#if showParent2Dropdown && parent2Results.length > 0}
					<div
						class="absolute z-10 w-full mt-1 bg-white border border-brand-border rounded-lg shadow-lg max-h-48 overflow-auto"
					>
						{#each parent2Results as person}
							<button
								type="button"
								onclick={() => selectParent2(person)}
								class="w-full px-4 py-2 text-left hover:bg-brand-bg-muted focus:bg-brand-bg-muted"
							>
								{person.first_name}
								{person.last_name}
							</button>
						{/each}
					</div>
				{/if}
			{/if}
		</div>

		<!-- Notes -->
		<div>
			<label for="notes" class="block text-sm font-medium text-brand-text-secondary mb-1"
				>Notes (optional)</label
			>
			<textarea
				id="notes"
				bind:value={notes}
				rows="3"
				class="w-full px-3 py-2 border border-brand-border rounded-lg focus:ring-2 focus:ring-brand-accent focus:border-transparent"
				placeholder="Any additional notes..."
			></textarea>
		</div>

		<!-- Actions -->
		<div class="flex gap-4">
			<button
				type="submit"
				disabled={submitting}
				class="flex-1 px-6 py-3 bg-brand-accent text-white rounded-lg hover:bg-brand-accent/90 transition-colors disabled:opacity-50"
			>
				{submitting ? 'Saving...' : 'Record Birth'}
			</button>
			<a
				href="/analytics"
				class="px-6 py-3 border border-brand-border text-brand-text-secondary rounded-lg hover:bg-brand-bg-subtle transition-colors text-center"
			>
				Cancel
			</a>
		</div>
	</form>
</div>
