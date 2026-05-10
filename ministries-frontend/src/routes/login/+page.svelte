<script lang="ts">
	import { goto } from '$app/navigation';
	import { memberApi, setToken } from '$lib/api';
	import { onMount } from 'svelte';

	let error = $state('');
	let loading = $state(false);

	const GOOGLE_CLIENT_ID = '532875659774-2b57bv8ld15ki8jfd3ap7b5t1brsd8vm.apps.googleusercontent.com';

	onMount(() => {
		// Load Google Identity Services script
		if (!document.getElementById('google-gsi')) {
			const script = document.createElement('script');
			script.id = 'google-gsi';
			script.src = 'https://accounts.google.com/gsi/client';
			script.async = true;
			script.defer = true;
			script.onload = initGoogle;
			document.head.appendChild(script);
		} else {
			initGoogle();
		}
	});

	function initGoogle() {
		if (!(window as any).google?.accounts?.id) return;

		(window as any).google.accounts.id.initialize({
			client_id: GOOGLE_CLIENT_ID,
			callback: handleCredentialResponse,
			ux_mode: 'popup'
		});

		const btn = document.getElementById('google-signin-btn');
		if (btn) {
			(window as any).google.accounts.id.renderButton(btn, {
				theme: 'outline',
				size: 'large',
				text: 'signin_with',
				shape: 'rectangular',
				width: 300
			});
		}
	}

	async function handleCredentialResponse(response: any) {
		loading = true;
		error = '';
		try {
			const result = await memberApi.login(response.credential);
			setToken(result.token);
			goto('/dashboard');
		} catch (err) {
			error = err instanceof Error ? err.message : 'Login failed';
		} finally {
			loading = false;
		}
	}
</script>

<div class="min-h-screen flex items-center justify-center px-4 bg-brand-bg-subtle">
	<div class="w-full max-w-sm">
		<div class="bg-white rounded-lg shadow-sm border border-brand-border p-8">
			<div class="text-center mb-8">
				<img src="/logo.png" alt="ParishHub" class="w-14 h-14 mx-auto mb-3" />
				<h1 class="text-2xl font-bold text-brand-primary tracking-tight">ParishHub</h1>
				<p class="text-xs text-brand-text-muted font-medium tracking-tight mt-0.5">Ministries</p>
				<p class="mt-1 text-sm text-brand-text-secondary">Sign in to manage your groups</p>
			</div>

			{#if error}
				<div class="mb-4 p-3 rounded bg-red-50 text-red-700 text-sm">
					{error}
				</div>
			{/if}

			<div class="flex justify-center">
				<div id="google-signin-btn"></div>
			</div>

			{#if loading}
				<p class="mt-4 text-center text-sm text-brand-text-muted">Signing in...</p>
			{/if}

			<p class="mt-6 text-center text-xs text-brand-text-muted">
				Only registered ministry members and leaders can sign in.
				<br />
				Contact your group leader for access.
			</p>
		</div>
	</div>
</div>
