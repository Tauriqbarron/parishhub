<script lang="ts">
	import { page } from '$app/stores';
	import { goto } from '$app/navigation';
	import { Home, Users, Calendar, LogOut, Menu, X } from 'lucide-svelte';
	import { onMount } from 'svelte';
	import { memberApi, clearToken, type MemberUser } from '$lib/api';

	let { children } = $props();

	let user = $state<MemberUser | null>(null);
	let loading = $state(true);
	let menuOpen = $state(false);

	async function loadUser() {
		const token = localStorage.getItem('member_token');
		if (!token) {
			loading = false;
			return;
		}
		try {
			user = await memberApi.me();
		} catch {
			clearToken();
		}
		loading = false;
	}

	function handleLogout() {
		clearToken();
		user = null;
		goto('/login');
	}

	onMount(loadUser);

	const isLoginPage = $derived($page.url.pathname === '/login');
	const navItems = $derived([
		{ href: '/dashboard', label: 'Dashboard', icon: Home },
		{ href: '/groups', label: 'My Groups', icon: Users },
		{ href: '/events', label: 'Events', icon: Calendar }
	]);
</script>

{#if isLoginPage}
	{@render children()}
{:else if loading}
	<div class="min-h-screen flex items-center justify-center">
		<div class="animate-pulse text-gray-400">Loading...</div>
	</div>
{:else if !user}
	{@render children()}
{:else}
	<div class="min-h-screen flex flex-col">
		<!-- Header -->
		<header class="bg-white border-b border-gray-200 sticky top-0 z-30">
			<div class="max-w-4xl mx-auto px-4 h-14 flex items-center justify-between">
				<div class="flex items-center gap-3">
					<button
						class="lg:hidden p-1.5 text-gray-500 hover:text-gray-700"
						onclick={() => (menuOpen = !menuOpen)}
					>
						{#if menuOpen}<X class="w-5 h-5" />{:else}<Menu class="w-5 h-5" />{/if}
					</button>
					<a href="/dashboard" class="font-semibold text-gray-900">Ministries</a>
				</div>
				<div class="flex items-center gap-3">
					{#if user.picture}
						<img src={user.picture} alt="" class="w-7 h-7 rounded-full" />
					{/if}
					<span class="text-sm text-gray-600 hidden sm:block">{user.name || user.email}</span>
					<button
						onclick={handleLogout}
						class="p-1.5 text-gray-400 hover:text-gray-600"
						title="Sign out"
					>
						<LogOut class="w-4 h-4" />
					</button>
				</div>
			</div>
		</header>

		<div class="flex-1 flex max-w-4xl mx-auto w-full">
			<!-- Sidebar (desktop) -->
			<nav class="hidden lg:block w-48 p-4 shrink-0">
				<ul class="space-y-1">
					{#each navItems as item}
						<li>
							<a
								href={item.href}
								class="flex items-center gap-2.5 px-3 py-2 rounded-md text-sm transition-colors
									{$page.url.pathname.startsWith(item.href)
									? 'bg-orange-50 text-orange-700 font-medium'
									: 'text-gray-600 hover:bg-gray-50 hover:text-gray-900'}"
							>
								<svelte:component this={item.icon} class="w-4 h-4" />
								{item.label}
							</a>
						</li>
					{/each}
				</ul>
			</nav>

			<!-- Mobile sidebar overlay -->
			{#if menuOpen}
				<div
					class="fixed inset-0 bg-black/20 z-40 lg:hidden"
					onclick={() => (menuOpen = false)}
					role="button"
					tabindex="0"
				></div>
				<nav class="fixed top-14 left-0 bottom-0 w-56 bg-white border-r border-gray-200 z-50 lg:hidden p-4">
					<ul class="space-y-1">
						{#each navItems as item}
							<li>
								<a
									href={item.href}
									onclick={() => (menuOpen = false)}
									class="flex items-center gap-2.5 px-3 py-2 rounded-md text-sm transition-colors
										{$page.url.pathname.startsWith(item.href)
										? 'bg-orange-50 text-orange-700 font-medium'
										: 'text-gray-600 hover:bg-gray-50'}"
								>
									<svelte:component this={item.icon} class="w-4 h-4" />
									{item.label}
								</a>
							</li>
						{/each}
					</ul>
				</nav>
			{/if}

			<!-- Main content -->
			<main class="flex-1 p-4 min-w-0">
				{@render children()}
			</main>
		</div>

		<!-- Mobile bottom nav -->
		<nav class="lg:hidden fixed bottom-0 left-0 right-0 bg-white border-t border-gray-200 z-30">
			<div class="flex justify-around py-2">
				{#each navItems as item}
					<a
						href={item.href}
						class="flex flex-col items-center gap-0.5 px-4 py-1 text-xs
							{$page.url.pathname.startsWith(item.href)
							? 'text-orange-600'
							: 'text-gray-400'}"
					>
						<svelte:component this={item.icon} class="w-5 h-5" />
						{item.label}
					</a>
				{/each}
			</div>
		</nav>
	</div>
{/if}
