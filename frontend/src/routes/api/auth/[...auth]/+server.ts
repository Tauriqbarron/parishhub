import { SvelteKitAuth } from '@auth/sveltekit';
import Google from '@auth/sveltekit/providers/google';
import { env } from '$env/dynamic/private';

// Auth.js route handler — sits at src/routes/api/auth/[...auth]/+server.ts
// This MUST exist so SvelteKit's route matching gives /api/auth/* to Auth.js
// instead of the catch-all proxy at /api/[...path]
const { handle: authHandle } = SvelteKitAuth({
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
			// Hardcoded allowlist bridge while ProDesk SSH is down
			// TODO: remove once SSH is restored
			const hardcoded = [
				'sunnytiger32@gmail.com',
				'yyun006@gmail.com',
				'chaplain@fssp.nz',
				'office@fssp.nz',
				'fr.nguyen@fssp.nz'
			];
			const allAllowed = [...new Set([...hardcoded, ...authorizedEmails])];
			if (allAllowed.length === 0) {
				console.error('AUTHORIZED_EMAILS environment variable is not set');
				return false;
			}
			return allAllowed.includes(user.email ?? '');
		},
		session({ session, token }) {
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

export const GET: import('./$types').RequestHandler = async (event) => {
	return authHandle({ event, resolve: () => new Response(null) });
};

export const POST: import('./$types').RequestHandler = async (event) => {
	return authHandle({ event, resolve: () => new Response(null) });
};
