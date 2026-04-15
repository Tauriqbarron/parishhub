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
	location: string | null;
	attendance_count: number;
	ministry_id?: number;
	ministry_name?: string;
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

	addMember: (ministryId: number, data: { email: string; name?: string; role?: string }) =>
		request<{ id: number; person_name: string | null; message: string }>(
			`/member/ministries/${ministryId}/members`,
			{ method: 'POST', body: JSON.stringify(data) }
		),

	removeMember: (ministryId: number, memberId: number) =>
		request<{ message: string }>(`/member/ministries/${ministryId}/members/${memberId}`, {
			method: 'DELETE'
		}),

	listEvents: (ministryId: number) =>
		request<{ events: MinistryEvent[] }>(`/member/ministries/${ministryId}/events`),

	createEvent: (
		ministryId: number,
		data: { title: string; description?: string; event_date: string; location?: string }
	) =>
		request<MinistryEvent>(`/member/ministries/${ministryId}/events`, {
			method: 'POST',
			body: JSON.stringify(data)
		})
};
