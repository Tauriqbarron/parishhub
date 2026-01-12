import { SvelteKitAuth } from '@auth/sveltekit';
import Google from '@auth/sveltekit/providers/google';
import { env } from '$env/dynamic/private';

export const { handle, signIn, signOut } = SvelteKitAuth({
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
