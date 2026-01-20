import { describe, it, expect, beforeEach, vi } from 'vitest';
import { get } from 'svelte/store';
import { toasts } from '$lib/stores/toast';

// Mock crypto.randomUUID
vi.stubGlobal('crypto', {
	randomUUID: () => 'test-uuid-' + Math.random().toString(36).substr(2, 9)
});

describe('Toast Store', () => {
	beforeEach(() => {
		toasts.clear();
	});

	describe('add', () => {
		it('should add a toast with default type info', () => {
			toasts.add('Test message');
			const currentToasts = get(toasts);

			expect(currentToasts).toHaveLength(1);
			expect(currentToasts[0].message).toBe('Test message');
			expect(currentToasts[0].type).toBe('info');
		});

		it('should add a toast with specified type', () => {
			toasts.add('Error message', 'error');
			const currentToasts = get(toasts);

			expect(currentToasts[0].type).toBe('error');
		});

		it('should add multiple toasts', () => {
			toasts.add('Toast 1');
			toasts.add('Toast 2');
			toasts.add('Toast 3');
			const currentToasts = get(toasts);

			expect(currentToasts).toHaveLength(3);
		});
	});

	describe('remove', () => {
		it('should remove a toast by id', () => {
			const id = toasts.add('Test message', 'info', 0);
			expect(get(toasts)).toHaveLength(1);

			toasts.remove(id);
			expect(get(toasts)).toHaveLength(0);
		});

		it('should only remove the specified toast', () => {
			toasts.add('Toast 1', 'info', 0);
			const id2 = toasts.add('Toast 2', 'info', 0);
			toasts.add('Toast 3', 'info', 0);

			toasts.remove(id2);
			const currentToasts = get(toasts);

			expect(currentToasts).toHaveLength(2);
			expect(currentToasts.find((t) => t.message === 'Toast 2')).toBeUndefined();
		});
	});

	describe('clear', () => {
		it('should remove all toasts', () => {
			toasts.add('Toast 1', 'info', 0);
			toasts.add('Toast 2', 'info', 0);
			toasts.add('Toast 3', 'info', 0);

			toasts.clear();
			expect(get(toasts)).toHaveLength(0);
		});
	});

	describe('convenience methods', () => {
		it('should add success toast', () => {
			toasts.success('Success!');
			expect(get(toasts)[0].type).toBe('success');
		});

		it('should add error toast', () => {
			toasts.error('Error!');
			expect(get(toasts)[0].type).toBe('error');
		});

		it('should add warning toast', () => {
			toasts.warning('Warning!');
			expect(get(toasts)[0].type).toBe('warning');
		});

		it('should add info toast', () => {
			toasts.info('Info!');
			expect(get(toasts)[0].type).toBe('info');
		});
	});

	describe('auto-removal', () => {
		it('should auto-remove toast after duration', async () => {
			vi.useFakeTimers();

			toasts.add('Auto-remove', 'info', 1000);
			expect(get(toasts)).toHaveLength(1);

			vi.advanceTimersByTime(1000);
			expect(get(toasts)).toHaveLength(0);

			vi.useRealTimers();
		});

		it('should not auto-remove if duration is 0', async () => {
			vi.useFakeTimers();

			toasts.add('No auto-remove', 'info', 0);
			expect(get(toasts)).toHaveLength(1);

			vi.advanceTimersByTime(10000);
			expect(get(toasts)).toHaveLength(1);

			vi.useRealTimers();
		});
	});
});
