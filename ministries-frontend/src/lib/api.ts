const API_BASE = 'http://localhost:8000/api';

function getToken(): string | null {
	if (typeof window === 'undefined') return null;
	return localStorage.getItem('member_token');
}

export function setToken(token: string) {
	if (typeof window !== 'undefined') {
		localStorage.setItem('member_token', token);
	}
}

export function clearToken() {
	if (typeof window !== 'undefined') {
		localStorage.removeItem('member_token');
	}
}

async function request<T>(endpoint: string, options?: RequestInit): Promise<T> {
	const token = getToken();
	const headers: Record<string, string> = {
		'Content-Type': 'application/json',
		...((options?.headers as Record<string, string>) || {})
	};
	if (token) {
		headers['Authorization'] = `Bearer ${token}`;
	}

	const response = await fetch(`${API_BASE}${endpoint}`, {
		...options,
		headers
	});

	if (!response.ok) {
		let message = 'Something went wrong';
		try {
			const data = await response.json();
			message = data.detail || data.message || message;
		} catch {}
		if (response.status === 401) {
			clearToken();
			if (typeof window !== 'undefined') window.location.href = '/login';
		}
		throw new Error(message);
	}

	if (response.status === 204) return undefined as T;
	return response.json();
}

// Types
export interface MemberUser {
	email: string;
	name: string | null;
	picture: string | null;
	roles: Array<{ role: string; ministry_id: number }>;
}

export interface LoginResponse {
	token: string;
	user: MemberUser;
}

export interface MinistrySummary {
	id: number;
	name: string;
	description: string | null;
	is_active: boolean;
	user_role: string | null;
	member_count: number;
}

export interface MinistryMember {
	id: number;
	person_id: number;
	person_name: string | null;
	role: string;
	joined_date: string | null;
	is_active: boolean;
}

export interface MinistryEvent {
	id: number;
	title: string;
	description: string | null;
	event_date: string;
	start_time: string | null;
	end_time: string | null;
	location: string | null;
	event_type: string;
	capacity: number | null;
	is_cancelled: boolean;
	recurrence_rule: string | null;
	rsvp_count: number;
	spots_remaining: number | null;
	attendance_count: number;
	ministry_id?: number;
	ministry_name?: string;
}

export interface EventDetail extends MinistryEvent {
	user_rsvp: string | null;
	rsvp_summary: { going: number; maybe: number; not_going: number };
	rsvps: Array<{ id: number; person_id: number; person_name: string | null; status: string }>;
	attendance: Array<{ person_id: number; person_name: string | null; attended: boolean }>;
}

export interface EventRSVP {
	id: number;
	event_id: number;
	person_id: number;
	person_name: string | null;
	status: string;
}

export interface WeekDashboard {
	week_start: string;
	week_end: string;
	events: MinistryEvent[];
}

// API
export const memberApi = {
	login: (idToken: string) =>
		request<LoginResponse>('/auth/member/login', {
			method: 'POST',
			body: JSON.stringify({ id_token: idToken })
		}),

	me: () => request<MemberUser>('/auth/member/me'),

	dashboard: () => request<WeekDashboard>('/member/dashboard/week'),

	ministries: () => request<{ ministries: MinistrySummary[] }>('/member/ministries'),

	ministryDetail: (id: number) =>
		request<{
			id: number;
			name: string;
			description: string | null;
			is_active: boolean;
			user_role: string | null;
			members: MinistryMember[];
			events: MinistryEvent[];
		}>(`/member/ministries/${id}`),

	addMember: (ministryId: number, data: { email?: string; name?: string; person_id?: number; role?: string }) =>
		request<{ id: number; person_name: string | null; message: string }>(
			`/member/ministries/${ministryId}/members`,
			{ method: 'POST', body: JSON.stringify(data) }
		),

	searchPersons: (query: string) =>
		request<{ items: Array<{ id: number; first_name: string; last_name: string; email: string | null }> }>(
			`/member/persons/search?q=${encodeURIComponent(query)}`
		),

	eventDetail: (eventId: number) =>
		request<EventDetail>(`/member/events/${eventId}`),

	rsvp: (eventId: number, status: string) =>
		request<{ id: number; status: string; rsvp_count: number; spots_remaining: number | null }>(
			`/member/events/${eventId}/rsvp`,
			{ method: 'POST', body: JSON.stringify({ status }) }
		),

	getRsvps: (eventId: number) =>
		request<{ rsvps: EventRSVP[]; going_count: number; maybe_count: number; not_going_count: number }>(
			`/member/events/${eventId}/rsvps`
		),

	recordAttendance: (eventId: number, personIds: number[]) =>
		request<{ recorded: number }>(
			`/member/events/${eventId}/attendance`,
			{ method: 'POST', body: JSON.stringify({ person_ids: personIds }) }
		),

	getAttendance: (eventId: number) =>
		request<{ attendance: Array<{ person_id: number; person_name: string | null; attended: boolean }> }>(
			`/member/events/${eventId}/attendance`
		),

	removeMember: (ministryId: number, memberId: number) =>
		request<{ message: string }>(`/member/ministries/${ministryId}/members/${memberId}`, {
			method: 'DELETE'
		}),

	listEvents: (ministryId: number) =>
		request<{ events: MinistryEvent[] }>(`/member/ministries/${ministryId}/events`),

	createEvent: (
		ministryId: number,
		data: { title: string; description?: string; event_date: string; location?: string; start_time?: string; end_time?: string; event_type?: string; capacity?: number; recurrence_rule?: string; recurrence_end?: string }
	) =>
		request<MinistryEvent>(`/member/ministries/${ministryId}/events`, {
			method: 'POST',
			body: JSON.stringify(data)
		})
};
