<script lang="ts">
	import { onMount } from 'svelte';
	import {
		birthsApi,
		attendanceApi,
		populationApi,
		type BirthStatistics,
		type AttendanceTrend,
		type PopulationGrowth,
		type MassAttendanceCreate
	} from '$lib/api';
	import BarChart from '$lib/components/charts/BarChart.svelte';
	import LineChart from '$lib/components/charts/LineChart.svelte';
	import TrendCard from '$lib/components/charts/TrendCard.svelte';
	import { addToast } from '$lib/stores/toast';

	let activeTab: 'births' | 'attendance' | 'population' = $state('births');
	let loading = $state(true);

	let birthStats: BirthStatistics | null = $state(null);
	let attendanceStats: AttendanceTrend | null = $state(null);
	let populationStats: PopulationGrowth | null = $state(null);

	// Quick entry form state
	let quickEntryDate = $state('');
	let quickEntryCount = $state(0);
	let quickEntrySubmitting = $state(false);

	onMount(async () => {
		// Set default date to previous Sunday
		const today = new Date();
		const dayOfWeek = today.getDay();
		const previousSunday = new Date(today);
		previousSunday.setDate(today.getDate() - dayOfWeek - (dayOfWeek === 0 ? 7 : 0));
		quickEntryDate = previousSunday.toISOString().split('T')[0];

		await loadAllStats();
	});

	async function loadAllStats() {
		loading = true;
		try {
			const [births, attendance, population] = await Promise.all([
				birthsApi.getStatistics(),
				attendanceApi.getStatistics(),
				populationApi.getStatistics()
			]);
			birthStats = births;
			attendanceStats = attendance;
			populationStats = population;
		} catch (e) {
			addToast('Failed to load statistics', 'error');
		} finally {
			loading = false;
		}
	}

	async function submitQuickEntry() {
		if (!quickEntryDate || quickEntryCount <= 0) {
			addToast('Please enter a valid date and attendance count', 'error');
			return;
		}

		quickEntrySubmitting = true;
		try {
			const data: MassAttendanceCreate = {
				date: quickEntryDate,
				attendance_count: quickEntryCount
			};
			await attendanceApi.create(data);
			addToast('Attendance recorded successfully', 'success');
			quickEntryCount = 0;
			// Refresh attendance stats
			attendanceStats = await attendanceApi.getStatistics();
		} catch (e) {
			addToast('Failed to record attendance', 'error');
		} finally {
			quickEntrySubmitting = false;
		}
	}

	// Derived chart data
	let birthChartLabels = $derived(birthStats?.by_year.map((y) => String(y.year)).reverse() ?? []);
	let birthChartData = $derived(birthStats?.by_year.map((y) => y.count).reverse() ?? []);

	let attendanceChartLabels = $derived(
		attendanceStats?.recent_weeks.map((w) => w.date).reverse() ?? []
	);
	let attendanceChartData = $derived(
		attendanceStats?.recent_weeks.map((w) => w.count).reverse() ?? []
	);

	let populationChartLabels = $derived(
		populationStats?.history.map((s) => s.date).reverse() ?? []
	);
	let populationChartData = $derived(
		populationStats?.history.map((s) => s.registered_members).reverse() ?? []
	);

	// Current year births
	let birthsThisYear = $derived(
		birthStats?.by_year.find((y) => y.year === birthStats?.current_year)?.count ?? 0
	);
</script>

<svelte:head>
	<title>Analytics - Parish Database</title>
</svelte:head>

<div class="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
	<div class="flex justify-between items-center mb-8">
		<h1 class="text-2xl font-bold text-gray-900">Parish Analytics</h1>
		<div class="flex gap-2">
			<a
				href="/analytics/births/new"
				class="px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition-colors"
			>
				Record Birth
			</a>
			<a
				href="/analytics/attendance/new"
				class="px-4 py-2 bg-green-600 text-white rounded-lg hover:bg-green-700 transition-colors"
			>
				Record Attendance
			</a>
		</div>
	</div>

	{#if loading}
		<div class="flex items-center justify-center h-64">
			<div class="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600"></div>
		</div>
	{:else}
		<!-- Key Metrics Cards -->
		<div class="grid grid-cols-1 md:grid-cols-3 gap-6 mb-8">
			<TrendCard
				value={birthsThisYear}
				label="Births This Year"
				trend={null}
				trendLabel="Recorded births in {birthStats?.current_year}"
			/>
			<TrendCard
				value={attendanceStats?.weekly_average.toFixed(0) ?? '0'}
				label="Avg Weekly Attendance"
				trend={attendanceStats?.yoy_change_percent}
				trendLabel="Year over year change"
			/>
			<TrendCard
				value={populationStats?.current_members ?? 0}
				label="Total Registered Members"
				trend={populationStats?.growth_percent}
				trendLabel="Overall growth"
			/>
		</div>

		<!-- Tabbed Charts -->
		<div class="bg-white rounded-lg shadow mb-8">
			<div class="border-b border-gray-200">
				<nav class="flex -mb-px">
					<button
						class="px-6 py-4 text-sm font-medium border-b-2 transition-colors {activeTab === 'births'
							? 'border-blue-500 text-blue-600'
							: 'border-transparent text-gray-500 hover:text-gray-700 hover:border-gray-300'}"
						onclick={() => (activeTab = 'births')}
					>
						Births
					</button>
					<button
						class="px-6 py-4 text-sm font-medium border-b-2 transition-colors {activeTab === 'attendance'
							? 'border-blue-500 text-blue-600'
							: 'border-transparent text-gray-500 hover:text-gray-700 hover:border-gray-300'}"
						onclick={() => (activeTab = 'attendance')}
					>
						Attendance
					</button>
					<button
						class="px-6 py-4 text-sm font-medium border-b-2 transition-colors {activeTab === 'population'
							? 'border-blue-500 text-blue-600'
							: 'border-transparent text-gray-500 hover:text-gray-700 hover:border-gray-300'}"
						onclick={() => (activeTab = 'population')}
					>
						Population
					</button>
				</nav>
			</div>

			<div class="p-6">
				{#if activeTab === 'births'}
					{#if birthChartLabels.length > 0}
						<BarChart
							labels={birthChartLabels}
							datasets={[{ label: 'Births', data: birthChartData, backgroundColor: '#3B82F6' }]}
							title="Births by Year"
						/>
					{:else}
						<p class="text-gray-500 text-center py-8">No birth data available</p>
					{/if}
				{:else if activeTab === 'attendance'}
					{#if attendanceChartLabels.length > 0}
						<LineChart
							labels={attendanceChartLabels}
							datasets={[{ label: 'Attendance', data: attendanceChartData, borderColor: '#10B981', fill: true }]}
							title="Recent Mass Attendance"
						/>
					{:else}
						<p class="text-gray-500 text-center py-8">No attendance data available</p>
					{/if}
				{:else if activeTab === 'population'}
					{#if populationChartLabels.length > 0}
						<LineChart
							labels={populationChartLabels}
							datasets={[{ label: 'Members', data: populationChartData, borderColor: '#8B5CF6', fill: true }]}
							title="Population Over Time"
						/>
					{:else}
						<p class="text-gray-500 text-center py-8">No population data available</p>
					{/if}
				{/if}
			</div>
		</div>

		<!-- Quick Entry Widget -->
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
	{/if}
</div>
