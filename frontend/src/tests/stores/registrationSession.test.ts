import { describe, it, expect, beforeEach, vi, afterEach } from 'vitest';
import { get } from 'svelte/store';
import { registrationSessionStore } from '$lib/stores/registrationSession';
// Types imported via store — not directly referenced in test assertions

// Mock crypto.randomUUID
vi.stubGlobal('crypto', {
	randomUUID: () => 'test-uuid-' + Math.random().toString(36).substr(2, 9)
});

// Mock localStorage
const localStorageMock = (() => {
	let store: Record<string, string> = {};

	return {
		getItem: (key: string) => store[key] || null,
		setItem: (key: string, value: string) => {
			store[key] = value;
		},
		removeItem: (key: string) => {
			delete store[key];
		},
		clear: () => {
			store = {};
		}
	};
})();

Object.defineProperty(window, 'localStorage', {
	value: localStorageMock
});

describe('Registration Session Store', () => {
	beforeEach(() => {
		localStorageMock.clear();
		// Reset store to empty state (also clears storage)
		registrationSessionStore.clearSession();
	});

	afterEach(() => {
		// Ensure any debounce timers are cleared to avoid cross-test pollution
		// Access debounce via store internals not possible; call clearSession to cancel
		registrationSessionStore.clearSession();
	});

	describe('initSession', () => {
		it('should create a new session when no stored data exists', () => {
			const session = registrationSessionStore.initSession();

			expect(session.id).toBeTruthy();
			expect(session.registrationType).toBeNull();
			expect(session.household).toEqual({
				name: '',
				address: '',
				city: '',
				state: '',
				zipCode: '',
				phone: '',
				email: '',
				attendingSince: ''
			});
			expect(session.members).toEqual([]);
			expect(session.currentStep).toBe(0);
			expect(session.consent).toEqual({
				dataPrivacyConsent: false,
				photoMediaRelease: false,
				commEmail: false,
				commSms: false,
				commPhone: false,
				termsAcknowledged: false,
				consentedAt: ''
			});
		});

		it('should load existing session from storage', () => {
			const existingSession = {
				id: 'existing-id',
				lastUpdated: '2024-01-01T00:00:00Z',
				registrationType: 'household' as const,
				household: {
					name: 'Smith Family',
					address: '123 Main St',
					city: 'Anytown',
					state: 'ST',
					zipCode: '12345',
					phone: '555-5555',
					email: 'test@example.com',
					attendingSince: '2020-01-01'
				},
				members: [],
				currentStep: 2,
				consent: {
					dataPrivacyConsent: true,
					photoMediaRelease: false,
					commEmail: true,
					commSms: false,
					commPhone: false,
					termsAcknowledged: true,
					consentedAt: '2024-01-01T00:00:00Z'
				}
			};
			localStorageMock.setItem('parish_registration_session', JSON.stringify(existingSession));

			const loadedSession = registrationSessionStore.initSession();

			expect(loadedSession).toEqual(existingSession);
		});

		it('should reset step to 0 if stored session has step > 0 but no registrationType', () => {
			const invalidSession = {
				id: 'bad-id',
				lastUpdated: '2024-01-01T00:00:00Z',
				registrationType: null,
				household: {
					name: '',
					address: '',
					city: '',
					state: '',
					zipCode: '',
					phone: '',
					email: '',
					attendingSince: ''
				},
				members: [],
				currentStep: 3,
				consent: {
					dataPrivacyConsent: false,
					photoMediaRelease: false,
					commEmail: false,
					commSms: false,
					commPhone: false,
					termsAcknowledged: false,
					consentedAt: ''
				}
			};
			localStorageMock.setItem('parish_registration_session', JSON.stringify(invalidSession));

			const loadedSession = registrationSessionStore.initSession();

			expect(loadedSession.currentStep).toBe(0);
			expect(loadedSession.registrationType).toBeNull();
		});
	});

	describe('getSession', () => {
		it('should return the current session', () => {
			registrationSessionStore.initSession();
			const session = registrationSessionStore.getSession();
			expect(session).toBeDefined();
			expect(session.id).toBeTruthy();
		});
	});

	describe('saveSession', () => {
		it('should update lastUpdated and persist to storage', async () => {
			registrationSessionStore.initSession();
			// Advance any timers to ensure debounce fires
			vi.useFakeTimers();
			registrationSessionStore.saveSession();
			await vi.runAllTimersAsync();
			vi.useRealTimers();

			const stored = localStorageMock.getItem('parish_registration_session');
			expect(stored).not.toBeNull();
			const parsed = JSON.parse(stored!);
			expect(new Date(parsed.lastUpdated).getTime()).toBeGreaterThan(0);
		});
	});

	describe('clearSession', () => {
		it('should remove from storage and reset state', () => {
			registrationSessionStore.initSession();
			registrationSessionStore.setRegistrationType('household');
			registrationSessionStore.saveSession();
			expect(localStorageMock.getItem('parish_registration_session')).not.toBeNull();

			registrationSessionStore.clearSession();

			expect(localStorageMock.getItem('parish_registration_session')).toBeNull();
			const state = registrationSessionStore.getSession();
			expect(state.registrationType).toBeNull();
			expect(state.household).toEqual({
				name: '',
				address: '',
				city: '',
				state: '',
				zipCode: '',
				phone: '',
				email: '',
				attendingSince: ''
			});
		});

		it('should work even if localStorage is unavailable', () => {
			const originalLocalStorage = window.localStorage;
			Object.defineProperty(window, 'localStorage', {
				value: {
					getItem: () => null,
					setItem: () => {
						throw new Error('Storage unavailable');
					},
					removeItem: () => {}
				},
				writable: true
			});

			registrationSessionStore.initSession();
			registrationSessionStore.clearSession(); // should not throw

			Object.defineProperty(window, 'localStorage', {
				value: originalLocalStorage,
				writable: true
			});
		});
	});

	describe('updateHousehold', () => {
		it('should merge household updates', () => {
			registrationSessionStore.initSession();
			registrationSessionStore.updateHousehold({ name: 'Test Household', city: 'Test City' });

			const state = registrationSessionStore.getSession();
			expect(state.household.name).toBe('Test Household');
			expect(state.household.city).toBe('Test City');
			expect(state.household.address).toBe(''); // unchanged
		});
	});

	describe('addMember', () => {
		it('should add a new member with generated tempId', () => {
			registrationSessionStore.initSession();

			const memberData = {
				firstName: 'John',
				middleName: '',
				lastName: 'Doe',
				dateOfBirth: '1990-01-01',
				gender: 'male' as const,
				phone: '555-5555',
				email: 'john@example.com',
				isHeadOfHousehold: true,
				livesInHousehold: true,
				familyRole: 'parent' as const,
				sacraments: [],
				relationships: []
			};

			registrationSessionStore.addMember(memberData);

			const state = registrationSessionStore.getSession();
			expect(state.members).toHaveLength(1);
			const added = state.members[0];
			expect(added.firstName).toBe('John');
			expect(added.lastName).toBe('Doe');
			expect(added.tempId).toBeTruthy();
			expect(added.tempId).toMatch(/^test-uuid-/);
		});
	});

	describe('updateMember', () => {
		it('should update an existing member by tempId', () => {
			registrationSessionStore.initSession();
			registrationSessionStore.addMember({
				firstName: 'John',
				middleName: '',
				lastName: 'Doe',
				dateOfBirth: '1990-01-01',
				gender: 'male',
				phone: '555-5555',
				email: 'john@example.com',
				isHeadOfHousehold: true,
				livesInHousehold: true,
				familyRole: 'parent',
				sacraments: [],
				relationships: []
			});

			const tempId = get(registrationSessionStore).members[0].tempId;
			registrationSessionStore.updateMember(tempId, { firstName: 'Johnny' });

			const state = registrationSessionStore.getSession();
			expect(state.members[0].firstName).toBe('Johnny');
		});

		it('should not affect other members', () => {
			registrationSessionStore.initSession();
			registrationSessionStore.addMember({
				firstName: 'John',
				middleName: '',
				lastName: 'Doe',
				dateOfBirth: '1990-01-01',
				gender: 'male',
				phone: '555-5555',
				email: 'john@example.com',
				isHeadOfHousehold: true,
				livesInHousehold: true,
				familyRole: 'parent',
				sacraments: [],
				relationships: []
			});
			const johnTempId = get(registrationSessionStore).members[0].tempId;

			registrationSessionStore.addMember({
				firstName: 'Jane',
				middleName: '',
				lastName: 'Doe',
				dateOfBirth: '1992-01-01',
				gender: 'female',
				phone: '555-5556',
				email: 'jane@example.com',
				isHeadOfHousehold: false,
				livesInHousehold: true,
				familyRole: 'child',
				sacraments: [],
				relationships: []
			});

			registrationSessionStore.updateMember(johnTempId, { lastName: 'Smith' });

			const state = registrationSessionStore.getSession();
			expect(state.members[0].lastName).toBe('Smith'); // John updated
			expect(state.members[1].lastName).toBe('Doe'); // Jane unchanged
		});
	});

	describe('removeMember', () => {
		it('should remove member by tempId', () => {
			registrationSessionStore.initSession();
			registrationSessionStore.addMember({
				firstName: 'John',
				middleName: '',
				lastName: 'Doe',
				dateOfBirth: '1990-01-01',
				gender: 'male',
				phone: '555-5555',
				email: 'john@example.com',
				isHeadOfHousehold: true,
				livesInHousehold: true,
				familyRole: 'parent',
				sacraments: [],
				relationships: []
			});
			const tempId = get(registrationSessionStore).members[0].tempId;

			registrationSessionStore.removeMember(tempId);

			const state = registrationSessionStore.getSession();
			expect(state.members).toHaveLength(0);
		});

		it('should also remove relationships pointing to removed member', () => {
			registrationSessionStore.initSession();
			registrationSessionStore.addMember({
				firstName: 'John',
				middleName: '',
				lastName: 'Doe',
				dateOfBirth: '1990-01-01',
				gender: 'male',
				phone: '555-5555',
				email: 'john@example.com',
				isHeadOfHousehold: true,
				livesInHousehold: true,
				familyRole: 'parent',
				sacraments: [],
				relationships: []
			});
			const johnTempId = get(registrationSessionStore).members[0].tempId;

			registrationSessionStore.addMember({
				firstName: 'Jane',
				middleName: '',
				lastName: 'Doe',
				dateOfBirth: '1992-01-01',
				gender: 'female',
				phone: '555-5556',
				email: 'jane@example.com',
				isHeadOfHousehold: false,
				livesInHousehold: true,
				familyRole: 'child',
				sacraments: [],
				relationships: [{ targetTempId: johnTempId, relationshipType: 'child' }]
			});

			registrationSessionStore.removeMember(johnTempId);

			const state = registrationSessionStore.getSession();
			expect(state.members).toHaveLength(1); // Jane remains
			expect(state.members[0].relationships).toEqual([]); // Jane's relationship cleared
		});
	});

	describe('setCurrentStep', () => {
		it('should update current step', () => {
			registrationSessionStore.initSession();
			registrationSessionStore.setCurrentStep(3);
			expect(get(registrationSessionStore).currentStep).toBe(3);
		});
	});

	describe('setRegistrationType', () => {
		it('should set registration type', () => {
			registrationSessionStore.initSession();
			registrationSessionStore.setRegistrationType('household');
			expect(get(registrationSessionStore).registrationType).toBe('household');
		});
	});

	describe('updateConsent', () => {
		it('should merge consent updates', () => {
			registrationSessionStore.initSession();
			registrationSessionStore.updateConsent({ dataPrivacyConsent: true, termsAcknowledged: true });

			const consent = get(registrationSessionStore).consent;
			expect(consent.dataPrivacyConsent).toBe(true);
			expect(consent.termsAcknowledged).toBe(true);
			expect(consent.commEmail).toBe(false);
		});
	});

	describe('debouncing', () => {
		it('should debounce save operations', async () => {
			vi.useFakeTimers();

			registrationSessionStore.initSession();
			registrationSessionStore.updateHousehold({ name: 'First' });
			registrationSessionStore.updateHousehold({ name: 'Second' });
			registrationSessionStore.updateHousehold({ name: 'Third' });

			// No save yet
			// Run all timers
			await vi.runAllTimersAsync();

			const stored = localStorageMock.getItem('parish_registration_session');
			expect(stored).not.toBeNull();
			const parsed = JSON.parse(stored!);
			expect(parsed.household.name).toBe('Third');

			vi.useRealTimers();
		}, 10000);
	});

	describe('session persistence across init', () => {
		it('should persist and restore full session', async () => {
			// Build a session via operations
			registrationSessionStore.initSession();
			registrationSessionStore.setRegistrationType('household');
			registrationSessionStore.updateHousehold({ name: 'Test House', city: 'Testville' });
			registrationSessionStore.addMember({
				firstName: 'Alice',
				middleName: '',
				lastName: 'Smith',
				dateOfBirth: '1985-01-01',
				gender: 'female',
				phone: '555-1234',
				email: 'alice@example.com',
				isHeadOfHousehold: true,
				livesInHousehold: true,
				familyRole: 'parent',
				sacraments: [],
				relationships: []
			});
			registrationSessionStore.updateConsent({ dataPrivacyConsent: true });
			registrationSessionStore.setCurrentStep(1);
			// Force debounced saves to complete
			vi.useFakeTimers();
			registrationSessionStore.saveSession();
			await vi.runAllTimersAsync();
			vi.useRealTimers();

			// Verify storage content
			const stored = JSON.parse(localStorageMock.getItem('parish_registration_session')!);
			expect(stored.registrationType).toBe('household');
			expect(stored.household.name).toBe('Test House');
			expect(stored.members).toHaveLength(1);
			expect(stored.consent.dataPrivacyConsent).toBe(true);
			expect(stored.currentStep).toBe(1);
		});
	});
});
