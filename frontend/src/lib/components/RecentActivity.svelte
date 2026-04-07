<script lang="ts">
	import type { RecentActivity } from '$lib/api';
	import { goto } from '$app/navigation';

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

	function getActivityIcon(type: string): string {
		switch (type) {
			case 'person_added':
				return 'person';
			case 'sacrament_recorded':
				return 'sacrament';
			case 'household_created':
				return 'household';
			case 'death_recorded':
				return 'death';
			default:
				return 'default';
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
				{#if href}
					<a
						{href}
						onclick={(e) => {
							e.preventDefault();
							goto(href);
						}}
						class="flex items-start gap-3 hover:bg-gray-50 rounded-lg p-2 -m-2 cursor-pointer transition-colors group"
					>
						<div
							class="p-2 rounded-full flex-shrink-0 {getActivityIcon(activity.type) === 'person'
								? 'bg-blue-100'
								: getActivityIcon(activity.type) === 'death'
									? 'bg-gray-100'
									: getActivityIcon(activity.type) === 'sacrament'
										? 'bg-purple-100'
										: 'bg-green-100'}"
						>
							{#if getActivityIcon(activity.type) === 'person'}
								<svg
									class="w-4 h-4 text-blue-600"
									fill="none"
									stroke="currentColor"
									viewBox="0 0 24 24"
								>
									<path
										stroke-linecap="round"
										stroke-linejoin="round"
										stroke-width="2"
										d="M16 7a4 4 0 11-8 0 4 4 0 018 0zM12 14a7 7 0 00-7 7h14a7 7 0 00-7-7z"
									/>
								</svg>
							{:else if getActivityIcon(activity.type) === 'death'}
								<svg
									class="w-4 h-4 text-gray-600"
									fill="none"
									stroke="currentColor"
									viewBox="0 0 24 24"
								>
									<path
										stroke-linecap="round"
										stroke-linejoin="round"
										stroke-width="2"
										d="M12 2C6.48 2 2 6.48 2 12s4.48 10 10 10 10-4.48 10-10S17.52 2 12 2zm0 18c-4.42 0-8-3.58-8-8s3.58-8 8-8 8 3.58 8 8-3.58 8-8 8z"
									/>
									<circle cx="12" cy="12" r="3" />
								</svg>
							{:else if getActivityIcon(activity.type) === 'sacrament'}
								<svg
									class="w-4 h-4 text-purple-600"
									fill="none"
									stroke="currentColor"
									viewBox="0 0 24 24"
								>
									<path
										stroke-linecap="round"
										stroke-linejoin="round"
										stroke-width="2"
										d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z"
									/>
								</svg>
							{:else}
								<svg
									class="w-4 h-4 text-green-600"
									fill="none"
									stroke="currentColor"
									viewBox="0 0 24 24"
								>
									<path
										stroke-linecap="round"
										stroke-linejoin="round"
										stroke-width="2"
										d="M3 12l2-2m0 0l7-7 7 7M5 10v10a1 1 0 001 1h3m10-11l2 2m-2-2v10a1 1 0 01-1 1h-3m-6 0a1 1 0 001-1v-4a1 1 0 011-1h2a1 1 0 011 1v4a1 1 0 001 1m-6 0h6"
									/>
								</svg>
							{/if}
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
						<div
							class="p-2 rounded-full flex-shrink-0 {getActivityIcon(activity.type) === 'person'
								? 'bg-blue-100'
								: getActivityIcon(activity.type) === 'death'
									? 'bg-gray-100'
									: getActivityIcon(activity.type) === 'sacrament'
										? 'bg-purple-100'
										: 'bg-green-100'}"
						>
							{#if getActivityIcon(activity.type) === 'person'}
								<svg
									class="w-4 h-4 text-blue-600"
									fill="none"
									stroke="currentColor"
									viewBox="0 0 24 24"
								>
									<path
										stroke-linecap="round"
										stroke-linejoin="round"
										stroke-width="2"
										d="M16 7a4 4 0 11-8 0 4 4 0 018 0zM12 14a7 7 0 00-7 7h14a7 7 0 00-7-7z"
									/>
								</svg>
							{:else if getActivityIcon(activity.type) === 'death'}
								<svg
									class="w-4 h-4 text-gray-600"
									fill="none"
									stroke="currentColor"
									viewBox="0 0 24 24"
								>
									<path
										stroke-linecap="round"
										stroke-linejoin="round"
										stroke-width="2"
										d="M12 2C6.48 2 2 6.48 2 12s4.48 10 10 10 10-4.48 10-10S17.52 2 12 2zm0 18c-4.42 0-8-3.58-8-8s3.58-8 8-8 8 3.58 8 8-3.58 8-8 8z"
									/>
									<circle cx="12" cy="12" r="3" />
								</svg>
							{:else if getActivityIcon(activity.type) === 'sacrament'}
								<svg
									class="w-4 h-4 text-purple-600"
									fill="none"
									stroke="currentColor"
									viewBox="0 0 24 24"
								>
									<path
										stroke-linecap="round"
										stroke-linejoin="round"
										stroke-width="2"
										d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z"
									/>
								</svg>
							{:else}
								<svg
									class="w-4 h-4 text-green-600"
									fill="none"
									stroke="currentColor"
									viewBox="0 0 24 24"
								>
									<path
										stroke-linecap="round"
										stroke-linejoin="round"
										stroke-width="2"
										d="M3 12l2-2m0 0l7-7 7 7M5 10v10a1 1 0 001 1h3m10-11l2 2m-2-2v10a1 1 0 01-1 1h-3m-6 0a1 1 0 001-1v-4a1 1 0 011-1h2a1 1 0 011 1v4a1 1 0 001 1m-6 0h6"
									/>
								</svg>
							{/if}
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
