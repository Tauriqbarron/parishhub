<script lang="ts">
	import { statisticsApi, attendanceApi, massTimesApi, api, type DashboardData, type MassAttendanceCreate, type MassTime } from '$lib/api';
	import StatCard from '$lib/components/StatCard.svelte';
	import QuickActions from '$lib/components/QuickActions.svelte';
	import RecentActivity from '$lib/components/RecentActivity.svelte';
	import SacramentTrendsChart from '$lib/components/SacramentTrendsChart.svelte';
	import { addToast } from '$lib/stores/toast';

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
		} catch (e) {
			error = e instanceof Error ? e.message : 'Failed to load dashboard data';
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
		} catch (e) {
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
			<h1 class="text-2xl font-bold text-gray-900">Dashboard</h1>
			<p class="text-gray-600 mt-1">Welcome to the Parish Database management system</p>
		</div>
		<div class="flex items-center gap-2">
			<div
				class="w-3 h-3 rounded-full {healthStatus === 'connected'
					? 'bg-green-500'
					: healthStatus === 'loading'
						? 'bg-yellow-500 animate-pulse'
						: 'bg-red-500'}"
			></div>
			<span class="text-sm text-gray-600">
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
			{#each Array(4) as _}
				<div class="bg-white rounded-lg shadow p-6 animate-pulse">
					<div class="flex items-center gap-4">
						<div class="p-3 rounded-full bg-gray-200 w-14 h-14"></div>
						<div class="space-y-2">
							<div class="h-8 bg-gray-200 rounded w-16"></div>
							<div class="h-4 bg-gray-200 rounded w-24"></div>
						</div>
					</div>
				</div>
			{/each}
		</div>
	{:else if error}
		<!-- Error State -->
		<div class="bg-red-50 border border-red-200 rounded-lg p-6">
			<div class="flex items-center gap-3">
				<svg
					class="w-6 h-6 text-red-600 flex-shrink-0"
					fill="none"
					stroke="currentColor"
					viewBox="0 0 24 24"
				>
					<path
						stroke-linecap="round"
						stroke-linejoin="round"
						stroke-width="2"
						d="M12 8v4m0 4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z"
					/>
				</svg>
				<div>
					<h3 class="text-red-800 font-medium">Failed to load dashboard</h3>
					<p class="text-red-600 text-sm">{error}</p>
				</div>
			</div>
			<button
				onclick={loadDashboard}
				class="mt-4 px-4 py-2 bg-red-600 text-white rounded-lg hover:bg-red-700 transition-colors"
			>
				Retry
			</button>
		</div>
	{:else if dashboardData}
		<!-- Statistics Cards -->
		<div class="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
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
		</div>

		<!-- Quick Entry: Sunday Attendance -->
		<div class="bg-white rounded-lg shadow p-6">
			<h3 class="text-lg font-medium text-gray-900 mb-4">Quick Entry: Sunday Attendance</h3>
			<form onsubmit={(e) => { e.preventDefault(); submitQuickEntry(); }} class="flex flex-wrap gap-4 items-end">
				<div>
					<label for="quick-date" class="block text-sm font-medium text-gray-700 mb-1">Date</label>
					<input
						type="date"
						id="quick-date"
						bind:value={quickEntryDate}
						class="px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
					/>
				</div>
				<div>
					<label for="quick-mass-time" class="block text-sm font-medium text-gray-700 mb-1">Mass Time</label>
					<select
						id="quick-mass-time"
						bind:value={quickEntryMassTime}
						class="px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
					>
						<option value="">All Masses</option>
						{#each massTimeOptions as massTime}
							<option value={massTime.time}>{massTime.name} ({massTime.time})</option>
						{/each}
					</select>
				</div>
				<div>
					<label for="quick-count" class="block text-sm font-medium text-gray-700 mb-1">Attendance Count</label>
					<input
						type="number"
						id="quick-count"
						bind:value={quickEntryCount}
						min="0"
						class="px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent w-32"
					/>
				</div>
				<button
					type="submit"
					disabled={quickEntrySubmitting}
					class="px-6 py-2 bg-green-600 text-white rounded-lg hover:bg-green-700 transition-colors disabled:opacity-50"
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
