import { error, redirect } from '@sveltejs/kit';
import type { RequestHandler } from './$types';
import { isAuthorizedEmail } from '$lib/server/authorized';
import { renderGuide } from '$lib/help/render';

const html = renderGuide();

// hooks.server.ts already requires a session. Checking the allowlist too means an admin removed
// from AUTHORIZED_EMAILS loses the guide at once, not when their session expires.
export const GET: RequestHandler = async ({ locals }) => {
	const session = await locals.auth();
	if (!session?.user?.email) redirect(303, '/login');
	if (!isAuthorizedEmail(session.user.email)) error(403, 'Not authorized');

	return new Response(html, {
		headers: {
			'Content-Type': 'text/html; charset=utf-8',
			'Cache-Control': 'private, no-cache'
		}
	});
};
