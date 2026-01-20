<script lang="ts">
	import { onMount } from 'svelte';
	import {
		birthsApi,
		attendanceApi,
		populationApi,
		type BirthStatistics,
		type AttendanceTrend,
		type PopulationGrowth
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

	onMount(async () => {
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
						<div class="text-center py-8">
							<div class="grid grid-cols-2 gap-4 max-w-md mx-auto mb-4">
								<div class="bg-purple-50 rounded-lg p-4">
									<p class="text-3xl font-bold text-purple-600">{populationStats?.current_members ?? 0}</p>
									<p class="text-sm text-gray-600">Registered Members</p>
								</div>
								<div class="bg-purple-50 rounded-lg p-4">
									<p class="text-3xl font-bold text-purple-600">{populationStats?.current_households ?? 0}</p>
									<p class="text-sm text-gray-600">Households</p>
								</div>
							</div>
							<p class="text-gray-500 text-sm">No historical data yet. Population snapshots will appear here over time.</p>
						</div>
					{/if}
				{/if}
			</div>
		</div>
	{/if}
</div>
