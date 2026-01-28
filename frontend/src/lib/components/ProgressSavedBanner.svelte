<script lang="ts">
	import { registrationSessionStore } from '$lib/stores/registrationSession';
	import { get } from 'svelte/store';

	interface Props {
		onStartOver?: () => void;
	}

	let { onStartOver }: Props = $props();

	let dismissed = $state(false);
	let session = $state(get(registrationSessionStore));

	$effect(() => {
		const unsubscribe = registrationSessionStore.subscribe((s) => {
			session = s;
		});
		return unsubscribe;
	});

	const lastUpdated = $derived(
		session?.lastUpdated
			? new Date(session.lastUpdated).toLocaleString()
			: null
	);

	const hasExistingSession = $derived(
		session?.id && session?.lastUpdated && !dismissed
	);

	function handleStartOver() {
		if (onStartOver) {
			onStartOver();
		} else {
			registrationSessionStore.clearSession();
			registrationSessionStore.initSession();
		}
		dismissed = true;
	}

	function handleDismiss() {
		dismissed = true;
	}
</script>

{#if hasExistingSession && lastUpdated}
	<div class="bg-yellow-50 border border-yellow-200 p-4 rounded-lg mb-4 relative">
		<button
			type="button"
			class="absolute top-2 right-2 text-yellow-600 hover:text-yellow-800"
			onclick={handleDismiss}
			aria-label="Dismiss"
		>
			<svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
				<path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12" />
			</svg>
		</button>
		<p class="text-yellow-800 pr-6">
			<strong>Welcome back!</strong> We found your saved progress from {lastUpdated}.
			You can continue where you left off.
		</p>
		<button
			type="button"
			class="mt-2 text-yellow-600 hover:text-yellow-800 underline text-sm"
			onclick={handleStartOver}
		>
			Start over instead
		</button>
	</div>
{/if}
