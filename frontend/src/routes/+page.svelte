<script lang="ts">
	import {
		statisticsApi,
		attendanceApi,
		massTimesApi,
		api,
		type DashboardData,
		type MassAttendanceCreate,
		type MassTime
	} from '$lib/api';
	import StatCard from '$lib/components/StatCard.svelte';
	import QuickActions from '$lib/components/QuickActions.svelte';
	import RecentActivity from '$lib/components/RecentActivity.svelte';
	import SacramentTrendsChart from '$lib/components/SacramentTrendsChart.svelte';
	import { addToast } from '$lib/stores/toast';
	import { AlertCircle } from 'lucide-svelte';

	let dashboardData = $state<DashboardData | null>(null);
	let loading = $state(true);
	let error = $state<string | null>(null);
	let healthStatus = $state<'loading' | 'connected' | 'error'>('loading');

	// Quick entry form state
	let quickEntryDate = $state('');
	let quickEntryMassTime = $state('');
	let quickEntryCount = $state(0);
	let quickEntrySubmitting = $state(false);
	let massTimeOptions = $state<MassTime[]>([]);

	async function checkHealth() {
		try {
			const data = await api.health();
			healthStatus = data.status === 'ok' ? 'connected' : 'error';
		} catch {
			healthStatus = 'error';
		}
	}

	async function loadDashboard() {
		try {
			loading = true;
			error = null;
			dashboardData = await statisticsApi.getDashboard();
		} catch {
			error = 'Failed to load dashboard data';
		} finally {
			loading = false;
		}
	}

	async function loadMassTimes() {
		try {
			massTimeOptions = await massTimesApi.list(true);
		} catch {
			massTimeOptions = [];
		}
	}

	$effect(() => {
		checkHealth();
		loadDashboard();
		loadMassTimes();
		// Set default date to previous Sunday
		const today = new Date();
		const dayOfWeek = today.getDay();
		// eslint-disable-next-line svelte/prefer-svelte-reactivity
		const previousSunday = new Date(today);
		previousSunday.setDate(today.getDate() - dayOfWeek - (dayOfWeek === 0 ? 7 : 0));
		quickEntryDate = previousSunday.toISOString().split('T')[0];
	});

	async function submitQuickEntry() {
		if (!quickEntryDate || quickEntryCount <= 0) {
			addToast('Please enter a valid date and attendance count', 'error');
			return;
		}

		quickEntrySubmitting = true;
		try {
			const data: MassAttendanceCreate = {
				date: quickEntryDate,
				mass_time: quickEntryMassTime || undefined,
				attendance_count: quickEntryCount
			};
			await attendanceApi.create(data);
			addToast('Attendance recorded successfully', 'success');
			quickEntryCount = 0;
			quickEntryMassTime = '';
		} catch {
			addToast('Failed to record attendance', 'error');
		} finally {
			quickEntrySubmitting = false;
		}
	}

	let currentYear = new Date().getFullYear();
</script>

<div class="space-y-6">
	<!-- Page Header -->
	<div class="flex flex-col sm:flex-row sm:items-center sm:justify-between gap-4">
		<div>
			<h1 class="text-2xl font-bold text-brand-primary">Dashboard</h1>
			<p class="text-brand-text-secondary mt-1">Welcome to the ParishHub management system</p>
		</div>
		<div class="flex items-center gap-2">
			<div
				class="w-3 h-3 rounded-full {healthStatus === 'connected'
					? 'bg-brand-success'
					: healthStatus === 'loading'
						? 'bg-brand-accent animate-pulse'
						: 'bg-brand-error'}"
			></div>
			<span class="text-sm text-brand-text-secondary">
				{healthStatus === 'loading'
					? 'Connecting...'
					: healthStatus === 'connected'
						? 'Connected'
						: 'Offline'}
			</span>
		</div>
	</div>

	{#if loading}
		<!-- Loading State -->
		<div class="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
			{#each [1, 2, 3, 4] as n (n)}
				<div class="bg-white rounded-lg shadow border border-brand-border p-6 animate-pulse">
					<div class="flex items-center gap-4">
						<div class="p-3 rounded-full bg-brand-bg-muted w-14 h-14"></div>
						<div class="space-y-2">
							<div class="h-8 bg-brand-bg-muted rounded w-16"></div>
							<div class="h-4 bg-brand-bg-muted rounded w-24"></div>
						</div>
					</div>
				</div>
			{/each}
		</div>
	{:else if error}
		<!-- Error State -->
		<div class="bg-brand-error/10 border border-brand-error/20 rounded-lg p-6">
			<div class="flex items-center gap-3">
				<AlertCircle class="w-6 h-6 text-brand-error flex-shrink-0" />
				<div>
					<h3 class="text-brand-error font-medium">Failed to load dashboard</h3>
					<p class="text-brand-error/80 text-sm">{error}</p>
				</div>
			</div>
			<button
				onclick={loadDashboard}
				class="mt-4 px-4 py-2 bg-brand-error text-white rounded-lg hover:opacity-90 transition-opacity"
			>
				Retry
			</button>
		</div>
	{:else if dashboardData}
		<!-- Statistics Cards -->
		<div class="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-5 gap-4">
			<StatCard
				value={dashboardData.stats.total_people}
				label="People"
				icon="people"
				href="/people"
			/>
			<StatCard
				value={dashboardData.stats.total_households}
				label="Households"
				icon="households"
				href="/households"
			/>
			<StatCard
				value={dashboardData.stats.baptisms_this_year}
				label="Baptisms"
				sublabel="({currentYear})"
				icon="baptism"
			/>
			<StatCard
				value={dashboardData.stats.marriages_this_year}
				label="Marriages"
				sublabel="({currentYear})"
				icon="marriage"
			/>
			<StatCard
				value={dashboardData.stats.deaths_this_year}
				label="Deaths"
				sublabel="({currentYear})"
				icon="death"
			/>
		</div>

		<!-- Quick Entry: Sunday Attendance -->
		<div class="bg-white rounded-lg shadow border border-brand-border p-6">
			<h3 class="text-lg font-medium text-brand-primary mb-4">Quick Entry: Sunday Attendance</h3>
			<form
				onsubmit={(e) => {
					e.preventDefault();
					submitQuickEntry();
				}}
				class="flex flex-wrap gap-4 items-end"
			>
				<div>
					<label for="quick-date" class="block text-sm font-medium text-brand-text-secondary mb-1"
						>Date</label
					>
					<input
						type="date"
						id="quick-date"
						bind:value={quickEntryDate}
						class="px-3 py-2 border border-brand-border rounded-lg focus:ring-2 focus:ring-brand-accent focus:border-transparent"
					/>
				</div>
				<div>
					<label
						for="quick-mass-time"
						class="block text-sm font-medium text-brand-text-secondary mb-1">Mass Time</label
					>
					<select
						id="quick-mass-time"
						bind:value={quickEntryMassTime}
						class="px-3 py-2 border border-brand-border rounded-lg focus:ring-2 focus:ring-brand-accent focus:border-transparent"
					>
						<option value="">All Masses</option>
						{#each massTimeOptions as massTime}
							<option value={massTime.time}>{massTime.name} ({massTime.time})</option>
						{/each}
					</select>
				</div>
				<div>
					<label for="quick-count" class="block text-sm font-medium text-brand-text-secondary mb-1"
						>Attendance Count</label
					>
					<input
						type="number"
						id="quick-count"
						bind:value={quickEntryCount}
						min="0"
						class="px-3 py-2 border border-brand-border rounded-lg focus:ring-2 focus:ring-brand-accent focus:border-transparent w-32"
					/>
				</div>
				<button
					type="submit"
					disabled={quickEntrySubmitting}
					class="px-6 py-2 bg-brand-accent text-white rounded-lg hover:opacity-90 transition-opacity disabled:opacity-50"
				>
					{quickEntrySubmitting ? 'Saving...' : 'Record'}
				</button>
			</form>
		</div>

		<!-- Quick Actions -->
		<QuickActions />

		<!-- Two-column layout for Recent Activity and Chart -->
		<div class="grid grid-cols-1 lg:grid-cols-2 gap-6">
			<RecentActivity activities={dashboardData.recent_activity} />
			<SacramentTrendsChart trends={dashboardData.sacrament_trends} />
		</div>
	{/if}
</div>
