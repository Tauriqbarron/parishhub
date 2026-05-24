<script lang="ts">
	import { signOut } from '@auth/sveltekit/client';
	import type { Session } from '@auth/core/types';
	import { Menu, Bell } from 'lucide-svelte';
	import Logo from './Logo.svelte';
	import NotificationDropdown from './NotificationDropdown.svelte';
	import { unreadCount, startPolling, stopPolling } from '$stores/notifications';
	import { onMount } from 'svelte';

	interface Props {
		session: Session;
		onMenuToggle?: () => void;
		showMenuButton?: boolean;
	}

	let { session, onMenuToggle, showMenuButton = false }: Props = $props();

	let dropdownOpen = $state(false);
	let bellRef: HTMLButtonElement | undefined = $state();

	function toggleDropdown() {
		dropdownOpen = !dropdownOpen;
	}

	function closeDropdown() {
		dropdownOpen = false;
	}

	onMount(() => {
		startPolling();
		return () => stopPolling();
	});
</script>

<header class="bg-white sticky top-0 z-40 border-b border-brand-border">
	<div class="flex items-center justify-between">
		<!-- Simple logo (mobile only) -->
		<div class="flex items-center gap-3 lg:hidden">
			{#if showMenuButton}
				<button
					onclick={onMenuToggle}
					class="p-2 -ml-2 text-brand-text-muted hover:text-brand-primary hover:bg-brand-bg-subtle rounded-sm"
					aria-label="Toggle navigation menu"
				>
					<Menu class="w-6 h-6" />
				</button>
			{/if}
			<div class="flex items-center gap-2">
				<Logo size={32} detail="simple" />
				<span class="text-base font-bold text-brand-primary tracking-tight">ParishHub</span>
			</div>
		</div>
		<!-- Full logo (desktop only) -->
		<div class="hidden lg:flex items-center gap-3 pl-2">
			<img
				src="/logo-double-border-shield-cross-church.png"
				alt="ParishHub"
				width="68"
				height="68"
				class="h-[68px] w-[68px]"
			/>
			<h1 class="text-2xl font-bold text-brand-primary tracking-tight">ParishHub</h1>
		</div>
		<div class="pr-4 flex items-center gap-3">
			<!-- Notification bell -->
			<div class="relative">
				<button
					bind:this={bellRef}
					onclick={toggleDropdown}
					class="p-2 text-brand-text-muted hover:text-brand-primary hover:bg-brand-bg-subtle rounded-sm transition-colors relative"
					aria-label="Notifications"
				>
					<Bell class="w-5 h-5" />
					{#if $unreadCount > 0}
						<span
							class="absolute -top-0.5 -right-0.5 min-w-[18px] h-[18px] flex items-center justify-center rounded-full bg-red-500 text-white text-[10px] font-bold leading-none px-1"
						>
							{$unreadCount > 99 ? '99+' : $unreadCount}
						</span>
					{/if}
				</button>
				{#if dropdownOpen}
					<NotificationDropdown onClose={closeDropdown} />
				{/if}
			</div>
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
