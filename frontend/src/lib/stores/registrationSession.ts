import { writable, get } from 'svelte/store';

const STORAGE_KEY = 'parish_registration_session';
const DEBOUNCE_MS = 500;

export interface RegistrationMemberSacrament {
	type: string;
	date: string;
	additionalData: Record<string, unknown>;
}

export interface RegistrationMemberRelationship {
	targetTempId: string;
	relationshipType: string;
}

export interface RegistrationMember {
	tempId: string;
	firstName: string;
	middleName: string;
	lastName: string;
	dateOfBirth: string;
	gender: 'male' | 'female' | 'other' | '';
	phone: string;
	email: string;
	isHeadOfHousehold: boolean;
	sacraments: RegistrationMemberSacrament[];
	relationships: RegistrationMemberRelationship[];
}

export interface RegistrationHousehold {
	name: string;
	address: string;
	city: string;
	state: string;
	zipCode: string;
	phone: string;
	email: string;
	attendingSince: string;
}

export interface RegistrationConsent {
	dataPrivacyConsent: boolean;
	photoMediaRelease: boolean;
	commEmail: boolean;
	commSms: boolean;
	commPhone: boolean;
	termsAcknowledged: boolean;
	consentedAt: string;
}

export interface RegistrationSession {
	id: string;
	lastUpdated: string;
	household: RegistrationHousehold;
	members: RegistrationMember[];
	currentStep: number;
	consent: RegistrationConsent;
}

const emptyHousehold: RegistrationHousehold = {
	name: '',
	address: '',
	city: '',
	state: '',
	zipCode: '',
	phone: '',
	email: '',
	attendingSince: ''
};

const emptyConsent: RegistrationConsent = {
	dataPrivacyConsent: false,
	photoMediaRelease: false,
	commEmail: false,
	commSms: false,
	commPhone: false,
	termsAcknowledged: false,
	consentedAt: ''
};

const emptySession: RegistrationSession = {
	id: '',
	lastUpdated: '',
	household: { ...emptyHousehold },
	members: [],
	currentStep: 0,
	consent: { ...emptyConsent }
};

function generateUUID(): string {
	return crypto.randomUUID();
}

function createRegistrationSessionStore() {
	const { subscribe, set, update } = writable<RegistrationSession>({ ...emptySession });

	let debounceTimer: ReturnType<typeof setTimeout> | null = null;

	function saveToStorage(session: RegistrationSession): void {
		if (typeof window === 'undefined') return;
		try {
			localStorage.setItem(STORAGE_KEY, JSON.stringify(session));
		} catch {
			// Storage full or unavailable
		}
	}

	function loadFromStorage(): RegistrationSession | null {
		if (typeof window === 'undefined') return null;
		try {
			const stored = localStorage.getItem(STORAGE_KEY);
			if (stored) {
				return JSON.parse(stored) as RegistrationSession;
			}
		} catch {
			// Invalid JSON or storage unavailable
		}
		return null;
	}

	function debouncedSave(session: RegistrationSession): void {
		if (debounceTimer) {
			clearTimeout(debounceTimer);
		}
		debounceTimer = setTimeout(() => {
			saveToStorage(session);
			debounceTimer = null;
		}, DEBOUNCE_MS);
	}

	return {
		subscribe,

		initSession(): RegistrationSession {
			const stored = loadFromStorage();
			if (stored && stored.id) {
				set(stored);
				return stored;
			}
			const newSession: RegistrationSession = {
				id: generateUUID(),
				lastUpdated: new Date().toISOString(),
				household: { ...emptyHousehold },
				members: [],
				currentStep: 0,
				consent: { ...emptyConsent }
			};
			set(newSession);
			saveToStorage(newSession);
			return newSession;
		},

		saveSession(): void {
			const currentSession = get({ subscribe });
			const updatedSession = {
				...currentSession,
				lastUpdated: new Date().toISOString()
			};
			set(updatedSession);
			debouncedSave(updatedSession);
		},

		clearSession(): void {
			if (typeof window !== 'undefined') {
				localStorage.removeItem(STORAGE_KEY);
			}
			set({ ...emptySession });
		},

		getSession(): RegistrationSession {
			return get({ subscribe });
		},

		updateHousehold(household: Partial<RegistrationHousehold>): void {
			update((session) => {
				const updated = {
					...session,
					lastUpdated: new Date().toISOString(),
					household: { ...session.household, ...household }
				};
				debouncedSave(updated);
				return updated;
			});
		},

		addMember(member: Omit<RegistrationMember, 'tempId'>): void {
			update((session) => {
				const newMember: RegistrationMember = {
					...member,
					tempId: generateUUID()
				};
				const updated = {
					...session,
					lastUpdated: new Date().toISOString(),
					members: [...session.members, newMember]
				};
				debouncedSave(updated);
				return updated;
			});
		},

		updateMember(tempId: string, memberData: Partial<RegistrationMember>): void {
			update((session) => {
				const updated = {
					...session,
					lastUpdated: new Date().toISOString(),
					members: session.members.map((m) => (m.tempId === tempId ? { ...m, ...memberData } : m))
				};
				debouncedSave(updated);
				return updated;
			});
		},

		removeMember(tempId: string): void {
			update((session) => {
				const updated = {
					...session,
					lastUpdated: new Date().toISOString(),
					members: session.members.filter((m) => m.tempId !== tempId)
				};
				debouncedSave(updated);
				return updated;
			});
		},

		setCurrentStep(step: number): void {
			update((session) => {
				const updated = {
					...session,
					lastUpdated: new Date().toISOString(),
					currentStep: step
				};
				debouncedSave(updated);
				return updated;
			});
		},

		updateConsent(consent: Partial<RegistrationConsent>): void {
			update((session) => {
				const updated = {
					...session,
					lastUpdated: new Date().toISOString(),
					consent: { ...session.consent, ...consent }
				};
				debouncedSave(updated);
				return updated;
			});
		}
	};
}

export const registrationSessionStore = createRegistrationSessionStore();
