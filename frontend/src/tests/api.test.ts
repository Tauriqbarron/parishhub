import { describe, it, expect, beforeEach, vi } from 'vitest';

// Mock fetch globally
const mockFetch = vi.fn();
vi.stubGlobal('fetch', mockFetch);

// Import after mocking
import { api, personApi, householdApi, sacramentApi } from '$lib/api';

describe('API Module', () => {
	beforeEach(() => {
		mockFetch.mockReset();
	});

	describe('api.get', () => {
		it('should make a GET request with correct headers', async () => {
			mockFetch.mockResolvedValueOnce({
				ok: true,
				status: 200,
				json: () => Promise.resolve({ data: 'test' })
			});

			const result = await api.get('/test');

			expect(mockFetch).toHaveBeenCalledWith('/api/test', {
				credentials: 'include',
				headers: {
					'Content-Type': 'application/json'
				}
			});
			expect(result).toEqual({ data: 'test' });
		});

		it('should throw error on non-ok response', async () => {
			mockFetch.mockResolvedValueOnce({
				ok: false,
				status: 404,
				statusText: 'Not Found'
			});

			await expect(api.get('/test')).rejects.toThrow('API Error: 404 Not Found');
		});
	});

	describe('api.post', () => {
		it('should make a POST request with body', async () => {
			mockFetch.mockResolvedValueOnce({
				ok: true,
				status: 201,
				json: () => Promise.resolve({ id: 1 })
			});

			const result = await api.post('/test', { name: 'test' });

			expect(mockFetch).toHaveBeenCalledWith('/api/test', {
				credentials: 'include',
				headers: {
					'Content-Type': 'application/json'
				},
				method: 'POST',
				body: JSON.stringify({ name: 'test' })
			});
			expect(result).toEqual({ id: 1 });
		});
	});

	describe('api.put', () => {
		it('should make a PUT request with body', async () => {
			mockFetch.mockResolvedValueOnce({
				ok: true,
				status: 200,
				json: () => Promise.resolve({ id: 1, name: 'updated' })
			});

			const result = await api.put('/test/1', { name: 'updated' });

			expect(mockFetch).toHaveBeenCalledWith('/api/test/1', {
				credentials: 'include',
				headers: {
					'Content-Type': 'application/json'
				},
				method: 'PUT',
				body: JSON.stringify({ name: 'updated' })
			});
			expect(result).toEqual({ id: 1, name: 'updated' });
		});
	});

	describe('api.delete', () => {
		it('should make a DELETE request', async () => {
			mockFetch.mockResolvedValueOnce({
				ok: true,
				status: 204
			});

			const result = await api.delete('/test/1');

			expect(mockFetch).toHaveBeenCalledWith('/api/test/1', {
				credentials: 'include',
				headers: {
					'Content-Type': 'application/json'
				},
				method: 'DELETE'
			});
			expect(result).toBeUndefined();
		});
	});

	describe('personApi', () => {
		it('should list persons with filters', async () => {
			mockFetch.mockResolvedValueOnce({
				ok: true,
				status: 200,
				json: () =>
					Promise.resolve({
						items: [],
						total: 0,
						page: 1,
						per_page: 20,
						pages: 0
					})
			});

			await personApi.list({ search: 'john', gender: 'male' });

			expect(mockFetch).toHaveBeenCalledWith('/api/persons?search=john&gender=male', {
				credentials: 'include',
				headers: { 'Content-Type': 'application/json' }
			});
		});

		it('should get a single person', async () => {
			mockFetch.mockResolvedValueOnce({
				ok: true,
				status: 200,
				json: () => Promise.resolve({ id: 1, first_name: 'John' })
			});

			await personApi.get(1);

			expect(mockFetch).toHaveBeenCalledWith('/api/persons/1', {
				credentials: 'include',
				headers: { 'Content-Type': 'application/json' }
			});
		});

		it('should create a person', async () => {
			mockFetch.mockResolvedValueOnce({
				ok: true,
				status: 201,
				json: () => Promise.resolve({ id: 1, first_name: 'John', last_name: 'Doe' })
			});

			await personApi.create({
				first_name: 'John',
				last_name: 'Doe',
				middle_name: null,
				date_of_birth: null,
				gender: null,
				email: null,
				phone: null,
				address_line1: null,
				address_line2: null,
				city: null,
				postal_code: null,
				notes: null
			});

			expect(mockFetch).toHaveBeenCalledWith('/api/persons', expect.objectContaining({
				method: 'POST'
			}));
		});

		it('should update a person', async () => {
			mockFetch.mockResolvedValueOnce({
				ok: true,
				status: 200,
				json: () => Promise.resolve({ id: 1, first_name: 'Jane' })
			});

			await personApi.update(1, { first_name: 'Jane' });

			expect(mockFetch).toHaveBeenCalledWith('/api/persons/1', expect.objectContaining({
				method: 'PUT'
			}));
		});

		it('should delete a person', async () => {
			mockFetch.mockResolvedValueOnce({
				ok: true,
				status: 204
			});

			await personApi.delete(1);

			expect(mockFetch).toHaveBeenCalledWith('/api/persons/1', expect.objectContaining({
				method: 'DELETE'
			}));
		});
	});

	describe('householdApi', () => {
		it('should list households', async () => {
			mockFetch.mockResolvedValueOnce({
				ok: true,
				status: 200,
				json: () =>
					Promise.resolve({
						items: [],
						total: 0,
						page: 1,
						per_page: 20,
						pages: 0
					})
			});

			await householdApi.list({ search: 'smith' });

			expect(mockFetch).toHaveBeenCalledWith('/api/households?search=smith', {
				credentials: 'include',
				headers: { 'Content-Type': 'application/json' }
			});
		});

		it('should get a household with members', async () => {
			mockFetch.mockResolvedValueOnce({
				ok: true,
				status: 200,
				json: () => Promise.resolve({ id: 1, name: 'Smith Family', members: [] })
			});

			await householdApi.get(1);

			expect(mockFetch).toHaveBeenCalledWith('/api/households/1', {
				credentials: 'include',
				headers: { 'Content-Type': 'application/json' }
			});
		});

		it('should create a household', async () => {
			mockFetch.mockResolvedValueOnce({
				ok: true,
				status: 201,
				json: () => Promise.resolve({ id: 1, name: 'New Family', members: [] })
			});

			await householdApi.create({ name: 'New Family' });

			expect(mockFetch).toHaveBeenCalledWith('/api/households', expect.objectContaining({
				method: 'POST'
			}));
		});

		it('should add member to household', async () => {
			mockFetch.mockResolvedValueOnce({
				ok: true,
				status: 201,
				json: () => Promise.resolve({ person_id: 1, household_id: 1, role: 'head' })
			});

			await householdApi.addMember(1, 1, 'head', true);

			expect(mockFetch).toHaveBeenCalledWith(
				'/api/households/1/members?person_id=1&role=head&is_primary_household=true',
				expect.objectContaining({ method: 'POST' })
			);
		});

		it('should remove member from household', async () => {
			mockFetch.mockResolvedValueOnce({
				ok: true,
				status: 204
			});

			await householdApi.removeMember(1, 2);

			expect(mockFetch).toHaveBeenCalledWith('/api/households/1/members/2', expect.objectContaining({
				method: 'DELETE'
			}));
		});
	});

	describe('sacramentApi', () => {
		it('should get sacraments for person', async () => {
			mockFetch.mockResolvedValueOnce({
				ok: true,
				status: 200,
				json: () => Promise.resolve([])
			});

			await sacramentApi.getForPerson(1);

			expect(mockFetch).toHaveBeenCalledWith('/api/persons/1/sacraments', {
				credentials: 'include',
				headers: { 'Content-Type': 'application/json' }
			});
		});

		it('should create a sacrament', async () => {
			mockFetch.mockResolvedValueOnce({
				ok: true,
				status: 201,
				json: () =>
					Promise.resolve({
						id: 1,
						person_id: 1,
						sacrament_type: 'baptism',
						date_received: '2024-01-15'
					})
			});

			await sacramentApi.create({
				person_id: 1,
				sacrament_type: 'baptism',
				date_received: '2024-01-15'
			});

			expect(mockFetch).toHaveBeenCalledWith('/api/sacraments', expect.objectContaining({
				method: 'POST'
			}));
		});

		it('should delete a sacrament', async () => {
			mockFetch.mockResolvedValueOnce({
				ok: true,
				status: 204
			});

			await sacramentApi.delete(1);

			expect(mockFetch).toHaveBeenCalledWith('/api/sacraments/1', expect.objectContaining({
				method: 'DELETE'
			}));
		});
	});
});
