<script lang="ts">
	import { page } from '$app/stores';
	import { tick } from 'svelte';
	import { Home, Users, Building2, BarChart3, ClipboardCheck, Settings, X } from 'lucide-svelte';
	import type { Component } from 'svelte';

	interface NavItem {
		href: string;
		label: string;
		icon: Component;
	}

	interface Props {
		isOpen?: boolean;
		onClose?: () => void;
	}

	let { isOpen = true, onClose }: Props = $props();

	let navElement: HTMLElement | undefined = $state();

	function trapFocus(e: KeyboardEvent) {
		if (e.key !== 'Tab' || !navElement) return;
		const focusable = navElement.querySelectorAll<HTMLElement>(
			'a[href], button, input, select, textarea, [tabindex]:not([tabindex="-1"])'
		);
		if (focusable.length === 0) return;
		const first = focusable[0];
		const last = focusable[focusable.length - 1];
		if (e.shiftKey && document.activeElement === first) {
			e.preventDefault();
			last.focus();
		} else if (!e.shiftKey && document.activeElement === last) {
			e.preventDefault();
			first.focus();
		}
	}

	$effect(() => {
		if (isOpen && navElement) {
			tick().then(() => {
				const firstLink = navElement?.querySelector<HTMLElement>('a');
				firstLink?.focus();
			});
		}
	});

	const navItems: NavItem[] = [
		{ href: '/', label: 'Dashboard', icon: Home },
		{ href: '/people', label: 'People', icon: Users },
		{ href: '/households', label: 'Households', icon: Building2 },
		{ href: '/analytics', label: 'Analytics', icon: BarChart3 },
		{ href: '/analytics/attendance', label: 'Attendance', icon: ClipboardCheck },
		{ href: '/settings', label: 'Settings', icon: Settings }
	];

	function isActive(href: string): boolean {
		if (href === '/') {
			return $page.url.pathname === '/';
		}
		// Exact match for parent routes that have child nav items
		if (href === '/analytics') {
			return $page.url.pathname === '/analytics';
		}
		return $page.url.pathname.startsWith(href);
	}
</script>

<!-- Mobile overlay -->
{#if isOpen}
	<div
		class="fixed inset-0 bg-black/50 z-40 lg:hidden"
		onclick={onClose}
		onkeydown={(e) => e.key === 'Escape' && onClose?.()}
		role="button"
		tabindex="0"
		aria-label="Close navigation menu"
	></div>
{/if}

<!-- Navigation -->
<nav
	bind:this={navElement}
	onkeydown={trapFocus}
	class="fixed top-0 left-0 h-full w-64 bg-white shadow-lg transform transition-transform duration-300 ease-in-out z-50
		lg:translate-x-0 lg:static lg:shadow-none lg:border-r lg:border-gray-200
		{isOpen ? 'translate-x-0' : '-translate-x-full'}"
>
	<!-- Mobile header -->
	<div class="flex items-center justify-between p-4 border-b border-gray-200 lg:hidden">
		<span class="text-lg font-semibold text-gray-900">Menu</span>
		<button
			onclick={onClose}
			class="p-2 text-gray-600 hover:text-gray-900 hover:bg-gray-100 rounded-md"
			aria-label="Close menu"
		>
			<X class="w-5 h-5" />
		</button>
	</div>

	<!-- Navigation items -->
	<div class="p-4 pt-6 lg:pt-4">
		<ul class="space-y-1">
			{#each navItems as item (item.href)}
				<li>
					<a
						href={item.href}
						onclick={onClose}
						class="flex items-center gap-3 px-4 py-3 rounded-lg text-sm font-medium transition-colors
							{isActive(item.href)
							? 'bg-blue-50 text-blue-700'
							: 'text-gray-700 hover:bg-gray-100 hover:text-gray-900'}"
						aria-current={isActive(item.href) ? 'page' : undefined}
					>
						<svelte:component this={item.icon} class="w-5 h-5 flex-shrink-0" />
						<span>{item.label}</span>
					</a>
				</li>
			{/each}
		</ul>
	</div>
</nav>
