import { env } from '$env/dynamic/private';

/** Emails on the AUTHORIZED_EMAILS allowlist, the same list Auth.js checks at sign-in. */
export function authorizedEmails(): string[] {
	return (env.AUTHORIZED_EMAILS || '')
		.split(',')
		.map((e) => e.trim())
		.filter(Boolean);
}

export function isAuthorizedEmail(email: string | null | undefined): boolean {
	return !!email && authorizedEmails().includes(email);
}
