import type { RequestHandler } from './$types';
import signIn from '$lib/help/sign-in.generated.html?raw';

// Public: the only part of the guide people can read before they have access.
// Generated from guide.html by scripts/export-guides.mjs.
export const GET: RequestHandler = () =>
	new Response(signIn, {
		headers: {
			'Content-Type': 'text/html; charset=utf-8',
			'Cache-Control': 'public, max-age=300'
		}
	});
