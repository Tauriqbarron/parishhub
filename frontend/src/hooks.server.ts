import { SvelteKitAuth } from '@auth/sveltekit';
import Google from '@auth/sveltekit/providers/google';
import { env } from '$env/dynamic/private';
import type { Handle } from '@sveltejs/kit';
import { sequence } from '@sveltejs/kit/hooks';

const {
	handle: authHandle,
	signIn,
	signOut
} = SvelteKitAuth({
	providers: [
		Google({
			clientId: env.GOOGLE_CLIENT_ID,
			clientSecret: env.GOOGLE_CLIENT_SECRET
		})
	],
	secret: env.AUTH_SECRET,
	trustHost: true,
	callbacks: {
		signIn({ user }) {
			const authorizedEmails = (env.AUTHORIZED_EMAILS || '')
				.split(',')
				.map((e) => e.trim())
				.filter(Boolean);
			if (authorizedEmails.length === 0) {
				console.error('AUTHORIZED_EMAILS environment variable is not set');
				return false;
			}
			return authorizedEmails.includes(user.email ?? '');
		},
		session({ session, token }) {
			// Pass user info to the session
			if (session.user && token.sub) {
				session.user.id = token.sub;
			}
			return session;
		},
		jwt({ token, user }) {
			if (user) {
				token.id = user.id;
			}
			return token;
		}
	},
	pages: {
		signIn: '/login',
		error: '/login'
	}
});

// Rewrite URL to HTTPS when behind a reverse proxy (skip for localhost)
const httpsRedirect: Handle = async ({ event, resolve }) => {
	if (env.AUTH_URL) {
		const authUrl = new URL(env.AUTH_URL);
		// Only rewrite if AUTH_URL is HTTPS (i.e., behind a real proxy)
		if (authUrl.protocol === 'https:') {
			const url = new URL(event.request.url);
			url.protocol = 'https:';
			url.host = authUrl.host;
			event.request = new Request(url.toString(), event.request);
		}
	}
	return resolve(event);
};

// Protect non-public routes by requiring authentication
const protectRoutes: Handle = async ({ event, resolve }) => {
	const publicPaths = ['/register', '/login', '/auth', '/api/auth', '/api/register', '/api/'];
	if (publicPaths.some((path) => event.url.pathname.startsWith(path))) {
		return resolve(event);
	}
	const session = await event.locals.auth();
	if (!session) {
		return new Response(null, {
			status: 303,
			headers: { location: '/login' }
		});
	}
	return resolve(event);
};

export const handle = sequence(httpsRedirect, authHandle, protectRoutes);
export { signIn, signOut };
