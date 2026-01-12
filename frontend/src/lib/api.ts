const API_BASE = '/api';

async function request<T>(endpoint: string, options?: RequestInit): Promise<T> {
	const response = await fetch(`${API_BASE}${endpoint}`, {
		headers: {
			'Content-Type': 'application/json',
			...options?.headers
		},
		...options
	});

	if (!response.ok) {
		throw new Error(`API Error: ${response.status} ${response.statusText}`);
	}

	return response.json();
}

export const api = {
	get: <T>(endpoint: string) => request<T>(endpoint),

	post: <T>(endpoint: string, data: unknown) =>
		request<T>(endpoint, {
			method: 'POST',
			body: JSON.stringify(data)
		}),

	put: <T>(endpoint: string, data: unknown) =>
		request<T>(endpoint, {
			method: 'PUT',
			body: JSON.stringify(data)
		}),

	delete: <T>(endpoint: string) =>
		request<T>(endpoint, {
			method: 'DELETE'
		}),

	health: () => request<{ status: string }>('/health')
};

// Types
export type Gender = 'male' | 'female' | 'other';

export type SacramentType =
	| 'baptism'
	| 'first_communion'
	| 'confirmation'
	| 'marriage'
	| 'holy_orders';

export interface Sacrament {
	id: number;
	person_id: number;
	sacrament_type: SacramentType;
	date_received: string;
	notes: string | null;
	additional_data: Record<string, unknown> | null;
	created_at: string;
	updated_at: string;
}

export interface Person {
	id: number;
	first_name: string;
	middle_name: string | null;
	last_name: string;
	date_of_birth: string | null;
	gender: Gender | null;
	email: string | null;
	phone: string | null;
	address_line1: string | null;
	address_line2: string | null;
	city: string | null;
	postal_code: string | null;
	notes: string | null;
	created_at: string;
	updated_at: string;
}

export interface PersonWithRelations extends Person {
	household_memberships: unknown[];
	sacraments: Sacrament[];
}

export interface PaginatedResponse<T> {
	items: T[];
	total: number;
	page: number;
	per_page: number;
	pages: number;
}

export interface PersonFilters {
	search?: string;
	gender?: Gender;
	min_age?: number;
	max_age?: number;
	has_sacrament?: SacramentType;
	missing_sacrament?: SacramentType;
	sort_by?: 'first_name' | 'last_name' | 'email' | 'created_at' | 'updated_at' | 'date_of_birth';
	sort_order?: 'asc' | 'desc';
	page?: number;
	per_page?: number;
}

function buildQueryString(params: PersonFilters): string {
	const searchParams = new URLSearchParams();
	for (const [key, value] of Object.entries(params)) {
		if (value !== undefined && value !== null && value !== '') {
			searchParams.set(key, String(value));
		}
	}
	const qs = searchParams.toString();
	return qs ? `?${qs}` : '';
}

// Person API functions
export const personApi = {
	list: (filters: PersonFilters = {}) =>
		api.get<PaginatedResponse<Person>>(`/persons${buildQueryString(filters)}`),

	get: (id: number) => api.get<PersonWithRelations>(`/persons/${id}`),

	create: (data: Omit<Person, 'id' | 'created_at' | 'updated_at'>) =>
		api.post<Person>('/persons', data),

	update: (id: number, data: Partial<Omit<Person, 'id' | 'created_at' | 'updated_at'>>) =>
		api.put<Person>(`/persons/${id}`, data),

	delete: (id: number) => api.delete<void>(`/persons/${id}`)
};
