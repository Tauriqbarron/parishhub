import { SvelteKitAuth } from '@auth/sveltekit';
import Google from '@auth/sveltekit/providers/google';
import { env } from '$env/dynamic/private';
import type { Handle } from '@sveltejs/kit';
import { sequence } from '@sveltejs/kit/hooks';

// Rewrite URL to HTTPS when behind a reverse proxy
const httpsRedirect: Handle = async ({ event, resolve }) => {
	if (env.AUTH_URL) {
		const url = new URL(event.request.url);
		url.protocol = 'https:';
		url.host = new URL(env.AUTH_URL).host;
		event.request = new Request(url.toString(), event.request);
	}
	return resolve(event);
};

const { handle: authHandle, signIn, signOut } = SvelteKitAuth({
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
			// Only allow the single authorized email
			const authorizedEmail = env.AUTHORIZED_EMAIL;
			if (!authorizedEmail) {
				console.error('AUTHORIZED_EMAIL environment variable is not set');
				return false;
			}
			return user.email === authorizedEmail;
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

export const handle = sequence(httpsRedirect, authHandle);
export { signIn, signOut };
