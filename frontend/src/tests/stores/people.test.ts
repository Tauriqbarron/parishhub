import { describe, it, expect, beforeEach, vi } from 'vitest';
import { get } from 'svelte/store';
import { peopleStore } from '$lib/stores/people';

// Mock the personApi
vi.mock('$lib/api', () => {
	return {
		personApi: {
			list: vi.fn(),
			get: vi.fn()
		}
	};
});

import { personApi } from '$lib/api';

describe('People Store', () => {
	beforeEach(() => {
		vi.clearAllMocks();
		peopleStore.reset();
	});

	describe('initial state', () => {
		it('should have correct initial values', () => {
			const state = get(peopleStore);
			expect(state.persons).toEqual([]);
			expect(state.total).toBe(0);
			expect(state.page).toBe(1);
			expect(state.pages).toBe(0);
			expect(state.perPage).toBe(20);
			expect(state.loading).toBe(false);
			expect(state.error).toBeNull();
			expect(state.filters).toEqual({
				sort_by: 'last_name',
				sort_order: 'asc'
			});
		});
	});

	describe('load', () => {
		it('should load persons with full details', async () => {
			const mockListResponse = {
				items: [
					{
						id: 1,
						first_name: 'John',
						middle_name: null,
						last_name: 'Doe',
						date_of_birth: null,
						gender: null,
						email: null,
						phone: null,
						address_line1: null,
						address_line2: null,
						city: null,
						postal_code: null,
						notes: null,
						created_at: '2024-01-01',
						updated_at: '2024-01-01'
					},
					{
						id: 2,
						first_name: 'Jane',
						middle_name: null,
						last_name: 'Smith',
						date_of_birth: null,
						gender: null,
						email: null,
						phone: null,
						address_line1: null,
						address_line2: null,
						city: null,
						postal_code: null,
						notes: null,
						created_at: '2024-01-01',
						updated_at: '2024-01-01'
					}
				],
				total: 2,
				page: 1,
				per_page: 20,
				pages: 1
			};

			const mockPerson1 = {
				id: 1,
				first_name: 'John',
				middle_name: null,
				last_name: 'Doe',
				date_of_birth: null,
				gender: null,
				email: null,
				phone: null,
				address_line1: null,
				address_line2: null,
				city: null,
				postal_code: null,
				notes: null,
				created_at: '2024-01-01',
				updated_at: '2024-01-01',
				household_memberships: [],
				sacraments: [],
				death: null
			};
			const mockPerson2 = {
				id: 2,
				first_name: 'Jane',
				middle_name: null,
				last_name: 'Smith',
				date_of_birth: null,
				gender: null,
				email: null,
				phone: null,
				address_line1: null,
				address_line2: null,
				city: null,
				postal_code: null,
				notes: null,
				created_at: '2024-01-01',
				updated_at: '2024-01-01',
				household_memberships: [],
				sacraments: [],
				death: null
			};

			vi.mocked(personApi.list).mockResolvedValue(mockListResponse);
			vi.mocked(personApi.get).mockImplementation(async (id: number) => {
				if (id === 1) return mockPerson1;
				if (id === 2) return mockPerson2;
				throw new Error('Not found');
			});

			await peopleStore.load();

			expect(personApi.list).toHaveBeenCalledWith({
				sort_by: 'last_name',
				sort_order: 'asc'
			});
			expect(personApi.get).toHaveBeenCalledTimes(2);
			expect(personApi.get).toHaveBeenCalledWith(1);
			expect(personApi.get).toHaveBeenCalledWith(2);

			const state = get(peopleStore);
			expect(state.persons).toHaveLength(2);
			expect(state.persons[0].first_name).toBe('John');
			expect(state.persons[1].first_name).toBe('Jane');
			expect(state.loading).toBe(false);
			expect(state.error).toBeNull();
		});

		it('should handle errors during load', async () => {
			vi.mocked(personApi.list).mockRejectedValue(new Error('Network error'));

			await peopleStore.load();

			const state = get(peopleStore);
			expect(state.loading).toBe(false);
			expect(state.error).toBe('Network error');
			expect(state.persons).toEqual([]);
		});

		it('should handle get() errors for individual persons', async () => {
			const mockListResponse = {
				items: [
					{
						id: 1,
						first_name: 'John',
						middle_name: null,
						last_name: 'Doe',
						date_of_birth: null,
						gender: null,
						email: null,
						phone: null,
						address_line1: null,
						address_line2: null,
						city: null,
						postal_code: null,
						notes: null,
						created_at: '2024-01-01',
						updated_at: '2024-01-01'
					}
				],
				total: 1,
				page: 1,
				per_page: 20,
				pages: 1
			};
			vi.mocked(personApi.list).mockResolvedValue(mockListResponse);
			vi.mocked(personApi.get).mockRejectedValue(new Error('Not found'));

			await peopleStore.load();

			const state = get(peopleStore);
			expect(state.error).toBe('Not found');
			expect(state.persons).toEqual([]);
		});
	});

	describe('setPage', () => {
		it('should call load with new page', async () => {
			const mockResponse = { items: [], total: 0, page: 2, per_page: 20, pages: 2 };
			vi.mocked(personApi.list).mockResolvedValue(mockResponse);

			await peopleStore.setPage(2);

			expect(personApi.list).toHaveBeenCalledWith(expect.objectContaining({ page: 2 }));
		});
	});

	describe('setFilters', () => {
		it('should merge filters and reset page to 1', async () => {
			const mockResponse = { items: [], total: 0, page: 1, per_page: 20, pages: 0 };
			vi.mocked(personApi.list).mockResolvedValue(mockResponse);

			await peopleStore.setFilters({ gender: 'male' });

			expect(personApi.list).toHaveBeenCalledWith(
				expect.objectContaining({
					gender: 'male'
				})
			);
		});
	});

	describe('setSort', () => {
		it('should update sort criteria and reload', async () => {
			const mockResponse = { items: [], total: 0, page: 1, per_page: 20, pages: 0 };
			vi.mocked(personApi.list).mockResolvedValue(mockResponse);

			await peopleStore.setSort('first_name', 'asc');

			expect(personApi.list).toHaveBeenCalledWith(
				expect.objectContaining({
					sort_by: 'first_name',
					sort_order: 'asc'
				})
			);
		});
	});

	describe('reset', () => {
		it('should clear all state', async () => {
			const mockResponse = { items: [], total: 0, page: 1, per_page: 20, pages: 0 };
			vi.mocked(personApi.list).mockResolvedValue(mockResponse);

			await peopleStore.load();
			peopleStore.reset();

			const state = get(peopleStore);
			expect(state.persons).toEqual([]);
			expect(state.total).toBe(0);
			expect(state.page).toBe(1);
			expect(state.error).toBeNull();
		});
	});
});
