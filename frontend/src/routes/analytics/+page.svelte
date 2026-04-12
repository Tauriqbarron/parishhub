<script lang="ts">
	import { onMount } from 'svelte';
	import {
		birthsApi,
		attendanceApi,
		populationApi,
		deathsApi,
		type BirthStatistics,
		type AttendanceTrendExtended,
		type PopulationGrowth,
		type DeathStatistics
	} from '$lib/api';
	import BarChart from '$lib/components/charts/BarChart.svelte';
	import LineChart from '$lib/components/charts/LineChart.svelte';
	import TrendCard from '$lib/components/charts/TrendCard.svelte';
	import { addToast } from '$lib/stores/toast';

	const COLORS = ['#D97706', '#059669', '#F59E0B', '#DC2626', '#8B5CF6', '#EC4899'];

	let activeTab: 'births' | 'attendance' | 'population' | 'deaths' = $state('births');
	let attendanceView: 'total' | 'breakdown' = $state('total');
	let loading = $state(true);
	let error = $state<string | null>(null);

	let birthStats: BirthStatistics | null = $state(null);
	let attendanceStats: AttendanceTrendExtended | null = $state(null);
	let populationStats: PopulationGrowth | null = $state(null);
	let deathStats = $state<DeathStatistics | null>(null);

	// Attendance time period state
	type TimePeriod = '1M' | '3M' | '6M' | 'YTD' | '1Y' | '3Y' | 'custom';
	let attendancePeriod: TimePeriod = $state('1M');
	let customStartDate = $state('');
	let customEndDate = $state('');
	/* eslint-disable svelte/prefer-svelte-reactivity -- local utility, not reactive state */
	function getDateRange(period: TimePeriod): { start: string; end: string } {
		const today = new Date();
		const end = today.toISOString().split('T')[0];
		let start: Date;

		switch (period) {
			case '1M':
				start = new Date(today);
				start.setMonth(start.getMonth() - 1);
				break;
			case '3M':
				start = new Date(today);
				start.setMonth(start.getMonth() - 3);
				break;
			case '6M':
				start = new Date(today);
				start.setMonth(start.getMonth() - 6);
				break;
			case 'YTD':
				start = new Date(today.getFullYear(), 0, 1);
				break;
			case '1Y':
				start = new Date(today);
				start.setFullYear(start.getFullYear() - 1);
				break;
			case '3Y':
				start = new Date(today);
				start.setFullYear(start.getFullYear() - 3);
				break;
			case 'custom':
				return { start: customStartDate, end: customEndDate || end };
			default:
				start = new Date(today);
				start.setMonth(start.getMonth() - 1);
		}
		return { start: start.toISOString().split('T')[0], end };
	}
	/* eslint-enable svelte/prefer-svelte-reactivity */

	async function loadAttendanceStats() {
		loading = true;
		try {
			const { start, end } = getDateRange(attendancePeriod);
			const includeBreakdown = attendanceView === 'breakdown';
			attendanceStats = (await attendanceApi.getStatistics(
				includeBreakdown,
				start,
				end
			)) as AttendanceTrendExtended;
		} catch {
			addToast('Failed to load attendance statistics', 'error');
		} finally {
			loading = false;
		}
	}

	onMount(async () => {
		await loadAllStats();
	});

	async function loadAllStats() {
		loading = true;
		error = null;
		try {
			const { start, end } = getDateRange(attendancePeriod);
			const [births, attendance, population, deaths] = await Promise.all([
				birthsApi.getStatistics(),
				attendanceApi.getStatistics(attendanceView === 'breakdown', start, end),
				populationApi.getStatistics(),
				deathsApi.getStatistics()
			]);
			birthStats = births;
			attendanceStats = attendance as AttendanceTrendExtended;
			populationStats = population;
			deathStats = deaths;
		} catch (err) {
			error = err instanceof Error ? err.message : 'Failed to load statistics';
			addToast('Failed to load statistics', 'error');
		} finally {
			loading = false;
		}
	}

	// Derived chart data
	let birthChartLabels = $derived(
		(birthStats as BirthStatistics | null)?.by_year?.map((y) => String(y.year)).reverse() ?? []
	);
	let birthChartData = $derived(
		(birthStats as BirthStatistics | null)?.by_year?.map((y) => y.count).reverse() ?? []
	);

	let attendanceChartLabels = $derived(
		(attendanceStats as AttendanceTrendExtended | null)?.recent_weeks?.map((w) => w.date) ?? []
	);
	let attendanceChartData = $derived(
		(attendanceStats as AttendanceTrendExtended | null)?.recent_weeks?.map((w) => w.count) ?? []
	);

	let populationChartLabels = $derived(
		(populationStats as PopulationGrowth | null)?.history?.map((s) => s.date).reverse() ?? []
	);
	let populationChartData = $derived(
		(populationStats as PopulationGrowth | null)?.history
			?.map((s) => s.registered_members)
			.reverse() ?? []
	);

	let deathChartLabels = $derived(
		(deathStats as DeathStatistics | null)?.by_year?.map((y) => String(y.year)).reverse() ?? []
	);
	let deathChartData = $derived(
		(deathStats as DeathStatistics | null)?.by_year?.map((y) => y.count).reverse() ?? []
	);

	// Current year births
	let birthsThisYear = $derived(
		(birthStats as BirthStatistics | null)?.by_year?.find(
			(y) => y.year === (birthStats as BirthStatistics | null)?.current_year
		)?.count ?? 0
	);

	// Current year deaths
	let deathsThisYear = $derived(deathStats?.current_year_count ?? 0);
</script>

<svelte:head>
	<title>Analytics - Parish Database</title>
</svelte:head>

<div class="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
	<div class="flex justify-between items-center mb-8">
		<h1 class="text-2xl font-bold text-brand-primary">Parish Analytics</h1>
	</div>

	{#if loading}
		<div class="flex items-center justify-center h-64">
			<div class="animate-spin rounded-full h-12 w-12 border-b-2 border-brand-accent"></div>
		</div>
	{:else if error}
		<div
			class="bg-brand-error/10 border border-brand-error/20 rounded-lg p-6"
			role="alert"
			aria-live="assertive"
		>
			<div class="flex items-center gap-3">
				<svg
					class="w-6 h-6 text-brand-error flex-shrink-0"
					fill="none"
					stroke="currentColor"
					viewBox="0 0 24 24"
					aria-hidden="true"
					role="img"
				>
					<path
						stroke-linecap="round"
						stroke-linejoin="round"
						stroke-width="2"
						d="M12 8v4m0 4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z"
					/>
				</svg>
				<div>
					<h3 class="text-brand-error font-medium">Failed to load analytics</h3>
					<p class="text-brand-error text-sm">{error}</p>
				</div>
			</div>
			<button
				onclick={loadAllStats}
				class="mt-4 px-4 py-2 bg-brand-error text-white rounded-lg hover:bg-brand-error/90 transition-colors focus:outline-none focus:ring-2 focus:ring-brand-error focus:ring-offset-2"
				aria-label="Retry loading analytics"
			>
				Retry
			</button>
		</div>
	{:else}
		<!-- Key Metrics Cards -->
		<div class="grid grid-cols-1 md:grid-cols-4 gap-6 mb-8">
			<TrendCard
				value={birthsThisYear}
				label="Births This Year"
				trend={null}
				trendLabel="Recorded births in {birthStats?.current_year}"
			/>
			<TrendCard
				value={deathsThisYear}
				label="Deaths This Year"
				trend={null}
				trendLabel="Recorded deaths in {new Date().getFullYear()}"
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
			<div class="border-b border-brand-border">
				<nav class="flex -mb-px">
					<button
						class="px-6 py-4 text-sm font-medium border-b-2 transition-colors {activeTab ===
						'births'
							? 'border-brand-accent text-brand-accent'
							: 'border-transparent text-brand-text-muted hover:text-brand-text-secondary hover:border-brand-border'}"
						onclick={() => (activeTab = 'births')}
					>
						Births
					</button>
					<button
						class="px-6 py-4 text-sm font-medium border-b-2 transition-colors {activeTab ===
						'deaths'
							? 'border-brand-error text-brand-error'
							: 'border-transparent text-brand-text-muted hover:text-brand-text-secondary hover:border-brand-border'}"
						onclick={() => (activeTab = 'deaths')}
					>
						Deaths
					</button>
					<button
						class="px-6 py-4 text-sm font-medium border-b-2 transition-colors {activeTab ===
						'attendance'
							? 'border-brand-accent text-brand-accent'
							: 'border-transparent text-brand-text-muted hover:text-brand-text-secondary hover:border-brand-border'}"
						onclick={() => (activeTab = 'attendance')}
					>
						Attendance
					</button>
					<button
						class="px-6 py-4 text-sm font-medium border-b-2 transition-colors {activeTab ===
						'population'
							? 'border-brand-accent text-brand-accent'
							: 'border-transparent text-brand-text-muted hover:text-brand-text-secondary hover:border-brand-border'}"
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
							datasets={[{ label: 'Births', data: birthChartData, backgroundColor: '#D97706' }]}
							title="Births by Year"
						/>
					{:else}
						<p class="text-brand-text-muted text-center py-8">No birth data available</p>
					{/if}
				{:else if activeTab === 'deaths'}
					{#if deathChartLabels.length > 0}
						<BarChart
							labels={deathChartLabels}
							datasets={[{ label: 'Deaths', data: deathChartData, backgroundColor: '#DC2626' }]}
							title="Deaths by Year"
						/>
					{:else}
						<p class="text-brand-text-muted text-center py-8">No death data available</p>
					{/if}
				{:else if activeTab === 'attendance'}
					<!-- Sub-tabs for Total vs Breakdown -->
					<div class="flex gap-2 mb-4">
						<button
							class="px-3 py-1 text-sm rounded {attendanceView === 'total'
								? 'bg-brand-accent/10 text-brand-accent'
								: 'text-brand-text-secondary hover:bg-brand-bg-muted'}"
							onclick={() => (attendanceView = 'total')}
						>
							Total
						</button>
						<button
							class="px-3 py-1 text-sm rounded {attendanceView === 'breakdown'
								? 'bg-brand-accent/10 text-brand-accent'
								: 'text-brand-text-secondary hover:bg-brand-bg-muted'}"
							onclick={() => (attendanceView = 'breakdown')}
						>
							By Mass Time
						</button>
					</div>

					<!-- Time Period Selector -->
					<div class="flex flex-wrap items-center gap-2 mb-4">
						{#each ['1M', '3M', '6M', 'YTD', '1Y', '3Y'] as period}
							<button
								class="px-3 py-1 text-xs font-medium rounded-full border transition-colors
									{attendancePeriod === period
									? 'bg-brand-success/10 text-brand-success border-brand-success/30'
									: 'bg-white text-brand-text-secondary border-brand-border hover:bg-brand-bg-subtle'}"
								onclick={() => {
									attendancePeriod = period as TimePeriod;
									loadAttendanceStats();
								}}
							>
								{period}
							</button>
						{/each}
						<button
							class="px-3 py-1 text-xs font-medium rounded-full border transition-colors
								{attendancePeriod === 'custom'
								? 'bg-brand-success/10 text-brand-success border-brand-success/30'
								: 'bg-white text-brand-text-secondary border-brand-border hover:bg-brand-bg-subtle'}"
							onclick={() => {
								attendancePeriod = 'custom';
							}}
						>
							Custom
						</button>
					</div>

					{#if attendancePeriod === 'custom'}
						<div class="flex items-center gap-3 mb-4">
							<input
								type="date"
								bind:value={customStartDate}
								class="px-3 py-1.5 text-sm border border-brand-border rounded-md focus:ring-2 focus:ring-brand-accent focus:border-brand-accent"
							/>
							<span class="text-brand-text-muted text-sm">to</span>
							<input
								type="date"
								bind:value={customEndDate}
								class="px-3 py-1.5 text-sm border border-brand-border rounded-md focus:ring-2 focus:ring-brand-accent focus:border-brand-accent"
							/>
							<button
								onclick={loadAttendanceStats}
								class="px-4 py-1.5 text-sm bg-brand-accent text-white rounded-md hover:bg-brand-accent/90 transition-colors"
							>
								Apply
							</button>
						</div>
					{/if}

					{#if attendanceView === 'total'}
						{#if attendanceChartLabels.length > 0}
							<LineChart
								labels={attendanceChartLabels}
								datasets={[
									{
										label: 'Attendance',
										data: attendanceChartData,
										borderColor: '#059669',
										fill: true
									}
								]}
								title="Recent Mass Attendance"
							/>
						{:else}
							<p class="text-brand-text-muted text-center py-8">No attendance data available</p>
						{/if}
					{:else if attendanceStats?.by_mass_time?.length}
						<LineChart
							labels={attendanceStats.by_mass_time[0]?.recent_weeks.map((w) => w.date).reverse() ??
								[]}
							datasets={attendanceStats.by_mass_time.map((mt, i) => ({
								label: mt.mass_time,
								data: mt.recent_weeks.map((w) => w.count).reverse(),
								borderColor: COLORS[i % COLORS.length],
								fill: false
							}))}
							title="Attendance by Mass Time"
						/>

						<table class="w-full mt-4 text-sm">
							<thead>
								<tr class="border-b">
									<th class="text-left py-2">Mass Time</th>
									<th class="text-right py-2">Weekly Avg</th>
									<th class="text-right py-2">Total (4 wks)</th>
								</tr>
							</thead>
							<tbody>
								{#each attendanceStats.by_mass_time as mt}
									<tr class="border-b">
										<td class="py-2">{mt.mass_time}</td>
										<td class="text-right">{mt.weekly_average.toFixed(0)}</td>
										<td class="text-right">{mt.total_attendance}</td>
									</tr>
								{/each}
							</tbody>
						</table>
					{:else}
						<p class="text-brand-text-muted text-center py-8">No breakdown data available</p>
					{/if}
				{:else if activeTab === 'population'}
					{#if populationChartLabels.length > 0}
						<LineChart
							labels={populationChartLabels}
							datasets={[
								{ label: 'Members', data: populationChartData, borderColor: '#D97706', fill: true }
							]}
							title="Population Over Time"
						/>
					{:else}
						<div class="text-center py-8">
							<div class="grid grid-cols-2 gap-4 max-w-md mx-auto mb-4">
								<div class="bg-brand-accent/10 rounded-lg p-4">
									<p class="text-3xl font-bold text-brand-accent">
										{populationStats?.current_members ?? 0}
									</p>
									<p class="text-sm text-brand-text-secondary">Registered Members</p>
								</div>
								<div class="bg-brand-accent/10 rounded-lg p-4">
									<p class="text-3xl font-bold text-brand-accent">
										{populationStats?.current_households ?? 0}
									</p>
									<p class="text-sm text-brand-text-secondary">Households</p>
								</div>
							</div>
							<p class="text-brand-text-muted text-sm">
								No historical data yet. Population snapshots will appear here over time.
							</p>
						</div>
					{/if}
				{/if}
			</div>
		</div>
	{/if}
</div>
