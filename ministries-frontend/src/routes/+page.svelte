<script lang="ts">
	import { goto } from '$app/navigation';
	import { onMount } from 'svelte';

	onMount(() => {
		const token = localStorage.getItem('member_token');
		goto(token ? '/dashboard' : '/login');
	});
</script>

<div class="min-h-screen flex items-center justify-center">
	<p class="text-sm text-gray-400">Redirecting...</p>
</div>
