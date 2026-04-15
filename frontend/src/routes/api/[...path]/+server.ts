import type { RequestHandler } from './$types';
import { env } from '$env/dynamic/private';
import { createHmac } from 'crypto';

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

// Public API paths that don't require authentication
// 'auth' must be public so Auth.js's own endpoints work through the proxy
const PUBLIC_API_PATHS = ['register', 'auth'];

async function proxyRequest(
	method: string,
	path: string,
	search: string,
	body: string | null,
	locals: App.Locals
): Promise<Response> {
	const isPublic = PUBLIC_API_PATHS.some((p) => path === p || path.startsWith(`${p}/`));

	const headers: Record<string, string> = {
		'Content-Type': 'application/json'
	};

	if (!isPublic) {
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
		const authorizedEmails = (env.AUTHORIZED_EMAILS || '')
			.split(',')
			.map((e) => e.trim())
			.filter(Boolean);
		if (!authorizedEmails.includes(session.user.email)) {
			return new Response(JSON.stringify({ detail: 'Not authorized' }), {
				status: 403,
				headers: { 'Content-Type': 'application/json' }
			});
		}

		// Generate HMAC signature
		const timestamp = Math.floor(Date.now() / 1000).toString();
		const authSecret = env.AUTH_SECRET;
		if (!authSecret) {
			return new Response(JSON.stringify({ detail: 'Server configuration error' }), {
				status: 500,
				headers: { 'Content-Type': 'application/json' }
			});
		}
		const signature = createHmac('sha256', authSecret)
			.update(`${timestamp}.${session.user.email}`)
			.digest('hex');

		headers['X-User-Email'] = session.user.email;
		headers['X-User-Name'] = session.user.name || '';
		headers['X-Auth-Timestamp'] = timestamp;
		headers['X-Auth-Signature'] = signature;
	}

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
