<script lang="ts">
	import type { RecentActivity } from '$lib/api';
	import { goto } from '$app/navigation';
	import { UserPlus, Church, Home, Skull } from 'lucide-svelte';
	import type { Component } from 'svelte';

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

	function getActivityIcon(type: string): { icon: Component; color: string; bg: string } {
		switch (type) {
			case 'person_added':
				return { icon: UserPlus, color: 'text-blue-600', bg: 'bg-blue-100' };
			case 'sacrament_recorded':
				return { icon: Church, color: 'text-purple-600', bg: 'bg-purple-100' };
			case 'household_created':
				return { icon: Home, color: 'text-green-600', bg: 'bg-green-100' };
			case 'death_recorded':
				return { icon: Skull, color: 'text-gray-600', bg: 'bg-gray-100' };
			default:
				return { icon: Home, color: 'text-green-600', bg: 'bg-green-100' };
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

<div class="bg-white rounded-lg shadow p-6">
	<h3 class="text-lg font-medium text-gray-900 mb-4">Recent Activity</h3>
	{#if activities.length === 0}
		<p class="text-gray-500 text-sm">No recent activity</p>
	{:else}
		<div class="space-y-4">
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
						class="flex items-start gap-3 hover:bg-gray-50 rounded-lg p-2 -m-2 cursor-pointer transition-colors group"
					>
						<div class="p-2 rounded-full flex-shrink-0 {iconInfo.bg}">
							<svelte:component this={iconInfo.icon} class="w-4 h-4 {iconInfo.color}" />
						</div>
						<div class="flex-1 min-w-0">
							<p class="text-sm text-gray-900 group-hover:text-blue-600 transition-colors">
								{activity.description}
							</p>
							<p class="text-xs text-gray-500">{formatTimeAgo(activity.timestamp)}</p>
						</div>
					</a>
				{:else}
					<div class="flex items-start gap-3">
						<div class="p-2 rounded-full flex-shrink-0 {iconInfo.bg}">
							<svelte:component this={iconInfo.icon} class="w-4 h-4 {iconInfo.color}" />
						</div>
						<div class="flex-1 min-w-0">
							<p class="text-sm text-gray-900">{activity.description}</p>
							<p class="text-xs text-gray-500">{formatTimeAgo(activity.timestamp)}</p>
						</div>
					</div>
				{/if}
			{/each}
		</div>
	{/if}
</div>
