<script lang="ts">
	import '../app.css';
	import Header from '$components/Header.svelte';
	import Nav from '$components/Nav.svelte';
	import Toast from '$components/Toast.svelte';

	let { children, data } = $props();

	let mobileNavOpen = $state(false);

	function toggleMobileNav() {
		mobileNavOpen = !mobileNavOpen;
	}

	function closeMobileNav() {
		mobileNavOpen = false;
	}
</script>

{#if data.session?.user}
	<div class="min-h-screen bg-gray-100">
		<Header
			session={data.session}
			onMenuToggle={toggleMobileNav}
			showMenuButton={true}
		/>

		<div class="flex">
			<Nav isOpen={mobileNavOpen} onClose={closeMobileNav} />

			<main class="flex-1 lg:ml-0">
				<div class="max-w-7xl mx-auto px-4 py-6">
					{@render children()}
				</div>
			</main>
		</div>
	</div>
{:else}
	{@render children()}
{/if}

<Toast />
