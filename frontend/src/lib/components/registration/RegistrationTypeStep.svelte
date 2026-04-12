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
		<h2 class="text-xl font-semibold text-brand-primary">How would you like to register?</h2>
		<p class="text-brand-text-secondary mt-1">
			Choose the option that best describes your situation.
		</p>
	</div>

	<div class="grid grid-cols-1 sm:grid-cols-2 gap-4">
		<!-- Individual Option -->
		<button
			type="button"
			onclick={() => select('individual')}
			class="relative flex flex-col items-center p-6 border-2 rounded-lg transition-all
				{selected === 'individual'
				? 'border-brand-accent bg-brand-accent/5 ring-2 ring-brand-accent'
				: 'border-brand-border hover:border-brand-border/70 bg-white'}"
		>
			<div
				class="w-16 h-16 rounded-full flex items-center justify-center mb-4
				{selected === 'individual' ? 'bg-brand-bg-muted' : 'bg-brand-bg-subtle'}"
			>
				<svg
					class="w-8 h-8 {selected === 'individual'
						? 'text-brand-accent'
						: 'text-brand-text-muted'}"
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
			<h3 class="text-lg font-medium text-brand-primary">Individual</h3>
			<p class="mt-2 text-sm text-brand-text-muted text-center">
				Register yourself as an individual parishioner without creating a household.
			</p>
			{#if selected === 'individual'}
				<div class="absolute top-3 right-3">
					<svg class="w-6 h-6 text-brand-accent" fill="currentColor" viewBox="0 0 20 20">
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
				? 'border-brand-accent bg-brand-accent/5 ring-2 ring-brand-accent'
				: 'border-brand-border hover:border-brand-border/70 bg-white'}"
		>
			<div
				class="w-16 h-16 rounded-full flex items-center justify-center mb-4
				{selected === 'household' ? 'bg-brand-bg-muted' : 'bg-brand-bg-subtle'}"
			>
				<svg
					class="w-8 h-8 {selected === 'household' ? 'text-brand-accent' : 'text-brand-text-muted'}"
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
			<h3 class="text-lg font-medium text-brand-primary">Household</h3>
			<p class="mt-2 text-sm text-brand-text-muted text-center">
				Register your household with multiple family members and relationships.
			</p>
			{#if selected === 'household'}
				<div class="absolute top-3 right-3">
					<svg class="w-6 h-6 text-brand-accent" fill="currentColor" viewBox="0 0 20 20">
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
