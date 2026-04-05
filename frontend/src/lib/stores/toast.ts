import { writable } from 'svelte/store';

export type ToastType = 'success' | 'error' | 'warning' | 'info';

export interface ToastAction {
	label: string;
	onClick: () => void;
}

export interface Toast {
	id: string;
	message: string;
	type: ToastType;
	duration?: number;
	actions?: ToastAction[];
}

function createToastStore() {
	const { subscribe, update } = writable<Toast[]>([]);

	function add(message: string, type: ToastType = 'info', duration = 5000) {
		const id = crypto.randomUUID();
		const toast: Toast = { id, message, type, duration };

		update((toasts) => [...toasts, toast]);

		if (duration > 0) {
			setTimeout(() => remove(id), duration);
		}

		return id;
	}

	function remove(id: string) {
		update((toasts) => toasts.filter((t) => t.id !== id));
	}

	function clear() {
		update(() => []);
	}

	return {
		subscribe,
		add,
		remove,
		clear,
		success: (message: string, duration?: number) => add(message, 'success', duration),
		error: (message: string, duration?: number) => add(message, 'error', duration),
		warning: (message: string, duration?: number) => add(message, 'warning', duration),
		info: (message: string, duration?: number) => add(message, 'info', duration),
		successWithActions: (message: string, actions: ToastAction[], duration = 10000) => {
			const id = crypto.randomUUID();
			update((t) => [...t, { id, message, type: 'success' as ToastType, duration, actions }]);
			if (duration > 0) setTimeout(() => remove(id), duration);
			return id;
		}
	};
}

export const toasts = createToastStore();

export const addToast = toasts.add;
