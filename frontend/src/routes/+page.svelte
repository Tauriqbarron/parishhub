<script lang="ts">
	let healthStatus = $state<string>('Checking...');

	async function checkHealth() {
		try {
			const response = await fetch('/api/health');
			const data = await response.json();
			healthStatus = data.status === 'ok' ? 'Backend Connected' : 'Backend Error';
		} catch {
			healthStatus = 'Backend Unavailable';
		}
	}

	$effect(() => {
		checkHealth();
	});
</script>

<div class="min-h-screen bg-gray-100 flex items-center justify-center">
	<div class="text-center">
		<h1 class="text-4xl font-bold text-gray-900 mb-4">Parish Database</h1>
		<p class="text-gray-600 mb-8">Manage your parish records with ease</p>
		<div class="inline-flex items-center px-4 py-2 rounded-full bg-white shadow">
			<span
				class="w-2 h-2 rounded-full mr-2 {healthStatus === 'Backend Connected'
					? 'bg-green-500'
					: healthStatus === 'Checking...'
						? 'bg-yellow-500'
						: 'bg-red-500'}"
			></span>
			<span class="text-sm text-gray-700">{healthStatus}</span>
		</div>
	</div>
</div>
