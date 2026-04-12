<script lang="ts">
	import { page } from '$app/stores';
	import { tick } from 'svelte';

	interface NavItem {
		href: string;
		label: string;
		icon: string;
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
		{
			href: '/',
			label: 'Dashboard',
			icon: 'M3 12l2-2m0 0l7-7 7 7M5 10v10a1 1 0 001 1h3m10-11l2 2m-2-2v10a1 1 0 01-1 1h-3m-6 0a1 1 0 001-1v-4a1 1 0 011-1h2a1 1 0 011 1v4a1 1 0 001 1m-6 0h6'
		},
		{
			href: '/people',
			label: 'People',
			icon: 'M12 4.354a4 4 0 110 5.292M15 21H3v-1a6 6 0 0112 0v1zm0 0h6v-1a6 6 0 00-9-5.197M13 7a4 4 0 11-8 0 4 4 0 018 0z'
		},
		{
			href: '/households',
			label: 'Households',
			icon: 'M3 12l2-2m0 0l7-7 7 7M5 10v10a1 1 0 001 1h3m10-11l2 2m-2-2v10a1 1 0 01-1 1h-3m-6 0a1 1 0 001-1v-4a1 1 0 011-1h2a1 1 0 011 1v4a1 1 0 001 1m-6 0h6'
		},
		{
			href: '/analytics',
			label: 'Analytics',
			icon: 'M9 19v-6a2 2 0 00-2-2H5a2 2 0 00-2 2v6a2 2 0 002 2h2a2 2 0 002-2zm0 0V9a2 2 0 012-2h2a2 2 0 012 2v10m-6 0a2 2 0 002 2h2a2 2 0 002-2m0 0V5a2 2 0 012-2h2a2 2 0 012 2v14a2 2 0 01-2 2h-2a2 2 0 01-2-2z'
		},
		{
			href: '/analytics/attendance',
			label: 'Attendance',
			icon: 'M9 5H7a2 2 0 00-2 2v12a2 2 0 002 2h10a2 2 0 002-2V7a2 2 0 00-2-2h-2M9 5a2 2 0 002 2h2a2 2 0 002-2M9 5a2 2 0 012-2h2a2 2 0 012 2m-3 7h3m-3 4h3m-6-4h.01M9 16h.01'
		},
		{
			href: '/settings',
			label: 'Settings',
			icon: 'M10.325 4.317c.426-1.756 2.924-1.756 3.35 0a1.724 1.724 0 002.573 1.066c1.543-.94 3.31.826 2.37 2.37a1.724 1.724 0 001.065 2.572c1.756.426 1.756 2.924 0 3.35a1.724 1.724 0 00-1.066 2.573c.94 1.543-.826 3.31-2.37 2.37a1.724 1.724 0 00-2.572 1.065c-.426 1.756-2.924 1.756-3.35 0a1.724 1.724 0 00-2.573-1.066c-1.543.94-3.31-.826-2.37-2.37a1.724 1.724 0 00-1.065-2.572c-1.756-.426-1.756-2.924 0-3.35a1.724 1.724 0 001.066-2.573c-.94-1.543.826-3.31 2.37-2.37.996.608 2.296.07 2.572-1.065z'
		}
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
			<svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
				<path
					stroke-linecap="round"
					stroke-linejoin="round"
					stroke-width="2"
					d="M6 18L18 6M6 6l12 12"
				/>
			</svg>
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
						<svg
							class="w-5 h-5 flex-shrink-0"
							fill="none"
							stroke="currentColor"
							viewBox="0 0 24 24"
						>
							<path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d={item.icon} />
						</svg>
						<span>{item.label}</span>
					</a>
				</li>
			{/each}
		</ul>
	</div>
</nav>
