<script lang="ts">
	import { api } from '$lib/api';
	import { page } from '$app/stores';
	import { goto } from '$app/navigation';

	let title = $state('');
	let body = $state('');
	let scope = $state<'parish' | 'ministry'>('parish');
	let ministryId = $state<number | null>(null);
	let channels: { email: boolean; sms: boolean; app: boolean } = $state({
		email: true,
		sms: false,
		app: true
	});
	let submitting = $state(false);
	let error = $state<string | null>(null);
	let success = $state(false);

	// Load ministries for scope selector
	let ministries: Array<{ id: number; name: string }> = $state([]);

	async function loadMinistries() {
		try {
			const data = await api.get<{ items: Array<{ id: number; name: string }> }>(
				'/ministries?per_page=100'
			);
			ministries = data.items;
		} catch {
			// Non-critical
		}
	}

	$effect(() => {
		loadMinistries();
	});

	async function handleSubmit(e: Event) {
		e.preventDefault();
		error = null;
		submitting = true;

		try {
			await api.post('/announcements', {
				title: title.trim(),
				body: body.trim(),
				scope,
				ministry_id: scope === 'ministry' ? ministryId : null,
				channels: Object.entries(channels)
					.filter(([, v]) => v)
					.map(([k]) => k)
			});
			success = true;
			setTimeout(() => goto('/announcements'), 1500);
		} catch (e) {
			error = e instanceof Error ? e.message : 'Failed to create announcement';
		} finally {
			submitting = false;
		}
	}

	function toggleChannel(channel: 'email' | 'sms' | 'app') {
		channels = { ...channels, [channel]: !channels[channel] };
	}
</script>

<div class="max-w-2xl mx-auto">
	<div class="mb-6">
		<a href="/announcements" class="text-sm text-brand-text-muted hover:text-brand-primary">
			&larr; Back to announcements
		</a>
	</div>

	<h1 class="text-2xl font-bold tracking-tight text-brand-primary mb-6">New Announcement</h1>

	{#if success}
		<div class="card p-4 mb-6 bg-green-50 border-green-200">
			<p class="text-sm text-green-800 font-medium">
				Announcement created successfully! Redirecting...
			</p>
		</div>
	{/if}

	{#if error}
		<div class="card p-4 mb-6 bg-red-50 border-red-200">
			<p class="text-sm text-red-800">{error}</p>
		</div>
	{/if}

	<form onsubmit={handleSubmit} class="space-y-6">
		<!-- Title -->
		<div>
			<label for="title" class="block text-sm font-medium text-brand-text-secondary mb-1.5">
				Title
			</label>
			<input
				id="title"
				type="text"
				bind:value={title}
				required
				placeholder="Sunday Mass schedule update..."
				class="w-full px-3 py-2 rounded-sm border border-brand-border bg-white text-brand-primary text-sm placeholder:text-brand-text-muted focus:outline-none focus:ring-2 focus:ring-brand-accent focus:ring-offset-2"
			/>
		</div>

		<!-- Body -->
		<div>
			<label for="body" class="block text-sm font-medium text-brand-text-secondary mb-1.5">
				Body <span class="text-brand-text-muted font-normal">(Markdown supported)</span>
			</label>
			<textarea
				id="body"
				bind:value={body}
				required
				rows={8}
				placeholder="Write your announcement...&#10;&#10;Use **bold**, *italic*, and - bullet points."
				class="w-full px-3 py-2 rounded-sm border border-brand-border bg-white text-brand-primary text-sm placeholder:text-brand-text-muted focus:outline-none focus:ring-2 focus:ring-brand-accent focus:ring-offset-2 resize-y"
			></textarea>
		</div>

		<!-- Scope -->
		<div>
			<label class="block text-sm font-medium text-brand-text-secondary mb-2">Scope</label>
			<div class="flex gap-3">
				<label class="flex items-center gap-2 cursor-pointer">
					<input
						type="radio"
						name="scope"
						value="parish"
						bind:group={scope}
						class="text-brand-accent focus:ring-brand-accent"
					/>
					<span class="text-sm text-brand-primary">Entire Parish</span>
				</label>
				<label class="flex items-center gap-2 cursor-pointer">
					<input
						type="radio"
						name="scope"
						value="ministry"
						bind:group={scope}
						class="text-brand-accent focus:ring-brand-accent"
					/>
					<span class="text-sm text-brand-primary">Specific Ministry</span>
				</label>
			</div>

			{#if scope === 'ministry'}
				<select
					bind:value={ministryId}
					required
					class="mt-2 w-full px-3 py-2 rounded-sm border border-brand-border bg-white text-brand-primary text-sm focus:outline-none focus:ring-2 focus:ring-brand-accent"
				>
					<option value={null}>Select a ministry...</option>
					{#each ministries as m}
						<option value={m.id}>{m.name}</option>
					{/each}
				</select>
			{/if}
		</div>

		<!-- Channels -->
		<div>
			<label class="block text-sm font-medium text-brand-text-secondary mb-2">
				Delivery Channels
			</label>
			<div class="flex flex-wrap gap-3">
				<label class="flex items-center gap-2 cursor-pointer">
					<input
						type="checkbox"
						checked={channels.email}
						onchange={() => toggleChannel('email')}
						class="text-brand-accent focus:ring-brand-accent rounded-sm"
					/>
					<span class="text-sm text-brand-primary">Email</span>
				</label>
				<label class="flex items-center gap-2 cursor-pointer">
					<input
						type="checkbox"
						checked={channels.sms}
						onchange={() => toggleChannel('sms')}
						class="text-brand-accent focus:ring-brand-accent rounded-sm"
					/>
					<span class="text-sm text-brand-primary">SMS</span>
				</label>
				<label class="flex items-center gap-2 cursor-pointer">
					<input
						type="checkbox"
						checked={channels.app}
						onchange={() => toggleChannel('app')}
						class="text-brand-accent focus:ring-brand-accent rounded-sm"
					/>
					<span class="text-sm text-brand-primary">In-App</span>
				</label>
			</div>
		</div>

		<!-- Submit -->
		<div class="flex items-center gap-3 pt-2">
			<button
				type="submit"
				disabled={submitting || !title.trim() || !body.trim()}
				class="btn-primary disabled:opacity-50 disabled:cursor-not-allowed inline-flex items-center gap-2"
			>
				{#if submitting}
					<span class="w-4 h-4 border-2 border-white border-t-transparent rounded-full animate-spin"
					></span>
				{/if}
				{submitting ? 'Sending...' : 'Send Announcement'}
			</button>
			<a href="/announcements" class="btn-secondary"> Cancel </a>
		</div>
	</form>
</div>
