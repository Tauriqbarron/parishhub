<script lang="ts">
	import type { RecentActivity } from '$lib/api';
	import { goto } from '$app/navigation';
	import { UserPlus, Church, Home, Skull } from 'lucide-svelte';

	type IconComponent = typeof UserPlus;

	interface Props {
		activities: RecentActivity[];
	}

	let { activities }: Props = $props();

	function formatTimeAgo(timestamp: string): string {
		const date = new Date(timestamp);
		const now = new Date();
		const diffMs = now.getTime() - date.getTime();
		const diffMins = Math.floor(diffMs / 60000);
		const diffHours = Math.floor(diffMs / 3600000);
		const diffDays = Math.floor(diffMs / 86400000);

		if (diffMins < 1) return 'just now';
		if (diffMins < 60) return `${diffMins} minute${diffMins > 1 ? 's' : ''} ago`;
		if (diffHours < 24) return `${diffHours} hour${diffHours > 1 ? 's' : ''} ago`;
		if (diffDays < 7) return `${diffDays} day${diffDays > 1 ? 's' : ''} ago`;
		return date.toLocaleDateString();
	}

	function getActivityIcon(type: string): { icon: IconComponent; color: string; bg: string } {
		switch (type) {
			case 'person_added':
				return { icon: UserPlus, color: 'text-brand-accent', bg: 'bg-brand-accent/10' };
			case 'sacrament_recorded':
				return { icon: Church, color: 'text-brand-primary-light', bg: 'bg-brand-primary/10' };
			case 'household_created':
				return { icon: Home, color: 'text-brand-success', bg: 'bg-brand-success/10' };
			case 'death_recorded':
				return { icon: Skull, color: 'text-brand-text-muted', bg: 'bg-brand-bg-muted' };
			default:
				return { icon: Home, color: 'text-brand-success', bg: 'bg-brand-success/10' };
		}
	}

	function getHref(activity: RecentActivity): string | null {
		if (activity.record_id == null) return null;
		switch (activity.record_type) {
			case 'person':
			case 'death':
				return `/people/${activity.record_id}`;
			case 'sacrament':
				return `/people/${activity.record_id}`;
			case 'household':
				return `/households/${activity.record_id}`;
			default:
				return null;
		}
	}
</script>

<div class="bg-white rounded-lg border border-brand-border p-6">
	<h3 class="text-lg font-semibold text-brand-primary mb-4 tracking-tight">Recent Activity</h3>
	{#if activities.length === 0}
		<p class="text-brand-text-secondary text-sm">No recent activity</p>
	{:else}
		<div class="space-y-3">
			{#each activities as activity}
				{@const href = getHref(activity)}
				{@const iconInfo = getActivityIcon(activity.type)}
				{#if href}
					<a
						{href}
						onclick={(e) => {
							e.preventDefault();
							goto(href);
						}}
						class="flex items-start gap-3 hover:bg-brand-bg-subtle rounded-lg p-2 -m-2 cursor-pointer transition-colors group"
					>
						<div class="p-2 rounded-lg flex-shrink-0 {iconInfo.bg}">
							<svelte:component this={iconInfo.icon} class="w-4 h-4 {iconInfo.color}" />
						</div>
						<div class="flex-1 min-w-0">
							<p class="text-sm text-brand-primary group-hover:text-brand-accent transition-colors">
								{activity.description}
							</p>
							<p class="text-xs text-brand-text-muted mt-0.5">
								{formatTimeAgo(activity.timestamp)}
							</p>
						</div>
					</a>
				{:else}
					<div class="flex items-start gap-3 p-2 -m-2">
						<div class="p-2 rounded-lg flex-shrink-0 {iconInfo.bg}">
							<svelte:component this={iconInfo.icon} class="w-4 h-4 {iconInfo.color}" />
						</div>
						<div class="flex-1 min-w-0">
							<p class="text-sm text-brand-primary">{activity.description}</p>
							<p class="text-xs text-brand-text-muted mt-0.5">
								{formatTimeAgo(activity.timestamp)}
							</p>
						</div>
					</div>
				{/if}
			{/each}
		</div>
	{/if}
</div>
