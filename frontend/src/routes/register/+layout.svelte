<script lang="ts">
	import '../../app.css';
	import Toast from '$components/Toast.svelte';

	let { children } = $props();
</script>

<div class="min-h-screen bg-gradient-to-b from-blue-50 to-gray-100">
	<header class="bg-white shadow-sm border-b border-gray-200">
		<div class="max-w-3xl mx-auto px-4 py-4">
			<div class="flex items-center justify-center">
				<div class="text-center">
					<h1 class="text-xl font-semibold text-blue-900">Auckland Latin Mass chaplaincy</h1>
					<p class="text-sm text-gray-500">Member Registration</p>
				</div>
			</div>
		</div>
	</header>

	<main class="flex-1">
		{@render children()}
	</main>

	<footer class="py-6 text-center text-sm text-gray-500">
		<p>Need help? Contact the chaplaincy office</p>
	</footer>
</div>

<Toast />
