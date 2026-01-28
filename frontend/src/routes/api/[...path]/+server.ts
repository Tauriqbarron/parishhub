import type { RequestHandler } from './$types';
import { env } from '$env/dynamic/private';

const BACKEND_URL = env.BACKEND_URL || 'http://localhost:8000';

export const GET: RequestHandler = async ({ params, url, locals }) => {
	return proxyRequest('GET', params.path, url.search, null, locals);
};

export const POST: RequestHandler = async ({ params, url, request, locals }) => {
	const body = await request.text();
	return proxyRequest('POST', params.path, url.search, body, locals);
};

export const PUT: RequestHandler = async ({ params, url, request, locals }) => {
	const body = await request.text();
	return proxyRequest('PUT', params.path, url.search, body, locals);
};

export const DELETE: RequestHandler = async ({ params, url, locals }) => {
	return proxyRequest('DELETE', params.path, url.search, null, locals);
};

async function proxyRequest(
	method: string,
	path: string,
	search: string,
	body: string | null,
	locals: App.Locals
): Promise<Response> {
	// Get session from Auth.js
	let session;
	try {
		session = await locals.auth();
	} catch (error) {
		console.error('Auth error:', error);
		return new Response(JSON.stringify({ detail: 'Authentication error' }), {
			status: 500,
			headers: { 'Content-Type': 'application/json' }
		});
	}

	if (!session?.user?.email) {
		return new Response(JSON.stringify({ detail: 'Not authenticated' }), {
			status: 401,
			headers: { 'Content-Type': 'application/json' }
		});
	}

	// Verify authorized email
	if (session.user.email !== env.AUTHORIZED_EMAIL) {
		return new Response(JSON.stringify({ detail: 'Not authorized' }), {
			status: 403,
			headers: { 'Content-Type': 'application/json' }
		});
	}

	const headers: Record<string, string> = {
		'Content-Type': 'application/json',
		'X-User-Email': session.user.email,
		'X-User-Name': session.user.name || ''
	};

	const fetchOptions: RequestInit = {
		method,
		headers
	};

	if (body && (method === 'POST' || method === 'PUT')) {
		fetchOptions.body = body;
	}

	try {
		const response = await fetch(`${BACKEND_URL}/api/${path}${search}`, fetchOptions);

		if (response.status === 204) {
			return new Response(null, { status: 204 });
		}

		const data = await response.text();

		return new Response(data, {
			status: response.status,
			headers: {
				'Content-Type': response.headers.get('Content-Type') || 'application/json'
			}
		});
	} catch (error) {
		console.error('Proxy error:', error);
		return new Response(JSON.stringify({ detail: 'Backend unavailable' }), {
			status: 502,
			headers: { 'Content-Type': 'application/json' }
		});
	}
}
