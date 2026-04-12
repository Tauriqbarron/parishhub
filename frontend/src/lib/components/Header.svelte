<script lang="ts">
	import { signOut } from '@auth/sveltekit/client';
	import type { Session } from '@auth/core/types';
	import { Menu } from 'lucide-svelte';

	interface Props {
		session: Session;
		onMenuToggle?: () => void;
		showMenuButton?: boolean;
	}

	let { session, onMenuToggle, showMenuButton = false }: Props = $props();
</script>

<header class="bg-white shadow-sm sticky top-0 z-40 border-b border-brand-border">
	<div class="max-w-7xl mx-auto px-4 py-4 flex items-center justify-between">
		<div class="flex items-center gap-4">
			{#if showMenuButton}
				<button
					onclick={onMenuToggle}
					class="p-2 -ml-2 text-brand-primary-muted hover:text-brand-primary hover:bg-brand-bg-muted rounded-md lg:hidden"
					aria-label="Toggle navigation menu"
				>
					<Menu class="w-6 h-6" />
				</button>
			{/if}
			<h1 class="text-xl font-semibold text-brand-primary">ParishHub</h1>
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
				<span class="text-sm text-brand-text-secondary">{session.user?.email}</span>
			</div>
			<button
				onclick={() => signOut()}
				class="px-3 py-1.5 text-sm text-brand-text-muted hover:text-brand-primary hover:bg-brand-bg-muted rounded-md transition-colors"
			>
				Sign out
			</button>
		</div>
	</div>
</header>
