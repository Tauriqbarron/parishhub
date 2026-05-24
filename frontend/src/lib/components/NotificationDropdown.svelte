<script lang="ts">
	import { onMount } from 'svelte';
	import { Bell, Loader2 } from 'lucide-svelte';
	import { notifications, loading, fetchRecent, markAsRead } from '$stores/notifications';
	import { goto } from '$app/navigation';

	interface Props {
		onClose: () => void;
	}

	let { onClose }: Props = $props();

	onMount(() => {
		fetchRecent(5);
	});

	function handleClick(deliveryId: number) {
		markAsRead([deliveryId]);
	}

	function handleViewAll() {
		onClose();
		goto('/notifications');
	}

	/** Close on Escape */
	function handleKeydown(e: KeyboardEvent) {
		if (e.key === 'Escape') onClose();
	}

	/** Format ISO date as relative time */
	function timeAgo(iso: string): string {
		const now = Date.now();
		const then = new Date(iso).getTime();
		const diff = now - then;
		const seconds = Math.floor(diff / 1000);
		const minutes = Math.floor(seconds / 60);
		const hours = Math.floor(minutes / 60);
		const days = Math.floor(hours / 24);

		if (seconds < 60) return 'Just now';
		if (minutes < 60) return `${minutes}m ago`;
		if (hours < 24) return `${hours}h ago`;
		if (days < 7) return `${days}d ago`;
		return new Date(iso).toLocaleDateString();
	}
</script>

<svelte:window onkeydown={handleKeydown} />

<!-- Backdrop -->
<div
	class="fixed inset-0 bg-transparent z-50"
	onclick={onClose}
	onkeydown={(e) => e.key === 'Escape' && onClose()}
	role="presentation"
></div>

<!-- Dropdown panel -->
<div
	class="absolute right-4 top-14 w-80 bg-white rounded-lg border border-brand-border shadow-lg z-50 overflow-hidden"
>
	<div class="flex items-center justify-between px-4 py-3 border-b border-brand-border">
		<h3 class="text-sm font-semibold text-brand-primary">Notifications</h3>
	</div>

	<div class="max-h-[360px] overflow-y-auto">
		{#if $loading}
			<div class="flex items-center justify-center py-8">
				<Loader2 class="w-5 h-5 animate-spin text-brand-text-muted" />
			</div>
		{:else if $notifications.length === 0}
			<div class="flex flex-col items-center justify-center py-8 text-brand-text-muted gap-2">
				<Bell class="w-8 h-8 opacity-30" />
				<p class="text-sm">No new notifications</p>
			</div>
		{:else}
			{#each $notifications as notif (notif.id)}
				<button
					class="w-full text-left px-4 py-3 hover:bg-brand-bg-subtle transition-colors border-b border-brand-border last:border-b-0 flex items-start gap-3"
					onclick={() => handleClick(notif.id)}
				>
					<!-- Unread dot -->
					<div class="flex-shrink-0 mt-1.5">
						{#if !notif.is_read}
							<span class="block w-2 h-2 rounded-full bg-amber-500"></span>
						{:else}
							<span class="block w-2 h-2 rounded-full bg-transparent"></span>
						{/if}
					</div>
					<div class="min-w-0 flex-1">
						<p class="text-sm font-medium text-brand-primary truncate">
							{notif.title}
						</p>
						<p class="text-xs text-brand-text-muted mt-0.5 line-clamp-2">
							{notif.body}
						</p>
						<span class="text-xs text-brand-text-muted mt-1 block">
							{timeAgo(notif.created_at)}
						</span>
					</div>
				</button>
			{/each}
		{/if}
	</div>

	<!-- View all -->
	<div class="border-t border-brand-border">
		<button
			class="w-full px-4 py-2.5 text-sm font-medium text-brand-accent hover:bg-brand-accent/5 transition-colors text-center"
			onclick={handleViewAll}
		>
			View all notifications
		</button>
	</div>
</div>
