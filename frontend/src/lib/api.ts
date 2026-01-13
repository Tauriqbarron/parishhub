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

// Household types and interfaces
export type HouseholdRole = 'head' | 'spouse' | 'child' | 'other';

export interface Household {
	id: number;
	name: string;
	address_line1: string | null;
	address_line2: string | null;
	city: string | null;
	postal_code: string | null;
	member_count: number;
	created_at: string;
	updated_at: string;
}

export interface HouseholdMember {
	person_id: number;
	household_id: number;
	role: HouseholdRole;
	is_primary_household: boolean;
	person: {
		id: number;
		first_name: string;
		middle_name: string | null;
		last_name: string;
	};
}

export interface HouseholdWithMembers extends Household {
	members: HouseholdMember[];
}

export interface HouseholdMembership {
	household_id: number;
	person_id: number;
	role: HouseholdRole;
	is_primary_household: boolean;
	household: Household;
}

// Family relationship types
export type RelationshipType = 'parent' | 'child' | 'spouse' | 'sibling';

export interface FamilyRelationship {
	id: number;
	person_id: number;
	related_person_id: number;
	relationship_type: RelationshipType;
	created_at: string;
}

export interface FamilyMember {
	id: number;
	first_name: string;
	middle_name: string | null;
	last_name: string;
	relationship_id: number;
}

export interface FamilyTree {
	parents: FamilyMember[];
	children: FamilyMember[];
	spouse: FamilyMember | null;
	siblings: FamilyMember[];
}

export interface PersonWithRelations extends Person {
	household_memberships: HouseholdMembership[];
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

// Sacrament types and interfaces
export interface SacramentCreate {
	person_id: number;
	sacrament_type: SacramentType;
	date_received: string;
	notes?: string | null;
	additional_data?: Record<string, unknown> | null;
}

export interface SacramentUpdate {
	sacrament_type?: SacramentType;
	date_received?: string;
	notes?: string | null;
	additional_data?: Record<string, unknown> | null;
}

// Sacrament API functions
export const sacramentApi = {
	getForPerson: (personId: number) => api.get<Sacrament[]>(`/persons/${personId}/sacraments`),

	create: (data: SacramentCreate) => api.post<Sacrament>('/sacraments', data),

	update: (id: number, data: SacramentUpdate) => api.put<Sacrament>(`/sacraments/${id}`, data),

	delete: (id: number) => api.delete<void>(`/sacraments/${id}`)
};

// Household filter and create types
export interface HouseholdFilters {
	search?: string;
	sort_by?: 'name' | 'created_at' | 'updated_at';
	sort_order?: 'asc' | 'desc';
	page?: number;
	per_page?: number;
}

export interface HouseholdCreate {
	name: string;
	address_line1?: string | null;
	address_line2?: string | null;
	city?: string | null;
	postal_code?: string | null;
	members?: Array<{
		person_id: number;
		role: HouseholdRole;
		is_primary_household?: boolean;
	}>;
}

export interface HouseholdUpdate {
	name?: string;
	address_line1?: string | null;
	address_line2?: string | null;
	city?: string | null;
	postal_code?: string | null;
}

export interface HouseholdMemberUpdate {
	role?: HouseholdRole;
	is_primary_household?: boolean;
}

function buildHouseholdQueryString(params: HouseholdFilters): string {
	const searchParams = new URLSearchParams();
	for (const [key, value] of Object.entries(params)) {
		if (value !== undefined && value !== null && value !== '') {
			searchParams.set(key, String(value));
		}
	}
	const qs = searchParams.toString();
	return qs ? `?${qs}` : '';
}

// Household API functions
export const householdApi = {
	list: (filters: HouseholdFilters = {}) =>
		api.get<PaginatedResponse<Household>>(`/households${buildHouseholdQueryString(filters)}`),

	get: (id: number) => api.get<HouseholdWithMembers>(`/households/${id}`),

	create: (data: HouseholdCreate) => api.post<HouseholdWithMembers>('/households', data),

	update: (id: number, data: HouseholdUpdate) => api.put<Household>(`/households/${id}`, data),

	delete: (id: number) => api.delete<void>(`/households/${id}`),

	addMember: (householdId: number, personId: number, role: HouseholdRole, isPrimary = true) =>
		api.post<HouseholdMember>(
			`/households/${householdId}/members?person_id=${personId}&role=${role}&is_primary_household=${isPrimary}`,
			{}
		),

	updateMember: (householdId: number, personId: number, data: HouseholdMemberUpdate) =>
		api.put<HouseholdMember>(`/households/${householdId}/members/${personId}`, data),

	removeMember: (householdId: number, personId: number) =>
		api.delete<void>(`/households/${householdId}/members/${personId}`)
};

// Relationship API functions
export const relationshipApi = {
	getForPerson: (personId: number) =>
		api.get<FamilyRelationship[]>(`/persons/${personId}/relationships`),

	getFamilyTree: (personId: number) => api.get<FamilyTree>(`/persons/${personId}/family-tree`),

	create: (personId: number, relatedPersonId: number, relationshipType: RelationshipType) =>
		api.post<FamilyRelationship>(`/persons/${personId}/relationships`, {
			related_person_id: relatedPersonId,
			relationship_type: relationshipType
		}),

	delete: (relationshipId: number) => api.delete<void>(`/relationships/${relationshipId}`)
};

// Dashboard statistics types and API
export interface DashboardStats {
	total_people: number;
	total_households: number;
	baptisms_this_year: number;
	marriages_this_year: number;
}

export interface RecentActivity {
	type: string;
	description: string;
	timestamp: string;
}

export interface SacramentTrend {
	year: number;
	baptism: number;
	first_communion: number;
	confirmation: number;
	marriage: number;
	holy_orders: number;
}

export interface DashboardData {
	stats: DashboardStats;
	recent_activity: RecentActivity[];
	sacrament_trends: SacramentTrend[];
}

export const statisticsApi = {
	getDashboard: () => api.get<DashboardData>('/statistics/dashboard')
};

// Analytics types
export interface Birth {
	id: number;
	baby_first_name: string;
	baby_last_name: string;
	date_of_birth: string;
	parent1_id: number | null;
	parent2_id: number | null;
	notes: string | null;
	created_at: string;
	updated_at: string;
}

export interface BirthCreate {
	baby_first_name: string;
	baby_last_name: string;
	date_of_birth: string;
	parent1_id?: number | null;
	parent2_id?: number | null;
	notes?: string | null;
}

export interface MassAttendance {
	id: number;
	date: string;
	mass_time: string | null;
	attendance_count: number;
	notes: string | null;
	created_at: string;
	updated_at: string;
}

export interface MassAttendanceCreate {
	date: string;
	mass_time?: string | null;
	attendance_count: number;
	notes?: string | null;
}

export interface PopulationSnapshot {
	id: number;
	date: string;
	registered_members: number;
	households: number;
	created_at: string;
	updated_at: string;
}

export interface YearlyCount {
	year: number;
	count: number;
}

export interface BirthStatistics {
	by_year: YearlyCount[];
	total: number;
	current_year: number;
}

export interface AttendanceTrend {
	weekly_average: number;
	monthly_average: number;
	yoy_change_percent: number | null;
	recent_weeks: Array<{
		date: string;
		count: number;
		mass_time: string | null;
	}>;
}

export interface PopulationGrowth {
	history: PopulationSnapshot[];
	current_members: number;
	current_households: number;
	growth_percent: number | null;
}

// Births API
export const birthsApi = {
	list: (filters: { page?: number; per_page?: number; year?: number } = {}) => {
		const params = new URLSearchParams();
		if (filters.page) params.set('page', String(filters.page));
		if (filters.per_page) params.set('per_page', String(filters.per_page));
		if (filters.year) params.set('year', String(filters.year));
		const qs = params.toString();
		return api.get<PaginatedResponse<Birth>>(`/births${qs ? `?${qs}` : ''}`);
	},

	get: (id: number) => api.get<Birth>(`/births/${id}`),

	create: (data: BirthCreate) => api.post<Birth>('/births', data),

	update: (id: number, data: Partial<BirthCreate>) => api.put<Birth>(`/births/${id}`, data),

	delete: (id: number) => api.delete<void>(`/births/${id}`),

	getStatistics: (year?: number) => {
		const qs = year ? `?year=${year}` : '';
		return api.get<BirthStatistics>(`/births/statistics${qs}`);
	}
};

// Mass Attendance API
export const attendanceApi = {
	list: (filters: { page?: number; per_page?: number; start_date?: string; end_date?: string } = {}) => {
		const params = new URLSearchParams();
		if (filters.page) params.set('page', String(filters.page));
		if (filters.per_page) params.set('per_page', String(filters.per_page));
		if (filters.start_date) params.set('start_date', filters.start_date);
		if (filters.end_date) params.set('end_date', filters.end_date);
		const qs = params.toString();
		return api.get<PaginatedResponse<MassAttendance>>(`/mass-attendance${qs ? `?${qs}` : ''}`);
	},

	get: (id: number) => api.get<MassAttendance>(`/mass-attendance/${id}`),

	create: (data: MassAttendanceCreate) => api.post<MassAttendance>('/mass-attendance', data),

	update: (id: number, data: Partial<MassAttendanceCreate>) =>
		api.put<MassAttendance>(`/mass-attendance/${id}`, data),

	delete: (id: number) => api.delete<void>(`/mass-attendance/${id}`),

	getStatistics: () => api.get<AttendanceTrend>('/mass-attendance/statistics')
};

// Population API
export const populationApi = {
	list: (filters: { page?: number; per_page?: number } = {}) => {
		const params = new URLSearchParams();
		if (filters.page) params.set('page', String(filters.page));
		if (filters.per_page) params.set('per_page', String(filters.per_page));
		const qs = params.toString();
		return api.get<PaginatedResponse<PopulationSnapshot>>(`/population${qs ? `?${qs}` : ''}`);
	},

	get: (id: number) => api.get<PopulationSnapshot>(`/population/${id}`),

	create: (data: { date: string; registered_members: number; households: number }) =>
		api.post<PopulationSnapshot>('/population', data),

	delete: (id: number) => api.delete<void>(`/population/${id}`),

	getStatistics: () => api.get<PopulationGrowth>('/population/statistics')
};
