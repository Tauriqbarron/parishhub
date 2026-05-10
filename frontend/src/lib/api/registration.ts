import { api } from '$lib/api';
import type {
	RegistrationApiPayload,
	IndividualRegistrationApiPayload,
	RegistrationSubmitResponse,
	IndividualRegistrationSubmitResponse
} from '$lib/schemas/registration';

// Re-export for convenience
export type {
	RegistrationApiPayload,
	IndividualRegistrationApiPayload,
	RegistrationSubmitResponse,
	IndividualRegistrationSubmitResponse
} from '$lib/schemas/registration';

// ---- Registration URL types ----

export interface RegistrationURLConfig {
	baseUrl: string;
}

export interface RegistrationURLResponse {
	baseUrl: string;
	registrationUrl: string;
}

// ---- API functions ----

export const registrationApi = {
	/**
	 * Submit a household registration (public endpoint).
	 */
	submit: (payload: RegistrationApiPayload) =>
		api.post<RegistrationSubmitResponse>('/register', payload),

	/**
	 * Submit an individual registration without household (public endpoint).
	 */
	submitIndividual: (payload: IndividualRegistrationApiPayload) =>
		api.post<IndividualRegistrationSubmitResponse>('/register/individual', payload),

	/**
	 * Get the registration URL configuration (authenticated).
	 */
	getUrl: () => api.get<RegistrationURLResponse>('/v1/registration/url'),

	/**
	 * Update the registration URL configuration (authenticated).
	 */
	updateUrl: (config: RegistrationURLConfig) =>
		api.put<RegistrationURLResponse>('/v1/registration/url', config)
};
