<script lang="ts">
	import { signOut } from '@auth/sveltekit/client';
	import type { Session } from '@auth/core/types';
	import { Menu } from 'lucide-svelte';
	import Logo from './Logo.svelte';

	interface Props {
		session: Session;
		onMenuToggle?: () => void;
		showMenuButton?: boolean;
	}

	let { session, onMenuToggle, showMenuButton = false }: Props = $props();
</script>

<header class="bg-white sticky top-0 z-40 border-b border-brand-border">
	<div class="max-w-7xl mx-auto px-4 py-3 flex items-center justify-between">
		<div class="flex items-center gap-3">
			{#if showMenuButton}
				<button
					onclick={onMenuToggle}
					class="p-2 -ml-2 text-brand-text-muted hover:text-brand-primary hover:bg-brand-bg-subtle rounded-sm lg:hidden"
					aria-label="Toggle navigation menu"
				>
					<Menu class="w-6 h-6" />
				</button>
			{/if}
			<div class="flex items-center gap-2">
				<Logo size={28} />
				<h1 class="text-lg font-bold text-brand-primary tracking-tight">ParishHub</h1>
			</div>
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
				class="px-3 py-1.5 text-sm text-brand-text-muted hover:text-brand-primary hover:bg-brand-bg-subtle rounded-sm transition-colors"
			>
				Sign out
			</button>
		</div>
	</div>
</header>
