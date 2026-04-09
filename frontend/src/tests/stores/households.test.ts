import { describe, it, expect, beforeEach, vi } from 'vitest';
import { get } from 'svelte/store';
import { householdsStore } from '$lib/stores/households';

// Mock the householdApi
vi.mock('$lib/api', () => {
	return {
		householdApi: {
			list: vi.fn()
		}
	};
});

import { householdApi } from '$lib/api';

describe('Households Store', () => {
	beforeEach(() => {
		vi.clearAllMocks();
		householdsStore.reset();
	});

	describe('initial state', () => {
		it('should have correct initial values', () => {
			const state = get(householdsStore);
			expect(state.households).toEqual([]);
			expect(state.total).toBe(0);
			expect(state.page).toBe(1);
			expect(state.pages).toBe(0);
			expect(state.perPage).toBe(20);
			expect(state.loading).toBe(false);
			expect(state.error).toBeNull();
			expect(state.filters).toEqual({
				sort_by: 'name',
				sort_order: 'asc'
			});
		});
	});

	describe('load', () => {
		it('should load households and update state', async () => {
			const mockResponse = {
				items: [
					{
						id: 1,
						name: 'Household 1',
						address_line1: null,
						address_line2: null,
						city: null,
						postal_code: null,
						member_count: 3,
						created_at: '2024-01-01',
						updated_at: '2024-01-01'
					},
					{
						id: 2,
						name: 'Household 2',
						address_line1: null,
						address_line2: null,
						city: null,
						postal_code: null,
						member_count: 4,
						created_at: '2024-01-01',
						updated_at: '2024-01-01'
					}
				],
				total: 2,
				page: 1,
				per_page: 20,
				pages: 1
			};
			vi.mocked(householdApi.list).mockResolvedValue(mockResponse);

			await householdsStore.load();

			// Should be called with merged filters: default sort
			expect(householdApi.list).toHaveBeenCalledWith({
				sort_by: 'name',
				sort_order: 'asc'
			});

			const state = get(householdsStore);
			expect(state.households).toEqual(mockResponse.items);
			expect(state.total).toBe(2);
			expect(state.page).toBe(1);
			expect(state.perPage).toBe(20);
			expect(state.loading).toBe(false);
			expect(state.error).toBeNull();
		});

		it('should accept custom filters', async () => {
			const mockResponse = { items: [], total: 0, page: 1, per_page: 10, pages: 0 };
			vi.mocked(householdApi.list).mockResolvedValue(mockResponse);

			await householdsStore.load({ search: 'test', per_page: 10 });

			expect(householdApi.list).toHaveBeenCalledWith({
				sort_by: 'name',
				sort_order: 'asc',
				search: 'test',
				per_page: 10
			});
		});

		it('should handle errors', async () => {
			const errorMessage = 'Failed to fetch';
			vi.mocked(householdApi.list).mockRejectedValue(new Error(errorMessage));

			await householdsStore.load();

			const state = get(householdsStore);
			expect(state.loading).toBe(false);
			expect(state.error).toBe(errorMessage);
			expect(state.households).toEqual([]);
		});

		it('should set loading state while fetching', async () => {
			let resolvePromise!: (value: any) => void;
			const promise = new Promise<
				import('$lib/api').PaginatedResponse<import('$lib/api').Household>
			>((resolve) => {
				resolvePromise = resolve;
			});
			vi.mocked(householdApi.list).mockReturnValue(promise);

			householdsStore.load();
			expect(get(householdsStore).loading).toBe(true);

			resolvePromise!({ items: [], total: 0, page: 1, per_page: 20, pages: 0 });
			await promise;
		});
	});

	describe('setPage', () => {
		it('should call load with new page', async () => {
			const mockResponse = { items: [], total: 0, page: 2, per_page: 20, pages: 2 };
			vi.mocked(householdApi.list).mockResolvedValue(mockResponse);

			await householdsStore.setPage(2);

			expect(householdApi.list).toHaveBeenCalledWith(expect.objectContaining({ page: 2 }));
		});
	});

	describe('setFilters', () => {
		it('should update filters and reload with page 1', async () => {
			const mockResponse = { items: [], total: 0, page: 1, per_page: 20, pages: 0 };
			vi.mocked(householdApi.list).mockResolvedValue(mockResponse);

			await householdsStore.setFilters({ sort_by: 'created_at' });

			expect(householdApi.list).toHaveBeenCalledWith(
				expect.objectContaining({
					sort_by: 'created_at'
				})
			);
		});
	});

	describe('setSort', () => {
		it('should update sort fields and reload', async () => {
			const mockResponse = { items: [], total: 0, page: 1, per_page: 20, pages: 0 };
			vi.mocked(householdApi.list).mockResolvedValue(mockResponse);

			await householdsStore.setSort('name', 'desc');

			expect(householdApi.list).toHaveBeenCalledWith(
				expect.objectContaining({
					sort_by: 'name',
					sort_order: 'desc'
				})
			);
		});
	});

	describe('reset', () => {
		it('should reset to initial state', async () => {
			const mockResponse = { items: [], total: 0, page: 1, per_page: 20, pages: 0 };
			vi.mocked(householdApi.list).mockResolvedValue(mockResponse);

			await householdsStore.load();
			householdsStore.reset();

			const state = get(householdsStore);
			expect(state.households).toEqual([]);
			expect(state.total).toBe(0);
			expect(state.page).toBe(1);
			expect(state.loading).toBe(false);
			expect(state.error).toBeNull();
		});
	});
});
