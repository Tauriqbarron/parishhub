<script lang="ts">
	import { Users, Home, Droplets, Heart, Cross } from 'lucide-svelte';
	import type { Component } from 'svelte';

	interface Props {
		value: number | string;
		label: string;
		sublabel?: string;
		icon: 'people' | 'households' | 'baptism' | 'marriage' | 'death';
		href?: string;
	}

	let { value, label, sublabel, icon, href }: Props = $props();

	const iconMap: Record<string, Component> = {
		people: Users,
		households: Home,
		baptism: Droplets,
		marriage: Heart,
		death: Cross
	};
</script>

{#if href}
	<a
		{href}
		class="bg-white rounded-lg shadow p-6 hover:shadow-md transition-shadow cursor-pointer block"
	>
		<div class="flex items-center gap-4">
			<div class="p-3 rounded-full {icon === 'death' ? 'bg-gray-100' : 'bg-blue-100'}">
				<svelte:component
					this={iconMap[icon]}
					class="w-8 h-8 {icon === 'death' ? 'text-gray-600' : 'text-blue-600'}"
				/>
			</div>
			<div>
				<p class="text-3xl font-bold text-gray-900">{value}</p>
				<p class="text-sm font-medium text-gray-500">{label}</p>
				{#if sublabel}
					<p class="text-xs text-brand-text-secondary">{sublabel}</p>
				{/if}
			</div>
		</div>
	</a>
{:else}
	<div class="bg-white rounded-lg shadow p-6">
		<div class="flex items-center gap-4">
			<div class="p-3 rounded-full {icon === 'death' ? 'bg-gray-100' : 'bg-blue-100'}">
				<svelte:component
					this={iconMap[icon]}
					class="w-8 h-8 {icon === 'death' ? 'text-gray-600' : 'text-blue-600'}"
				/>
			</div>
			<div>
				<p class="text-3xl font-bold text-gray-900">{value}</p>
				<p class="text-sm font-medium text-gray-500">{label}</p>
				{#if sublabel}
					<p class="text-xs text-brand-text-secondary">{sublabel}</p>
				{/if}
			</div>
		</div>
	</div>
{/if}
