<script lang="ts">
	import { registrationSessionStore } from '$lib/stores/registrationSession';
	import MemberSacraments from './MemberSacraments.svelte';
	import { get } from 'svelte/store';

	let members = $derived(get(registrationSessionStore).members);

	$effect(() => {
		const unsubscribe = registrationSessionStore.subscribe((session) => {
			members = session.members;
		});
		return unsubscribe;
	});

	export function isValid(): boolean {
		return true;
	}
</script>

<div class="space-y-4">
	<p class="text-gray-600">
		Add any sacraments each family member has received. This step is optional and can be completed
		later.
	</p>

	{#if members.length === 0}
		<div class="text-center py-8 border-2 border-dashed border-gray-300 rounded-lg">
			<svg
				class="mx-auto h-12 w-12 text-gray-400"
				fill="none"
				stroke="currentColor"
				viewBox="0 0 24 24"
			>
				<path
					stroke-linecap="round"
					stroke-linejoin="round"
					stroke-width="2"
					d="M13 16h-1v-4h-1m1-4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z"
				/>
			</svg>
			<p class="mt-2 text-sm text-gray-500">No family members added yet</p>
			<p class="text-xs text-gray-400">Go back to the Family Members step to add members first</p>
		</div>
	{:else}
		<div class="space-y-3">
			{#each members as member (member.tempId)}
				<MemberSacraments {member} />
			{/each}
		</div>
	{/if}
</div>
