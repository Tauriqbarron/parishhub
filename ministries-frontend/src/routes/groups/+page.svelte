<script lang="ts">
	import { goto } from '$app/navigation';
	import { onMount } from 'svelte';
	import { memberApi, type MinistrySummary } from '$lib/api';
	import { Users, Shield, ChevronRight } from 'lucide-svelte';

	let ministries = $state<MinistrySummary[]>([]);
	let loading = $state(true);
	let error = $state('');

	onMount(async () => {
		try {
			const result = await memberApi.ministries();
			ministries = result.ministries;
		} catch (err) {
			error = err instanceof Error ? err.message : 'Failed to load groups';
		} finally {
			loading = false;
		}
	});
</script>

<div>
	<h1 class="text-xl font-semibold text-brand-primary tracking-tight mb-4">My Groups</h1>

	{#if loading}
	<div class="space-y-3">
		{#each [1, 2] as i}
			<div class="animate-pulse bg-white rounded-lg border border-brand-border p-4">
				<div class="flex items-center justify-between">
					<div class="min-w-0 flex-1">
						<div class="flex items-center gap-2">
							<div class="h-4 bg-brand-bg-muted rounded w-28"></div>
							<div class="h-4 bg-brand-bg-muted rounded w-14"></div>
						</div>
						<div class="mt-1 h-3 bg-brand-bg-muted rounded w-40"></div>
						<div class="mt-1.5 flex items-center gap-1">
							<div class="h-3 w-3 bg-brand-bg-muted rounded"></div>
							<div class="h-3 bg-brand-bg-muted rounded w-20"></div>
						</div>
					</div>
					<div class="h-4 w-4 bg-brand-bg-muted rounded ml-2"></div>
				</div>
			</div>
		{/each}
	</div>
	{:else if error}
		<div class="p-4 bg-red-50 rounded-lg text-red-700 text-sm">{error}</div>
	{:else if ministries.length === 0}
		<div class="bg-white rounded-lg border border-brand-border p-8 text-center">
			<Users class="mx-auto w-10 h-10 text-brand-text-muted" />
			<p class="mt-2 text-sm text-brand-text-secondary">You're not part of any groups yet.</p>
			<p class="text-xs text-brand-text-muted">Ask your leader to add you.</p>
		</div>
	{:else}
		<div class="space-y-3">
			{#each ministries as m (m.id)}
				<button
					class="w-full text-left bg-white rounded-lg border border-brand-border p-4 hover:border-orange-200 transition-colors"
					onclick={() => goto(`/groups/${m.id}`)}
				>
					<div class="flex items-center justify-between">
						<div class="min-w-0 flex-1">
							<div class="flex items-center gap-2">
								<h3 class="text-sm font-medium text-brand-primary truncate">{m.name}</h3>
								{#if m.user_role === 'leader' || m.user_role === 'admin'}
									<span class="inline-flex items-center gap-0.5 px-1.5 py-0.5 bg-brand-accent-muted text-brand-accent rounded text-[10px] font-medium">
										<Shield class="w-3 h-3" /> {m.user_role}
									</span>
								{/if}
								{#if !m.is_active}
									<span class="px-1.5 py-0.5 bg-brand-bg-muted text-brand-text-secondary rounded text-[10px]">Inactive</span>
								{/if}
							</div>
							{#if m.description}
								<p class="mt-0.5 text-xs text-brand-text-muted truncate">{m.description}</p>
							{/if}
							<p class="mt-1 text-xs text-brand-text-muted">
								<Users class="w-3 h-3 inline" /> {m.member_count} member{m.member_count !== 1 ? 's' : ''}
							</p>
						</div>
						<ChevronRight class="w-4 h-4 text-brand-text-muted shrink-0 ml-2" />
					</div>
				</button>
			{/each}
		</div>
	{/if}
</div>
