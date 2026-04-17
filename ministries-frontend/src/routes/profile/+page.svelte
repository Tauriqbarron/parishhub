<script lang="ts">
	import { goto } from '$app/navigation';
	import { onMount } from 'svelte';
	import { memberApi, type MemberUser, type MinistrySummary } from '$lib/api';
	import { User, Shield, ChevronRight, Users } from 'lucide-svelte';

	let user = $state<MemberUser | null>(null);
	let ministries = $state<MinistrySummary[]>([]);
	let loading = $state(true);
	let error = $state('');

	onMount(async () => {
		try {
			const [me, result] = await Promise.all([
				memberApi.me(),
				memberApi.ministries()
			]);
			user = me;
			ministries = result.ministries;
		} catch (err) {
			error = err instanceof Error ? err.message : 'Failed to load profile';
		} finally {
			loading = false;
		}
	});

	const roleColors: Record<string, string> = {
		leader: 'bg-orange-50 text-orange-700',
		admin: 'bg-purple-50 text-purple-700',
		member: 'bg-gray-100 text-gray-600'
	};
</script>

<div>
	<h1 class="text-xl font-semibold text-gray-900 mb-4">Profile</h1>

	{#if loading}
		<div class="animate-pulse space-y-4">
			<div class="bg-white rounded-lg border border-gray-200 p-4 flex items-center gap-4">
				<div class="w-14 h-14 bg-gray-100 rounded-full"></div>
				<div>
					<div class="h-5 bg-gray-100 rounded w-32 mb-1.5"></div>
					<div class="h-3 bg-gray-100 rounded w-40"></div>
				</div>
			</div>
			<div class="h-4 bg-gray-100 rounded w-24"></div>
			{#each [1, 2] as i}
				<div class="bg-white rounded-lg border border-gray-200 p-4 flex items-center justify-between">
					<div class="h-4 bg-gray-100 rounded w-28"></div>
					<div class="h-4 w-4 bg-gray-100 rounded"></div>
				</div>
			{/each}
		</div>
	{:else if error}
		<div class="p-4 bg-red-50 rounded-lg text-red-700 text-sm">{error}</div>
	{:else}
		<!-- User Info Card -->
		<div class="bg-white rounded-lg border border-gray-200 p-4 mb-4 flex items-center gap-4">
			{#if user?.picture}
				<img src={user.picture} alt="" class="w-14 h-14 rounded-full" />
			{:else}
				<div class="w-14 h-14 rounded-full bg-gray-100 flex items-center justify-center">
					<User class="w-7 h-7 text-gray-400" />
				</div>
			{/if}
			<div>
				<h2 class="text-base font-semibold text-gray-900">{user?.name || 'Member'}</h2>
				<p class="text-sm text-gray-500">{user?.email}</p>
			</div>
		</div>

		<!-- Ministries -->
		<h3 class="text-sm font-medium text-gray-500 mb-2">My Ministries</h3>
		<div class="bg-white rounded-lg border border-gray-200 divide-y divide-gray-100">
			{#if ministries.length === 0}
				<p class="p-4 text-sm text-gray-400 text-center">No ministries yet</p>
			{:else}
				{#each ministries as m (m.id)}
					<button
						class="w-full text-left px-4 py-3 flex items-center justify-between hover:bg-gray-50 transition-colors"
						onclick={() => goto(`/groups/${m.id}`)}
					>
						<div class="min-w-0 flex-1">
							<div class="flex items-center gap-2">
								<span class="text-sm font-medium text-gray-900 truncate">{m.name}</span>
								<span class="inline-block px-1.5 py-0.5 text-[10px] font-medium rounded {roleColors[m.user_role] || roleColors.member}">
									{m.user_role}
								</span>
							</div>
							<p class="text-xs text-gray-400 mt-0.5">
								<Users class="w-3 h-3 inline" /> {m.member_count} member{m.member_count !== 1 ? 's' : ''}
							</p>
						</div>
						<ChevronRight class="w-4 h-4 text-gray-300 shrink-0 ml-2" />
					</button>
				{/each}
			{/if}
		</div>
	{/if}
</div>
