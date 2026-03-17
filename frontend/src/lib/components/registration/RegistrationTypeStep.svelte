<script lang="ts">
	import { registrationSessionStore } from '$lib/stores/registrationSession';
	import type { RegistrationType } from '$lib/stores/registrationSession';
	import { get } from 'svelte/store';

	let selected = $state<RegistrationType>(get(registrationSessionStore).registrationType);

	$effect(() => {
		const unsubscribe = registrationSessionStore.subscribe((s) => {
			selected = s.registrationType;
		});
		return unsubscribe;
	});

	function select(type: RegistrationType) {
		selected = type;
		registrationSessionStore.setRegistrationType(type);
	}

	export function isValid(): boolean {
		return selected !== null;
	}
</script>

<div class="space-y-6">
	<div class="text-center mb-6">
		<h2 class="text-xl font-semibold text-gray-900">How would you like to register?</h2>
		<p class="text-gray-600 mt-1">Choose the option that best describes your situation.</p>
	</div>

	<div class="grid grid-cols-1 sm:grid-cols-2 gap-4">
		<!-- Individual Option -->
		<button
			type="button"
			onclick={() => select('individual')}
			class="relative flex flex-col items-center p-6 border-2 rounded-lg transition-all
				{selected === 'individual'
				? 'border-blue-600 bg-blue-50 ring-2 ring-blue-600'
				: 'border-gray-200 hover:border-gray-300 bg-white'}"
		>
			<div
				class="w-16 h-16 rounded-full flex items-center justify-center mb-4
				{selected === 'individual' ? 'bg-blue-100' : 'bg-gray-100'}"
			>
				<svg
					class="w-8 h-8 {selected === 'individual' ? 'text-blue-600' : 'text-gray-400'}"
					fill="none"
					stroke="currentColor"
					viewBox="0 0 24 24"
				>
					<path
						stroke-linecap="round"
						stroke-linejoin="round"
						stroke-width="2"
						d="M16 7a4 4 0 11-8 0 4 4 0 018 0zM12 14a7 7 0 00-7 7h14a7 7 0 00-7-7z"
					/>
				</svg>
			</div>
			<h3 class="text-lg font-medium text-gray-900">Individual</h3>
			<p class="mt-2 text-sm text-gray-500 text-center">
				Register yourself as an individual parishioner without creating a household.
			</p>
			{#if selected === 'individual'}
				<div class="absolute top-3 right-3">
					<svg class="w-6 h-6 text-blue-600" fill="currentColor" viewBox="0 0 20 20">
						<path
							fill-rule="evenodd"
							d="M10 18a8 8 0 100-16 8 8 0 000 16zm3.707-9.293a1 1 0 00-1.414-1.414L9 10.586 7.707 9.293a1 1 0 00-1.414 1.414l2 2a1 1 0 001.414 0l4-4z"
							clip-rule="evenodd"
						/>
					</svg>
				</div>
			{/if}
		</button>

		<!-- Household Option -->
		<button
			type="button"
			onclick={() => select('household')}
			class="relative flex flex-col items-center p-6 border-2 rounded-lg transition-all
				{selected === 'household'
				? 'border-blue-600 bg-blue-50 ring-2 ring-blue-600'
				: 'border-gray-200 hover:border-gray-300 bg-white'}"
		>
			<div
				class="w-16 h-16 rounded-full flex items-center justify-center mb-4
				{selected === 'household' ? 'bg-blue-100' : 'bg-gray-100'}"
			>
				<svg
					class="w-8 h-8 {selected === 'household' ? 'text-blue-600' : 'text-gray-400'}"
					fill="none"
					stroke="currentColor"
					viewBox="0 0 24 24"
				>
					<path
						stroke-linecap="round"
						stroke-linejoin="round"
						stroke-width="2"
						d="M3 12l2-2m0 0l7-7 7 7M5 10v10a1 1 0 001 1h3m10-11l2 2m-2-2v10a1 1 0 01-1 1h-3m-6 0a1 1 0 001-1v-4a1 1 0 011-1h2a1 1 0 011 1v4a1 1 0 001 1m-6 0h6"
					/>
				</svg>
			</div>
			<h3 class="text-lg font-medium text-gray-900">Household</h3>
			<p class="mt-2 text-sm text-gray-500 text-center">
				Register your household with multiple family members and relationships.
			</p>
			{#if selected === 'household'}
				<div class="absolute top-3 right-3">
					<svg class="w-6 h-6 text-blue-600" fill="currentColor" viewBox="0 0 20 20">
						<path
							fill-rule="evenodd"
							d="M10 18a8 8 0 100-16 8 8 0 000 16zm3.707-9.293a1 1 0 00-1.414-1.414L9 10.586 7.707 9.293a1 1 0 00-1.414 1.414l2 2a1 1 0 001.414 0l4-4z"
							clip-rule="evenodd"
						/>
					</svg>
				</div>
			{/if}
		</button>
	</div>
</div>
