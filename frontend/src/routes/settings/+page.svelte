<script lang="ts">
	import { onMount } from 'svelte';
	import { api, registrationApi } from '$lib/api';
	import { addToast } from '$lib/stores/toast';

	let baseUrl = $state('');
	let registrationUrl = $state('');
	let loading = $state(true);
	let saving = $state(false);
	let urlNotConfigured = $state(false);

	const QR_API_BASE = 'https://api.qrserver.com/v1/create-qr-code/?size=200x200&data=';

	onMount(async () => {
		await loadRegistrationUrl();
	});

	async function loadRegistrationUrl() {
		loading = true;
		urlNotConfigured = false;
		try {
			const response = await registrationApi.getUrl();
			baseUrl = response.base_url;
			registrationUrl = response.registration_url;
		} catch (err) {
			if (err instanceof Error && err.message.includes('404')) {
				urlNotConfigured = true;
			} else {
				addToast('Failed to load registration URL', 'error');
			}
		} finally {
			loading = false;
		}
	}

	async function saveBaseUrl() {
		if (!baseUrl.trim()) {
			addToast('Please enter a base URL', 'error');
			return;
		}
		saving = true;
		try {
			const response = await registrationApi.updateUrl({ base_url: baseUrl.trim() });
			baseUrl = response.base_url;
			registrationUrl = response.registration_url;
			urlNotConfigured = false;
			addToast('Registration URL saved', 'success');
		} catch {
			addToast('Failed to save registration URL', 'error');
		} finally {
			saving = false;
		}
	}

	function getQrCodeUrl(): string {
		if (!registrationUrl) return '';
		return `${QR_API_BASE}${encodeURIComponent(registrationUrl)}`;
	}

	async function downloadQrCode() {
		if (!registrationUrl) return;
		try {
			const blob = await api.download(getQrCodeUrl());
			const url = window.URL.createObjectURL(blob);
			const a = document.createElement('a');
			a.href = url;
			a.download = 'registration-qr-code.png';
			document.body.appendChild(a);
			a.click();
			document.body.removeChild(a);
			window.URL.revokeObjectURL(url);
			addToast('QR code downloaded', 'success');
		} catch {
			addToast('Failed to download QR code', 'error');
		}
	}

	function copyRegistrationUrl() {
		if (!registrationUrl) return;
		navigator.clipboard.writeText(registrationUrl);
		addToast('URL copied to clipboard', 'success');
	}
</script>

<div class="max-w-4xl mx-auto">
	<div class="mb-6">
		<h1 class="text-2xl font-bold text-brand-primary">Settings</h1>
		<p class="text-brand-text-secondary mt-1">Manage parish configuration and settings</p>
	</div>

	<!-- QR Code Registration Section -->
	<div class="bg-white shadow rounded-lg overflow-hidden mb-6">
		<div class="px-6 py-4 border-b border-brand-border">
			<h2 class="text-lg font-medium text-brand-primary">QR Code Registration</h2>
			<p class="text-sm text-brand-text-muted mt-1">
				Configure the public registration URL and generate a QR code for parishioners to register
			</p>
		</div>

		{#if loading}
			<div class="p-6">
				<div class="animate-pulse space-y-4">
					<div class="h-10 bg-brand-bg-subtle rounded w-full"></div>
					<div class="h-10 bg-brand-bg-subtle rounded w-32"></div>
				</div>
			</div>
		{:else}
			<div class="p-6 space-y-6">
				<!-- Base URL Input -->
				<div>
					<label for="baseUrl" class="block text-sm font-medium text-brand-text-secondary">
						Base URL
					</label>
					<p class="text-xs text-brand-text-muted mt-1 mb-2">
						Enter the publicly accessible URL for your parish database (e.g., Cloudflare tunnel URL)
					</p>
					<div class="flex gap-3">
						<input
							type="url"
							id="baseUrl"
							bind:value={baseUrl}
							placeholder="https://your-parish.example.com"
							class="flex-1 block w-full rounded-md border-brand-border shadow-sm focus:border-brand-accent focus:ring-brand-accent sm:text-sm"
						/>
						<button
							type="button"
							onclick={saveBaseUrl}
							disabled={saving}
							class="inline-flex items-center px-4 py-2 border border-transparent text-sm font-medium rounded-md shadow-sm bg-brand-accent text-white hover:bg-brand-accent/90 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-brand-accent disabled:opacity-50 disabled:cursor-not-allowed"
						>
							{#if saving}
								<svg
									class="animate-spin -ml-1 mr-2 h-4 w-4 text-white"
									fill="none"
									viewBox="0 0 24 24"
								>
									<circle
										class="opacity-25"
										cx="12"
										cy="12"
										r="10"
										stroke="currentColor"
										stroke-width="4"
									></circle>
									<path
										class="opacity-75"
										fill="currentColor"
										d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"
									></path>
								</svg>
								Saving...
							{:else}
								Save
							{/if}
						</button>
					</div>
				</div>

				{#if registrationUrl && !urlNotConfigured}
					<!-- Registration URL Display -->
					<div>
						<label class="block text-sm font-medium text-brand-text-secondary mb-2">
							Registration URL
						</label>
						<div class="flex items-center gap-3">
							<div
								class="flex-1 bg-brand-bg-subtle rounded-md px-3 py-2 text-sm text-brand-text-secondary border border-brand-border truncate"
							>
								{registrationUrl}
							</div>
							<button
								type="button"
								onclick={copyRegistrationUrl}
								class="inline-flex items-center px-3 py-2 border border-brand-border text-sm font-medium rounded-md text-brand-text-secondary bg-white hover:bg-brand-bg-subtle focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-blue-500"
							>
								<svg class="w-4 h-4 mr-1" fill="none" stroke="currentColor" viewBox="0 0 24 24">
									<path
										stroke-linecap="round"
										stroke-linejoin="round"
										stroke-width="2"
										d="M8 16H6a2 2 0 01-2-2V6a2 2 0 012-2h8a2 2 0 012 2v2m-6 12h8a2 2 0 002-2v-8a2 2 0 00-2-2h-8a2 2 0 00-2 2v8a2 2 0 002 2z"
									/>
								</svg>
								Copy
							</button>
						</div>
					</div>

					<!-- QR Code Display -->
					<div>
						<label class="block text-sm font-medium text-brand-text-secondary mb-3">
							QR Code
						</label>
						<div class="flex flex-col sm:flex-row items-start gap-6">
							<div class="bg-white p-4 border border-brand-border rounded-lg shadow-sm">
								<img src={getQrCodeUrl()} alt="Registration QR Code" class="w-[200px] h-[200px]" />
							</div>
							<div class="space-y-3">
								<p class="text-sm text-brand-text-secondary">
									Scan this QR code to access the public registration form. Print and display at
									your parish for easy access.
								</p>
								<button
									type="button"
									onclick={downloadQrCode}
									class="inline-flex items-center px-4 py-2 border border-transparent text-sm font-medium rounded-md shadow-sm text-white bg-brand-success text-white hover:bg-brand-success/90 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-brand-success"
								>
									<svg class="w-4 h-4 mr-2" fill="none" stroke="currentColor" viewBox="0 0 24 24">
										<path
											stroke-linecap="round"
											stroke-linejoin="round"
											stroke-width="2"
											d="M4 16v1a3 3 0 003 3h10a3 3 0 003-3v-1m-4-4l-4 4m0 0l-4-4m4 4V4"
										/>
									</svg>
									Download QR Code
								</button>
							</div>
						</div>
					</div>
				{:else if urlNotConfigured}
					<div class="bg-yellow-50 border border-yellow-200 rounded-md p-4">
						<div class="flex">
							<svg
								class="h-5 w-5 text-yellow-400"
								fill="none"
								stroke="currentColor"
								viewBox="0 0 24 24"
							>
								<path
									stroke-linecap="round"
									stroke-linejoin="round"
									stroke-width="2"
									d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-3L13.732 4c-.77-1.333-2.694-1.333-3.464 0L3.34 16c-.77 1.333.192 3 1.732 3z"
								/>
							</svg>
							<div class="ml-3">
								<p class="text-sm text-yellow-700">
									No base URL configured. Enter your publicly accessible URL above and click Save to
									generate a QR code.
								</p>
							</div>
						</div>
					</div>
				{/if}
			</div>
		{/if}
	</div>

	<!-- Mass Times Link -->
	<div class="bg-white shadow rounded-lg overflow-hidden">
		<div class="px-6 py-4 border-b border-brand-border">
			<h2 class="text-lg font-medium text-brand-primary">Mass Times</h2>
			<p class="text-sm text-brand-text-muted mt-1">Configure mass times for attendance tracking</p>
		</div>
		<div class="p-6">
			<a
				href="/settings/mass-times"
				class="inline-flex items-center px-4 py-2 border border-brand-border text-sm font-medium rounded-md text-brand-text-secondary bg-white hover:bg-brand-bg-subtle focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-blue-500"
			>
				<svg class="w-5 h-5 mr-2 -ml-1" fill="none" stroke="currentColor" viewBox="0 0 24 24">
					<path
						stroke-linecap="round"
						stroke-linejoin="round"
						stroke-width="2"
						d="M12 8v4l3 3m6-3a9 9 0 11-18 0 9 9 0 0118 0z"
					/>
				</svg>
				Manage Mass Times
			</a>
		</div>
	</div>
</div>
