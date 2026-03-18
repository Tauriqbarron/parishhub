<script lang="ts">
	import { page } from '$app/stores';

	const householdName = $page.url.searchParams.get('name');
</script>

<div class="max-w-lg mx-auto text-center py-12">
	<div class="text-green-500 mb-4">
		<svg class="w-16 h-16 mx-auto" fill="none" stroke="currentColor" viewBox="0 0 24 24">
			<path
				stroke-linecap="round"
				stroke-linejoin="round"
				stroke-width="2"
				d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z"
			/>
		</svg>
	</div>

	<h1 class="text-2xl font-bold mb-4">Registration Complete!</h1>

	{#if householdName}
		<p class="text-gray-600 mb-6">
			Thank you for registering the {householdName} household.
		</p>
	{/if}

	<p class="text-gray-600 mb-4">
		Your information has been submitted to the chaplaincy office. We will review your information
		and be in touch shortly.
	</p>

	<p class="text-gray-500 text-sm">
		If you need to make any changes or additions, please contact us at
		<a href="mailto:dataadmin@fssp.nz" class="text-blue-600 hover:text-blue-800 underline"
			>dataadmin@fssp.nz</a
		>.
	</p>
</div>
