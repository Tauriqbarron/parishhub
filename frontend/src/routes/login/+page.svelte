<script lang="ts">
	import { signIn } from '@auth/sveltekit/client';
	import { page } from '$app/stores';

	// Get error from URL if present
	let errorMessage = $derived(getErrorMessage($page.url.searchParams.get('error')));

	function getErrorMessage(error: string | null): string | null {
		if (!error) return null;
		switch (error) {
			case 'AccessDenied':
				return 'Access denied. Your email is not authorized to use this application.';
			case 'Configuration':
				return 'Server configuration error. Please contact the administrator.';
			case 'Verification':
				return 'Verification failed. Please try again.';
			default:
				return 'An error occurred during sign in. Please try again.';
		}
	}
</script>

<div class="min-h-screen bg-brand-bg-subtle flex items-center justify-center p-4">
	<div
		class="max-w-md w-full bg-white rounded-xl shadow-lg overflow-hidden border border-brand-border"
	>
		<!-- Brand Header Section -->
		<div class="bg-brand-primary px-8 py-10 text-center">
			<h1 class="text-3xl font-bold text-white mb-2 tracking-tight">ParishHub</h1>
			<p class="text-white/60 text-sm">Parish Management System</p>
		</div>

		<!-- Sign-in Section -->
		<div class="px-8 py-8">
			<p class="text-brand-text-secondary text-center text-sm mb-6">
				Sign in with your authorized account
			</p>

			{#if errorMessage}
				<div class="mb-6 p-4 bg-brand-error/10 border border-brand-error/20 rounded-lg">
					<p class="text-brand-error text-sm">{errorMessage}</p>
				</div>
			{/if}

			<button
				onclick={() => signIn('google')}
				class="w-full flex items-center justify-center gap-3 px-4 py-3 border border-brand-border rounded-lg shadow-sm bg-white hover:bg-brand-bg-subtle transition-colors focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-brand-accent cursor-pointer"
			>
				<svg class="w-5 h-5" viewBox="0 0 24 24" xmlns="http://www.w3.org/2000/svg">
					<path
						d="M22.56 12.25c0-.78-.07-1.53-.2-2.25H12v4.26h5.92c-.26 1.37-1.04 2.53-2.21 3.31v2.77h3.57c2.08-1.92 3.28-4.74 3.28-8.09z"
						fill="#4285F4"
					/>
					<path
						d="M12 23c2.97 0 5.46-.98 7.28-2.66l-3.57-2.77c-.98.66-2.23 1.06-3.71 1.06-2.86 0-5.29-1.93-6.16-4.53H2.18v2.84C3.99 20.53 7.7 23 12 23z"
						fill="#34A853"
					/>
					<path
						d="M5.84 14.09c-.22-.66-.35-1.36-.35-2.09s.13-1.43.35-2.09V7.07H2.18C1.43 8.55 1 10.22 1 12s.43 3.45 1.18 4.93l2.85-2.22.81-.62z"
						fill="#FBBC05"
					/>
					<path
						d="M12 5.38c1.62 0 3.06.56 4.21 1.64l3.15-3.15C17.45 2.09 14.97 1 12 1 7.7 1 3.99 3.47 2.18 7.07l3.66 2.84c.87-2.6 3.3-4.53 6.16-4.53z"
						fill="#EA4335"
					/>
				</svg>
				<span class="text-gray-700 font-medium">Sign in with Google</span>
			</button>

			<p class="mt-6 text-center text-xs text-brand-text-muted">
				Only authorized email addresses can access this application.
			</p>
		</div>
	</div>
</div>
