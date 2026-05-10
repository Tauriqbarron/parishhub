import { api } from '$lib/api';

export interface RosterRole {
	id: number;
	name: string;
	description: string | null;
	person_count: number;
	created_at: string;
	updated_at: string;
}

export interface RosterRoleCreate {
	name: string;
	description?: string;
}

export interface RosterRoleUpdate {
	name?: string;
	description?: string;
}

export interface PersonRosterRole {
	id: number;
	person_id: number;
	role_id: number;
	created_at: string;
}

export interface RosterTemplateSettings {
	keep_assignee: boolean;
	auto_open_hours: number;
	reminder_hours: number[];
	allow_self_assign: boolean;
}

export interface RosterTemplateSlotCreate {
	role_id: number;
	label: string;
	sort_order?: number;
	min_persons?: number;
	max_persons?: number;
}

export interface RosterTemplateSlot {
	id: number;
	role_id: number;
	role_name?: string;
	label: string;
	sort_order: number;
	min_persons: number;
	max_persons: number;
	created_at: string;
	updated_at: string;
}

export interface RosterTemplate {
	id: number;
	name: string;
	description?: string;
	ministry_id?: number;
	mass_time_id?: number;
	event_id?: number;
	recurrence_rule: string;
	recurrence_end?: string;
	settings: RosterTemplateSettings;
	is_active: boolean;
	slots: RosterTemplateSlot[];
	slot_count: number;
	created_at: string;
	updated_at: string;
}

export interface RosterTemplateCreate {
	name: string;
	description?: string;
	ministry_id?: number;
	recurrence_rule?: string;
	settings?: RosterTemplateSettings;
	is_active?: boolean;
	slots?: RosterTemplateSlotCreate[];
}

export interface RosterAssignment {
	id: number;
	instance_id: number;
	slot_id: number;
	person_id: number;
	person_name?: string;
	slot_label?: string;
	role_name?: string;
	status: string;
	assigned_by?: number;
	assigned_at?: string;
	accepted_at?: string;
	declined_at?: string;
	completed_at?: string;
	cancelled_at?: string;
	notes?: string;
	created_at: string;
}

export interface RosterAssignmentCreate {
	instance_id: number;
	slot_id: number;
	person_id: number;
}

export interface RosterInstance {
	id: number;
	template_id: number;
	template_name?: string;
	date: string;
	status: string;
	generated_at?: string;
	published_at?: string;
	completed_at?: string;
	assignments: RosterAssignment[];
	created_at: string;
}

function qs(params: Record<string, string | number | boolean | undefined>): string {
	const pairs = Object.entries(params)
		.filter(([, v]) => v !== undefined)
		.map(([k, v]) => `${encodeURIComponent(k)}=${encodeURIComponent(String(v))}`);
	return pairs.length ? `?${pairs.join('&')}` : '';
}

export const rosterApi = {
	// Roles
	listRoles: () => api.get<RosterRole[]>('/roster/roles'),
	createRole: (data: RosterRoleCreate) => api.post<RosterRole>('/roster/roles', data),
	updateRole: (id: number, data: RosterRoleUpdate) => api.put<RosterRole>(`/roster/roles/${id}`, data),
	deleteRole: (id: number) => api.delete(`/roster/roles/${id}`),
	assignRole: (roleId: number, personId: number) =>
		api.post<PersonRosterRole>(`/roster/roles/${roleId}/assign`, { person_id: personId, role_id: roleId }),
	removeRole: (roleId: number, personId: number) =>
		api.delete(`/roster/roles/${roleId}/persons/${personId}`),

	// Templates
	listTemplates: (params?: { ministry_id?: number; is_active?: boolean }) =>
		api.get<RosterTemplate[]>(`/roster/templates${qs({ ministry_id: params?.ministry_id, is_active: params?.is_active })}`),
	getTemplate: (id: number) => api.get<RosterTemplate>(`/roster/templates/${id}`),
	createTemplate: (data: RosterTemplateCreate) => api.post<RosterTemplate>('/roster/templates', data),
	updateTemplate: (id: number, data: Partial<RosterTemplateCreate>) =>
		api.put<RosterTemplate>(`/roster/templates/${id}`, data),
	deleteTemplate: (id: number) => api.delete(`/roster/templates/${id}`),
	duplicateTemplate: (id: number) => api.post<RosterTemplate>(`/roster/templates/${id}/duplicate`),

	// Instances
	generateInstance: (templateId: number, date: string) =>
		api.post<RosterInstance>(`/roster/templates/${templateId}/generate${qs({ date })}`),
	listInstances: (params?: { date_from?: string; date_to?: string; ministry_id?: number }) =>
		api.get<RosterInstance[]>(`/roster/instances${qs(params || {})}`),
	getInstance: (id: number) => api.get<RosterInstance>(`/roster/instances/${id}`),
	publishInstance: (id: number) => api.put<RosterInstance>(`/roster/instances/${id}/publish`, {}),
	cancelInstance: (id: number) => api.put<RosterInstance>(`/roster/instances/${id}/cancel`, {}),
	completeInstance: (id: number) => api.put<RosterInstance>(`/roster/instances/${id}/complete`, {}),

	// Assignments (admin)
	assignPerson: (instanceId: number, data: RosterAssignmentCreate) =>
		api.post<RosterAssignment>(`/roster/instances/${instanceId}/assign`, data),
	removeAssignment: (id: number) => api.delete(`/roster/assignments/${id}`),

	// Parish aggregate
	getParishAggregate: (date: string) => api.get(`/roster/parish${qs({ date })}`),
};
