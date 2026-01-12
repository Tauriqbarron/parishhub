<script lang="ts">
	import '../app.css';
	import { signOut } from '@auth/sveltekit/client';

	let { children, data } = $props();
</script>

{#if data.session?.user}
	<div class="min-h-screen bg-gray-100">
		<header class="bg-white shadow-sm">
			<div class="max-w-7xl mx-auto px-4 py-4 flex items-center justify-between">
				<h1 class="text-xl font-semibold text-gray-900">Parish Database</h1>
				<div class="flex items-center gap-4">
					<div class="flex items-center gap-2">
						{#if data.session.user.image}
							<img
								src={data.session.user.image}
								alt={data.session.user.name || 'User'}
								class="w-8 h-8 rounded-full"
							/>
						{/if}
						<span class="text-sm text-gray-700">{data.session.user.email}</span>
					</div>
					<button
						onclick={() => signOut()}
						class="px-3 py-1.5 text-sm text-gray-600 hover:text-gray-900 hover:bg-gray-100 rounded-md transition-colors"
					>
						Sign out
					</button>
				</div>
			</div>
		</header>
		<main>
			{@render children()}
		</main>
	</div>
{:else}
	{@render children()}
{/if}
