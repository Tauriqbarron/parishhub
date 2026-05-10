<script lang="ts">
	import { page } from '$app/stores';
	import { goto } from '$app/navigation';
	import { Home, Users, Calendar, LogOut, Menu, X, User, List } from 'lucide-svelte';
	import { onMount } from 'svelte';
	import { memberApi, clearToken, type MemberUser, type WeekDashboard } from '$lib/api';

	let { children } = $props();

	let user = $state<MemberUser | null>(null);
	let dashboard = $state<WeekDashboard | null>(null);
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
			// Load dashboard for sidebar summary (non-blocking)
			memberApi.dashboard().then(d => { dashboard = d; }).catch(() => {});
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

	function formatShortDate(dateStr: string): string {
		return new Date(dateStr + 'T00:00:00').toLocaleDateString('en-US', {
			weekday: 'short', month: 'short', day: 'numeric'
		});
	}

	function formatTimeShort(time: string | null): string {
		if (!time) return '';
		const [h, m] = time.split(':');
		const hour = parseInt(h);
		return `${hour % 12 || 12}:${m} ${hour >= 12 ? 'PM' : 'AM'}`;
	}

	onMount(loadUser);

	const isLoginPage = $derived($page.url.pathname === '/login');
	const navItems = $derived([
		{ href: '/dashboard', label: 'This Week', icon: Calendar },
		{ href: '/groups', label: 'Groups', icon: Users },
		{ href: '/events', label: 'Events', icon: List },
		{ href: '/profile', label: 'Profile', icon: User }
	]);

	const upcomingEvents = $derived(
		dashboard?.events?.slice(0, 4) ?? []
	);
</script>

{#if isLoginPage}
	{@render children()}
{:else if loading}
	<div class="min-h-screen flex items-center justify-center bg-brand-bg-subtle">
		<div class="animate-pulse text-brand-text-muted">Loading...</div>
	</div>
{:else if !user}
	{@render children()}
{:else}
	<div class="min-h-screen flex flex-col bg-brand-bg-subtle">
		<!-- Header -->
		<header class="bg-white border-b border-brand-border shadow-sm sticky top-0 z-sticky">
			<div class="max-w-7xl mx-auto px-4 sm:px-6 h-14 flex items-center justify-between">
				<div class="flex items-center gap-3">
					<button
						class="lg:hidden p-1.5 text-brand-text-muted hover:text-brand-text-secondary transition-colors"
						onclick={() => (menuOpen = !menuOpen)}
					>
						{#if menuOpen}<X class="w-5 h-5" />{:else}<Menu class="w-5 h-5" />{/if}
					</button>
				<a href="/dashboard" class="flex items-center gap-2.5">
					<img src="/logo.png" alt="ParishHub" class="w-8 h-8" />
					<div class="flex items-baseline gap-1.5">
						<span class="font-bold text-brand-primary tracking-tight text-lg">ParishHub</span>
						<span class="text-sm text-brand-text-muted font-medium hidden sm:inline">Ministries</span>
					</div>
				</a>
				</div>
				<div class="flex items-center gap-3">
					{#if user.picture}
						<img src={user.picture} alt="" class="w-7 h-7 rounded-full" />
					{/if}
					<span class="text-sm text-brand-text-secondary hidden sm:block">{user.name || user.email}</span>
					<button
						onclick={handleLogout}
						class="p-1.5 text-brand-text-muted hover:text-brand-text-secondary transition-colors"
						title="Sign out"
					>
						<LogOut class="w-4 h-4" />
					</button>
				</div>
			</div>
		</header>

		<div class="flex-1 flex max-w-7xl mx-auto w-full">
			<!-- Sidebar (desktop) -->
			<aside class="hidden lg:flex flex-col w-64 p-4 shrink-0 border-r border-brand-border bg-white">
				<!-- Logo -->
				<a href="/dashboard" class="flex items-center gap-2.5 mb-5 px-1">
					<img src="/logo.png" alt="ParishHub" class="w-8 h-8" />
					<div>
						<p class="font-bold text-brand-primary tracking-tight text-sm leading-tight">ParishHub</p>
						<p class="text-[10px] text-brand-text-muted font-medium">Ministries</p>
					</div>
				</a>

				<!-- Nav links -->
				<nav>
					<p class="px-3 mb-1.5 text-[10px] font-semibold text-brand-text-muted uppercase tracking-wider">Navigation</p>
					<ul class="space-y-0.5">
						{#each navItems as item}
							<li>
								<a
									href={item.href}
									class="flex items-center gap-2.5 px-3 py-2 rounded-md text-sm transition-colors
										{$page.url.pathname.startsWith(item.href)
										? 'bg-brand-accent-muted text-brand-accent font-medium'
										: 'text-brand-text-secondary hover:bg-brand-bg-subtle hover:text-brand-primary'}"
								>
									<svelte:component this={item.icon} class="w-4 h-4" />
									{item.label}
								</a>
							</li>
						{/each}
					</ul>
				</nav>

				<!-- Upcoming events summary -->
				{#if upcomingEvents.length > 0}
					<div class="mt-auto pt-4 border-t border-brand-border">
						<p class="px-1 mb-2 text-[10px] font-semibold text-brand-text-muted uppercase tracking-wider">Upcoming</p>
						<div class="space-y-1.5">
							{#each upcomingEvents as event (event.id)}
								<button
									onclick={() => goto(`/groups/${event.ministry_id ?? 0}/events/${event.id}`)}
									class="w-full text-left px-2 py-1.5 rounded-md hover:bg-brand-bg-subtle transition-colors group"
								>
									<p class="text-xs font-medium text-brand-primary truncate group-hover:text-brand-accent transition-colors">{event.title}</p>
									<p class="text-[10px] text-brand-text-muted">{formatShortDate(event.event_date)}{event.start_time ? ` · ${formatTimeShort(event.start_time)}` : ''}</p>
								</button>
							{/each}
						</div>
					</div>
				{/if}
			</aside>

			<!-- Mobile sidebar overlay -->
			{#if menuOpen}
				<div
					class="fixed inset-0 bg-black/20 z-overlay lg:hidden"
					onclick={() => (menuOpen = false)}
					role="button"
					tabindex="0"
				></div>
				<nav class="fixed top-14 left-0 bottom-0 w-64 bg-white border-r border-brand-border shadow-lg z-modal lg:hidden p-4">
					<!-- User card mobile -->
					<div class="mb-4 pb-4 border-b border-brand-border">
						<p class="text-sm font-medium text-brand-primary">{user.name || 'Member'}</p>
						<p class="text-xs text-brand-text-muted">{user.email}</p>
					</div>
					<ul class="space-y-0.5">
						{#each navItems as item}
							<li>
								<a
									href={item.href}
									onclick={() => (menuOpen = false)}
									class="flex items-center gap-2.5 px-3 py-2 rounded-md text-sm transition-colors
										{$page.url.pathname.startsWith(item.href)
										? 'bg-brand-accent-muted text-brand-accent font-medium'
										: 'text-brand-text-secondary hover:bg-brand-bg-subtle'}"
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
			<main class="flex-1 p-4 sm:p-6 pb-20 lg:pb-6 min-w-0">
				{@render children()}
			</main>
		</div>

		<!-- Mobile bottom nav -->
		<nav class="lg:hidden fixed bottom-0 left-0 right-0 bg-white border-t border-brand-border shadow-sm z-sticky" style="padding-bottom: env(safe-area-inset-bottom)">
			<div class="flex justify-around py-2">
				{#each navItems as item}
					<a
						href={item.href}
						class="flex flex-col items-center gap-0.5 px-3 py-1 text-xs transition-colors
							{$page.url.pathname.startsWith(item.href)
							? 'text-brand-accent font-semibold'
							: 'text-brand-text-muted'}"
					>
						<svelte:component this={item.icon} class="w-5 h-5" strokeWidth={$page.url.pathname.startsWith(item.href) ? 2.5 : 2} />
						{item.label}
					</a>
				{/each}
			</div>
		</nav>
	</div>
{/if}
