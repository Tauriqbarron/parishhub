/**
 * Notification store — polls unread count and provides notification data
 * for the admin portal (SvelteKit).
 */
import { writable, derived } from 'svelte/store';
import { api } from '$lib/api';

export interface NotificationDelivery {
	id: number;
	title: string;
	body: string;
	category: string;
	channel: string;
	is_read: boolean;
	created_at: string;
}

export interface PaginatedNotifications {
	items: NotificationDelivery[];
	total: number;
	page: number;
	per_page: number;
	pages: number;
}

// ── State ──
export const unreadCount = writable<number>(0);
export const notifications = writable<NotificationDelivery[]>([]);
export const loading = writable<boolean>(false);
export const error = writable<string | null>(null);

// ── Derived ──
export const hasUnread = derived(unreadCount, ($n) => $n > 0);

// ── Actions ──
let pollInterval: ReturnType<typeof setInterval> | null = null;

export async function fetchUnreadCount(): Promise<void> {
	try {
		const data = await api.get<{ total: number }>('/member/notification/unread-count');
		unreadCount.set(data.total);
		error.set(null);
	} catch (e) {
		error.set(e instanceof Error ? e.message : 'Failed to fetch notification count');
	}
}

export async function fetchRecent(limit = 5): Promise<void> {
	loading.set(true);
	try {
		const data = await api.get<PaginatedNotifications>(
			`/member/notification/deliveries?status=unread&per_page=${limit}`
		);
		notifications.set(data.items);
		error.set(null);
	} catch (e) {
		error.set(e instanceof Error ? e.message : 'Failed to fetch notifications');
	} finally {
		loading.set(false);
	}
}

export async function markAsRead(deliveryIds: number[]): Promise<void> {
	try {
		await api.put('/member/notification/deliveries/mark-read', {
			delivery_ids: deliveryIds
		});
		// Optimistic update
		notifications.update((items) =>
			items.map((n) => (deliveryIds.includes(n.id) ? { ...n, is_read: true } : n))
		);
		unreadCount.update((n) => Math.max(0, n - deliveryIds.length));
	} catch (e) {
		error.set(e instanceof Error ? e.message : 'Failed to mark as read');
	}
}

export function startPolling(intervalMs = 60_000): void {
	if (pollInterval) return;
	fetchUnreadCount(); // Initial fetch
	pollInterval = setInterval(fetchUnreadCount, intervalMs);
}

export function stopPolling(): void {
	if (pollInterval) {
		clearInterval(pollInterval);
		pollInterval = null;
	}
}
