const API_BASE = '/api';

async function request<T>(endpoint: string, options?: RequestInit): Promise<T> {
	const response = await fetch(`${API_BASE}${endpoint}`, {
		credentials: 'include',
		headers: {
			'Content-Type': 'application/json',
			...options?.headers
		},
		...options
	});

	if (!response.ok) {
		// Try to extract a useful error message from the response
		let message = 'Something went wrong. Please try again.';
		try {
			const contentType = response.headers.get('Content-Type') || '';
			if (contentType.includes('application/json')) {
				const errorData = await response.json();
				message = errorData.detail || errorData.message || message;
			}
		} catch {
			// Response wasn't valid JSON — use generic message
		}
		throw new Error(message);
	}

	if (response.status === 204) {
		return undefined as T;
	}

	// Guard against non-JSON responses on success too
	const contentType = response.headers.get('Content-Type') || '';
	if (!contentType.includes('application/json')) {
		throw new Error('Something went wrong. Please try again.');
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

	download: async (url: string): Promise<Blob> => {
		const response = await fetch(url);
		if (!response.ok) {
			throw new Error(`Download Error: ${response.status} ${response.statusText}`);
		}
		return response.blob();
	},

	health: () => request<{ status: string }>('/health')
};

// Types
export type Gender = 'male' | 'female' | 'other';

export type SacramentType =
	| 'baptism'
	| 'first_communion'
	| 'confirmation'
	| 'marriage'
	| 'holy_orders'
	| 'anointing';

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
	death: DeathWithPerson | null;
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
	is_deceased?: boolean;
	has_household?: boolean;
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

export interface MarriageSideEffects {
	household_created: boolean;
	household_id: number | null;
	household_name: string | null;
	spouse_relationship_created: boolean;
}

export interface SacramentResponseWithEffects extends Sacrament {
	marriage_side_effects?: MarriageSideEffects | null;
}

// Sacrament API functions
export const sacramentApi = {
	getForPerson: (personId: number) => api.get<Sacrament[]>(`/persons/${personId}/sacraments`),

	create: (data: SacramentCreate) => api.post<SacramentResponseWithEffects>('/sacraments', data),

	update: (id: number, data: SacramentUpdate) => api.put<Sacrament>(`/sacraments/${id}`, data),

	delete: (id: number) => api.delete<void>(`/sacraments/${id}`),

	undoMarriageHousehold: (sacramentId: number) =>
		api.delete<void>(`/sacraments/${sacramentId}/auto-household`)
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
	deaths_this_year: number;
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
	anointing: number;
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
	mass_time_id: number | null;
	mass_time: string | null;
	mass_time_name: string | null;
	mass_time_time: string | null;
	attendance_count: number;
	notes: string | null;
	created_at: string;
	updated_at: string;
}

export interface MassAttendanceCreate {
	date: string;
	mass_time_id?: number | null;
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

export interface WeeklyDataPoint {
	date: string;
	count: number;
}

export interface MassTimeBreakdown {
	mass_time: string;
	mass_time_id: number | null;
	total_attendance: number;
	weekly_average: number;
	recent_weeks: WeeklyDataPoint[];
}

export interface AttendanceTrendExtended extends AttendanceTrend {
	by_mass_time: MassTimeBreakdown[];
}

export interface PopulationGrowth {
	history: PopulationSnapshot[];
	current_members: number;
	current_households: number;
	growth_percent: number | null;
}

// Death types
export interface Death {
	id: number;
	person_id: number;
	date_of_death: string;
	place_of_death: string | null;
	cause_of_death: string | null;
	burial_date: string | null;
	burial_location: string | null;
	funeral_date: string | null;
	funeral_location: string | null;
	officiating_priest_id: number | null;
	notes: string | null;
	created_at: string;
	updated_at: string;
}

export interface DeathCreate {
	person_id: number;
	date_of_death: string;
	place_of_death?: string | null;
	cause_of_death?: string | null;
	burial_date?: string | null;
	burial_location?: string | null;
	funeral_date?: string | null;
	funeral_location?: string | null;
	officiating_priest_id?: number | null;
	notes?: string | null;
}

export interface DeathWithPerson extends Death {
	person: {
		id: number;
		first_name: string;
		last_name: string;
	};
	officiating_priest: {
		id: number;
		first_name: string;
		last_name: string;
	} | null;
}

export interface DeathStatistics {
	by_year: YearlyCount[];
	total: number;
	current_year_count: number;
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
	list: (
		filters: { page?: number; per_page?: number; start_date?: string; end_date?: string } = {}
	) => {
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

	getStatistics: (includeBreakdown = false, startDate?: string, endDate?: string) => {
		const params = new URLSearchParams();
		if (includeBreakdown) params.set('include_breakdown', 'true');
		if (startDate) params.set('start_date', startDate);
		if (endDate) params.set('end_date', endDate);
		const qs = params.toString();
		return api.get<AttendanceTrend | AttendanceTrendExtended>(
			`/mass-attendance/statistics${qs ? `?${qs}` : ''}`
		);
	}
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

// Deaths API
export const deathsApi = {
	list: (filters: { page?: number; per_page?: number; year?: number } = {}) => {
		const params = new URLSearchParams();
		if (filters.page) params.set('page', String(filters.page));
		if (filters.per_page) params.set('per_page', String(filters.per_page));
		if (filters.year) params.set('year', String(filters.year));
		const qs = params.toString();
		return api.get<PaginatedResponse<DeathWithPerson>>(`/deaths${qs ? `?${qs}` : ''}`);
	},

	get: (id: number) => api.get<DeathWithPerson>(`/deaths/${id}`),

	create: (data: DeathCreate) => api.post<Death>('/deaths', data),

	update: (id: number, data: Partial<DeathCreate>) => api.put<Death>(`/deaths/${id}`, data),

	delete: (id: number) => api.delete<void>(`/deaths/${id}`),

	getStatistics: (year?: number) => {
		const qs = year ? `?year=${year}` : '';
		return api.get<DeathStatistics>(`/deaths/statistics${qs}`);
	},

	getForPerson: (personId: number) => api.get<DeathWithPerson>(`/persons/${personId}/death`)
};

// Mass Times types
export interface MassTime {
	id: number;
	name: string;
	time: string;
	day_of_week: number | null;
	is_active: boolean;
	created_at: string;
	updated_at: string;
}

export interface MassTimeCreate {
	name: string;
	time: string;
	day_of_week?: number | null;
	is_active?: boolean;
}

// Mass Times API
export const massTimesApi = {
	list: (activeOnly = true) => {
		const qs = activeOnly ? '?active_only=true' : '?active_only=false';
		return api.get<MassTime[]>(`/mass-times${qs}`);
	},
	get: (id: number) => api.get<MassTime>(`/mass-times/${id}`),
	create: (data: MassTimeCreate) => api.post<MassTime>('/mass-times', data),
	update: (id: number, data: Partial<MassTimeCreate>) =>
		api.put<MassTime>(`/mass-times/${id}`, data),
	delete: (id: number) => api.delete<void>(`/mass-times/${id}`)
};

// Registration types
export interface RegistrationSubmitResponse {
	success: boolean;
	household_id: number;
	member_ids: number[];
	message: string;
}

export interface IndividualRegistrationResponse {
	person_id: number;
	message: string;
}

// Registration URL types
export interface RegistrationURLConfig {
	base_url: string;
}

export interface RegistrationURLResponse {
	base_url: string;
	registration_url: string;
}

// Registration API
export const registrationApi = {
	submit: (session: {
		id: string;
		household: {
			name: string;
			address: string;
			city: string;
			state: string;
			zipCode: string;
			phone: string;
			email: string;
			attendingSince: string;
		};
		members: Array<{
			tempId: string;
			firstName: string;
			middleName: string;
			lastName: string;
			dateOfBirth: string;
			gender: string;
			phone: string;
			email: string;
			isHeadOfHousehold: boolean;
			livesInHousehold: boolean;
			sacraments: Array<{
				type: string;
				date: string;
				additionalData: Record<string, unknown>;
			}>;
			relationships: Array<{
				targetTempId: string;
				relationshipType: string;
			}>;
		}>;
		consent?: {
			dataPrivacyConsent: boolean;
			photoMediaRelease: boolean;
			commEmail: boolean;
			commSms: boolean;
			commPhone: boolean;
			termsAcknowledged: boolean;
			consentedAt: string;
		};
	}) => {
		// Flatten relationships and sacraments from nested member arrays
		// into top-level arrays matching the backend schema
		const relationships = session.members.flatMap((m) =>
			m.relationships.map((r) => ({
				fromTempId: m.tempId,
				toTempId: r.targetTempId,
				relationshipType: r.relationshipType
			}))
		);

		const sacraments = session.members.flatMap((m) =>
			m.sacraments.map((s) => ({
				memberTempId: m.tempId,
				sacramentType: s.type,
				date: s.date || null,
				additionalData: s.additionalData || {}
			}))
		);

		const payload = {
			household_name: session.household.name,
			street_address: session.household.address || null,
			city: session.household.city || null,
			state: session.household.state || null,
			zipCode: session.household.zipCode || null,
			phone: session.household.phone || null,
			email: session.household.email || null,
			attendingSince: session.household.attendingSince || null,
			members: session.members.map((m) => ({
				tempId: m.tempId,
				firstName: m.firstName,
				middleName: m.middleName || null,
				lastName: m.lastName,
				dateOfBirth: m.dateOfBirth || null,
				gender: m.gender || null,
				phone: m.phone || null,
				email: m.email || null,
				isHeadOfHousehold: m.isHeadOfHousehold,
				livesInHousehold: m.livesInHousehold ?? true
			})),
			relationships,
			sacraments,
			consent: session.consent?.dataPrivacyConsent
				? {
						dataPrivacyConsent: session.consent.dataPrivacyConsent,
						photoMediaRelease: session.consent.photoMediaRelease,
						commEmail: session.consent.commEmail,
						commSms: session.consent.commSms,
						commPhone: session.consent.commPhone,
						termsAcknowledged: session.consent.termsAcknowledged
					}
				: undefined
		};

		return api.post<RegistrationSubmitResponse>('/register', payload);
	},

	submitIndividual: (session: {
		members: Array<{
			tempId: string;
			firstName: string;
			middleName: string;
			lastName: string;
			dateOfBirth: string;
			gender: string;
			phone: string;
			email: string;
			sacraments: Array<{
				type: string;
				date: string;
				additionalData: Record<string, unknown>;
			}>;
		}>;
		consent?: {
			dataPrivacyConsent: boolean;
			photoMediaRelease: boolean;
			commEmail: boolean;
			commSms: boolean;
			commPhone: boolean;
			termsAcknowledged: boolean;
			consentedAt: string;
		};
	}) => {
		const member = session.members[0];
		if (!member) throw new Error('No member data found');

		const sacraments = member.sacraments.map((s) => ({
			memberTempId: member.tempId,
			sacramentType: s.type,
			date: s.date || null,
			additionalData: s.additionalData || {}
		}));

		const payload = {
			firstName: member.firstName,
			middleName: member.middleName || null,
			lastName: member.lastName,
			dateOfBirth: member.dateOfBirth || null,
			gender: member.gender || null,
			phone: member.phone || null,
			email: member.email || null,
			sacraments,
			consent: session.consent?.dataPrivacyConsent
				? {
						dataPrivacyConsent: session.consent.dataPrivacyConsent,
						photoMediaRelease: session.consent.photoMediaRelease,
						commEmail: session.consent.commEmail,
						commSms: session.consent.commSms,
						commPhone: session.consent.commPhone,
						termsAcknowledged: session.consent.termsAcknowledged
					}
				: undefined
		};

		return api.post<IndividualRegistrationResponse>('/register/individual', payload);
	},

	getUrl: () => api.get<RegistrationURLResponse>('/v1/registration/url'),

	updateUrl: (config: RegistrationURLConfig) =>
		api.put<RegistrationURLResponse>('/v1/registration/url', config)
};
