import { describe, it, expect, vi } from 'vitest';

vi.mock('$env/dynamic/private', () => ({
	env: { AUTHORIZED_EMAILS: 'office@example.org, priest@example.org' }
}));

import { GET } from '../../routes/help/+server';

type Session = { user?: { email?: string } } | null;
const call = (session: Session) =>
	// eslint-disable-next-line @typescript-eslint/no-explicit-any
	GET({ locals: { auth: async () => session } } as any);

describe('GET /help', () => {
	it('serves the guide to an approved admin', async () => {
		const res = await call({ user: { email: 'priest@example.org' } });
		expect(res.status).toBe(200);
		expect(res.headers.get('Content-Type')).toContain('text/html');
		expect(await res.text()).toContain('Part A: For the parish office');
	});

	it('sends signed-out visitors to the login page', async () => {
		await expect(call(null)).rejects.toMatchObject({ status: 303, location: '/login' });
	});

	it('refuses a signed-in email that is no longer on the allowlist', async () => {
		await expect(call({ user: { email: 'former@example.org' } })).rejects.toMatchObject({
			status: 403
		});
	});
});
