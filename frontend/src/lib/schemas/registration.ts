import { z } from 'zod';

// ---- Enum schemas ----

export const genderSchema = z.enum(['male', 'female', 'other', '']);

export const sacramentTypeSchema = z.enum([
	'baptism',
	'first_communion',
	'confirmation',
	'marriage',
	'holy_orders',
	'anointing'
]);

export const relationshipTypeSchema = z.enum(['parent', 'child', 'spouse', 'sibling']);

// ---- Member schema ----

export const registrationMemberSchema = z.object({
	tempId: z.string().min(1),
	firstName: z.string().min(1, 'First name is required').max(100),
	middleName: z.string().max(100).optional().default(''),
	lastName: z.string().min(1, 'Last name is required').max(100),
	dateOfBirth: z.string().optional().default(''),
	gender: genderSchema.optional().default(''),
	phone: z.string().max(20).optional().default(''),
	email: z.string().email('Invalid email').or(z.literal('')).optional().default(''),
	isHeadOfHousehold: z.boolean().default(false),
	livesInHousehold: z.boolean().default(true),
	sacraments: z
		.array(
			z.object({
				type: sacramentTypeSchema,
				date: z.string().optional().default(''),
				additionalData: z.record(z.unknown()).default({})
			})
		)
		.default([]),
	relationships: z
		.array(
			z.object({
				targetTempId: z.string().min(1),
				relationshipType: relationshipTypeSchema
			})
		)
		.default([])
});

export type RegistrationMemberSchema = z.infer<typeof registrationMemberSchema>;

// ---- Household schema ----

export const registrationHouseholdSchema = z.object({
	name: z.string().min(1, 'Household name is required').max(200),
	address: z.string().max(255).optional().default(''),
	city: z.string().max(100).optional().default(''),
	state: z.string().max(100).optional().default(''),
	zipCode: z.string().max(20).optional().default(''),
	phone: z.string().max(20).optional().default(''),
	email: z.string().email('Invalid email').or(z.literal('')).optional().default(''),
	attendingSince: z.string().optional().default('')
});

export type RegistrationHouseholdSchema = z.infer<typeof registrationHouseholdSchema>;

// ---- Individual schema ----

export const individualRegistrationSchema = z.object({
	firstName: z.string().min(1, 'First name is required').max(100),
	middleName: z.string().max(100).optional().default(''),
	lastName: z.string().min(1, 'Last name is required').max(100),
	dateOfBirth: z.string().optional().default(''),
	gender: genderSchema.optional().default(''),
	phone: z.string().max(20).optional().default(''),
	email: z.string().email('Invalid email').or(z.literal('')).optional().default('')
});

export type IndividualRegistrationSchema = z.infer<typeof individualRegistrationSchema>;

// ---- Consent schema ----

export const registrationConsentSchema = z.object({
	dataPrivacyConsent: z.boolean().refine((v) => v === true, {
		message: 'You must consent to data privacy'
	}),
	photoMediaRelease: z.boolean().default(false),
	commEmail: z.boolean().default(false),
	commSms: z.boolean().default(false),
	commPhone: z.boolean().default(false),
	termsAcknowledged: z.boolean().refine((v) => v === true, {
		message: 'You must acknowledge the terms'
	})
});

export type RegistrationConsentSchema = z.infer<typeof registrationConsentSchema>;

// ---- Full household registration ----

export const householdRegistrationSchema = z.object({
	household: registrationHouseholdSchema,
	members: z.array(registrationMemberSchema).min(1, 'At least one member is required'),
	consent: registrationConsentSchema.optional()
});

export type HouseholdRegistrationSchema = z.infer<typeof householdRegistrationSchema>;

// ---- API payload types (match backend camelCase aliases) ----

export interface RegistrationApiMember {
	tempId: string;
	firstName: string;
	middleName: string | null;
	lastName: string;
	dateOfBirth: string | null;
	gender: string | null;
	phone: string | null;
	email: string | null;
	isHeadOfHousehold: boolean;
	livesInHousehold: boolean;
}

export interface RegistrationApiRelationship {
	fromTempId: string;
	toTempId: string;
	relationshipType: string;
}

export interface RegistrationApiSacrament {
	memberTempId: string;
	sacramentType: string;
	date: string | null;
	church: string | null;
	minister: string | null;
	godfather: string | null;
	godmother: string | null;
	sponsor: string | null;
	parish: string | null;
	witness1: string | null;
	witness2: string | null;
	officiant: string | null;
	notes: string | null;
	spouseId: number | null;
	additionalData: Record<string, unknown>;
}

export interface RegistrationApiConsent {
	dataPrivacyConsent: boolean;
	photoMediaRelease: boolean;
	commEmail: boolean;
	commSms: boolean;
	commPhone: boolean;
	termsAcknowledged: boolean;
}

export interface RegistrationApiPayload {
	householdName: string;
	streetAddress: string | null;
	city: string | null;
	state: string | null;
	zipCode: string | null;
	phone: string | null;
	email: string | null;
	attendingSince: string | null;
	members: RegistrationApiMember[];
	relationships: RegistrationApiRelationship[];
	sacraments: RegistrationApiSacrament[];
	consent?: RegistrationApiConsent;
}

export interface IndividualRegistrationApiPayload {
	firstName: string;
	middleName: string | null;
	lastName: string;
	dateOfBirth: string | null;
	gender: string | null;
	phone: string | null;
	email: string | null;
	sacraments: RegistrationApiSacrament[];
	consent?: RegistrationApiConsent;
}

// ---- Response types ----

export interface RegistrationSubmitResponse {
	success: boolean;
	householdId: number;
	memberIds: number[];
	message: string;
}

export interface IndividualRegistrationSubmitResponse {
	personId: number;
	message: string;
}
