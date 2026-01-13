<script lang="ts">
	import { signOut } from '@auth/sveltekit/client';
	import type { Session } from '@auth/core/types';

	interface Props {
		session: Session;
		onMenuToggle?: () => void;
		showMenuButton?: boolean;
	}

	let { session, onMenuToggle, showMenuButton = false }: Props = $props();
</script>

<header class="bg-white shadow-sm sticky top-0 z-40">
	<div class="max-w-7xl mx-auto px-4 py-4 flex items-center justify-between">
		<div class="flex items-center gap-4">
			{#if showMenuButton}
				<button
					onclick={onMenuToggle}
					class="p-2 -ml-2 text-gray-600 hover:text-gray-900 hover:bg-gray-100 rounded-md lg:hidden"
					aria-label="Toggle navigation menu"
				>
					<svg class="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
						<path
							stroke-linecap="round"
							stroke-linejoin="round"
							stroke-width="2"
							d="M4 6h16M4 12h16M4 18h16"
						/>
					</svg>
				</button>
			{/if}
			<h1 class="text-xl font-semibold text-gray-900">Parish Database</h1>
		</div>
		<div class="flex items-center gap-4">
			<div class="hidden sm:flex items-center gap-2">
				{#if session.user?.image}
					<img
						src={session.user.image}
						alt={session.user.name || 'User'}
						class="w-8 h-8 rounded-full"
					/>
				{/if}
				<span class="text-sm text-gray-700">{session.user?.email}</span>
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
