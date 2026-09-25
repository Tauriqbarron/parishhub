import { describe, it, expect } from 'vitest';
import { GET } from '../../routes/help/sign-in/+server';

describe('GET /help/sign-in', () => {
	it('serves the public sign-in help without a session', async () => {
		// eslint-disable-next-line @typescript-eslint/no-explicit-any
		const res = await GET({} as any);
		expect(res.status).toBe(200);
		expect(res.headers.get('Content-Type')).toContain('text/html');
		const body = await res.text();
		expect(body).toContain('Get a Google account');
		expect(body).toContain('Admin access: who can use ParishHub');
		expect(body).not.toContain('Record a sacrament');
	});
});
