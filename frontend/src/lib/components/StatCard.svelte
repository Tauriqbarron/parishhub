<script lang="ts">
	import { Users, Home, Droplets, Heart, Cross } from 'lucide-svelte';

	type IconComponent = typeof Users;

	interface Props {
		value: number | string;
		label: string;
		sublabel?: string;
		icon: 'people' | 'households' | 'baptism' | 'marriage' | 'death';
		href?: string;
	}

	let { value, label, sublabel, icon, href }: Props = $props();

	const iconMap: Record<string, IconComponent> = {
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
		class="bg-white rounded-lg border border-brand-border p-6 hover:shadow-md transition-all cursor-pointer block group"
	>
		<div class="flex items-center gap-4">
			<div class="p-3 rounded-lg {icon === 'death' ? 'bg-brand-bg-muted' : 'bg-brand-accent/10'}">
				<svelte:component
					this={iconMap[icon]}
					class="w-7 h-7 {icon === 'death' ? 'text-brand-text-muted' : 'text-brand-accent'}"
				/>
			</div>
			<div>
				<p class="text-3xl font-bold text-brand-primary tracking-tight">{value}</p>
				<p class="text-sm text-brand-text-secondary mt-0.5">{label}</p>
				{#if sublabel}
					<p class="text-xs text-brand-text-muted">{sublabel}</p>
				{/if}
			</div>
		</div>
	</a>
{:else}
	<div class="bg-white rounded-lg border border-brand-border p-6">
		<div class="flex items-center gap-4">
			<div class="p-3 rounded-lg {icon === 'death' ? 'bg-brand-bg-muted' : 'bg-brand-accent/10'}">
				<svelte:component
					this={iconMap[icon]}
					class="w-7 h-7 {icon === 'death' ? 'text-brand-text-muted' : 'text-brand-accent'}"
				/>
			</div>
			<div>
				<p class="text-3xl font-bold text-brand-primary tracking-tight">{value}</p>
				<p class="text-sm text-brand-text-secondary mt-0.5">{label}</p>
				{#if sublabel}
					<p class="text-xs text-brand-text-muted">{sublabel}</p>
				{/if}
			</div>
		</div>
	</div>
{/if}
