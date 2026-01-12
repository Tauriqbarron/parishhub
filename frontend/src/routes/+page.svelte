<script lang="ts">
	let healthStatus = $state<'loading' | 'connected' | 'error'>('loading');

	async function checkHealth() {
		try {
			const response = await fetch('/api/health');
			const data = await response.json();
			healthStatus = data.status === 'ok' ? 'connected' : 'error';
		} catch {
			healthStatus = 'error';
		}
	}

	$effect(() => {
		checkHealth();
	});
</script>

<div>
	<div class="mb-8">
		<h1 class="text-2xl font-bold text-gray-900">Dashboard</h1>
		<p class="text-gray-600 mt-1">Welcome to the Parish Database management system</p>
	</div>

	<!-- Status Cards -->
	<div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
		<!-- Backend Status Card -->
		<div class="bg-white rounded-lg shadow p-6">
			<div class="flex items-center gap-4">
				<div class="p-3 rounded-full {healthStatus === 'connected' ? 'bg-green-100' : healthStatus === 'loading' ? 'bg-yellow-100' : 'bg-red-100'}">
					{#if healthStatus === 'loading'}
						<svg class="w-6 h-6 text-yellow-600 animate-spin" fill="none" viewBox="0 0 24 24">
							<circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4"></circle>
							<path class="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
						</svg>
					{:else if healthStatus === 'connected'}
						<svg class="w-6 h-6 text-green-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
							<path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M5 13l4 4L19 7" />
						</svg>
					{:else}
						<svg class="w-6 h-6 text-red-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
							<path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12" />
						</svg>
					{/if}
				</div>
				<div>
					<h3 class="text-sm font-medium text-gray-500">Backend Status</h3>
					<p class="text-lg font-semibold {healthStatus === 'connected' ? 'text-green-700' : healthStatus === 'loading' ? 'text-yellow-700' : 'text-red-700'}">
						{healthStatus === 'loading' ? 'Checking...' : healthStatus === 'connected' ? 'Connected' : 'Unavailable'}
					</p>
				</div>
			</div>
		</div>

		<!-- Quick Links Card -->
		<div class="bg-white rounded-lg shadow p-6">
			<h3 class="text-sm font-medium text-gray-500 mb-4">Quick Actions</h3>
			<div class="space-y-2">
				<a href="/people" class="flex items-center gap-2 text-blue-600 hover:text-blue-800 transition-colors">
					<svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
						<path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 4.354a4 4 0 110 5.292M15 21H3v-1a6 6 0 0112 0v1zm0 0h6v-1a6 6 0 00-9-5.197M13 7a4 4 0 11-8 0 4 4 0 018 0z" />
					</svg>
					<span>Manage People</span>
				</a>
				<a href="/households" class="flex items-center gap-2 text-blue-600 hover:text-blue-800 transition-colors">
					<svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
						<path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M3 12l2-2m0 0l7-7 7 7M5 10v10a1 1 0 001 1h3m10-11l2 2m-2-2v10a1 1 0 01-1 1h-3m-6 0a1 1 0 001-1v-4a1 1 0 011-1h2a1 1 0 011 1v4a1 1 0 001 1m-6 0h6" />
					</svg>
					<span>Manage Households</span>
				</a>
			</div>
		</div>

		<!-- Info Card -->
		<div class="bg-white rounded-lg shadow p-6">
			<h3 class="text-sm font-medium text-gray-500 mb-4">About</h3>
			<p class="text-sm text-gray-600">
				This application helps manage parish records including people, households, and sacraments.
			</p>
		</div>
	</div>
</div>
