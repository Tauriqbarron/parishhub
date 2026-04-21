<script lang="ts">
	import { ChevronLeft, ChevronRight, Calendar as CalendarIcon } from 'lucide-svelte';
	import { calendarApi, ministryApi, type CalendarEvent, type Ministry } from '$lib/api';
	import Breadcrumbs from '$lib/components/Breadcrumbs.svelte';
	import PageHeader from '$lib/components/PageHeader.svelte';
	import CalendarGrid from '$lib/components/calendar/CalendarGrid.svelte';
	import EventDetailModal from '$lib/components/calendar/EventDetailModal.svelte';

	let currentDate = $state(new Date());
	let activeView = $state<'month' | 'week' | 'day'>('month');
	let events = $state<CalendarEvent[]>([]);
	let loading = $state(false);
	let selectedMinistryId = $state<number | undefined>(undefined);
	let selectedEvent = $state<CalendarEvent | null>(null);
	let ministries = $state<Ministry[]>([]);

	// Date range helpers
	function getMonthRange(date: Date): { date_from: string; date_to: string } {
		const year = date.getFullYear();
		const month = date.getMonth();
		// Include leading/trailing days for grid overflow
		const firstDay = new Date(year, month, 1);
		let startOffset = firstDay.getDay() - 1;
		if (startOffset < 0) startOffset = 6;
		const start = new Date(year, month, 1 - startOffset);
		const end = new Date(start);
		end.setDate(start.getDate() + 41); // 6 weeks
		return {
			date_from: formatDateKey(start),
			date_to: formatDateKey(end)
		};
	}

	function getWeekRange(date: Date): { date_from: string; date_to: string } {
		const d = new Date(date);
		let dayOfWeek = d.getDay() - 1;
		if (dayOfWeek < 0) dayOfWeek = 6;
		const start = new Date(d);
		start.setDate(d.getDate() - dayOfWeek);
		const end = new Date(start);
		end.setDate(start.getDate() + 6);
		return {
			date_from: formatDateKey(start),
			date_to: formatDateKey(end)
		};
	}

	function formatDateKey(date: Date): string {
		const y = date.getFullYear();
		const m = String(date.getMonth() + 1).padStart(2, '0');
		const d = String(date.getDate()).padStart(2, '0');
		return `${y}-${m}-${d}`;
	}

	// Formatted period label
	const formattedPeriod = $derived.by(() => {
		if (activeView === 'month') {
			return currentDate.toLocaleDateString('en-NZ', { month: 'long', year: 'numeric' });
		}
		if (activeView === 'week') {
			const { date_from, date_to } = getWeekRange(currentDate);
			const from = new Date(date_from + 'T00:00:00');
			const to = new Date(date_to + 'T00:00:00');
			return `${from.toLocaleDateString('en-NZ', { month: 'short', day: 'numeric' })} – ${to.toLocaleDateString('en-NZ', { month: 'short', day: 'numeric', year: 'numeric' })}`;
		}
		return currentDate.toLocaleDateString('en-NZ', {
			weekday: 'long',
			month: 'long',
			day: 'numeric',
			year: 'numeric'
		});
	});

	async function loadEvents() {
		loading = true;
		try {
			const range =
				activeView === 'month'
					? getMonthRange(currentDate)
					: activeView === 'week'
						? getWeekRange(currentDate)
						: { date_from: formatDateKey(currentDate), date_to: formatDateKey(currentDate) };

			events = await calendarApi.listEvents({
				...range,
				ministry_id: selectedMinistryId
			});
		} catch {
			events = [];
		} finally {
			loading = false;
		}
	}

	async function loadMinistries() {
		try {
			const response = await ministryApi.list({ is_active: true, per_page: 100 });
			ministries = response.items;
		} catch {
			ministries = [];
		}
	}

	$effect(() => {
		loadMinistries();
	});

	// Re-fetch when view, date, or filter changes
	$effect(() => {
		// Track reactive dependencies
		const _ = currentDate.getTime();
		const __ = activeView;
		const ___ = selectedMinistryId;
		loadEvents();
	});

	function prevPeriod() {
		const d = new Date(currentDate);
		if (activeView === 'month') d.setMonth(d.getMonth() - 1);
		else if (activeView === 'week') d.setDate(d.getDate() - 7);
		else d.setDate(d.getDate() - 1);
		currentDate = d;
	}

	function nextPeriod() {
		const d = new Date(currentDate);
		if (activeView === 'month') d.setMonth(d.getMonth() + 1);
		else if (activeView === 'week') d.setDate(d.getDate() + 7);
		else d.setDate(d.getDate() + 1);
		currentDate = d;
	}

	function goToToday() {
		currentDate = new Date();
	}

	function handleEventClick(event: CalendarEvent) {
		selectedEvent = event;
	}

	function handleDateClick(dateKey: string) {
		currentDate = new Date(dateKey + 'T00:00:00');
		activeView = 'day';
	}

	function handleMinistryFilter(e: Event) {
		const value = (e.target as HTMLSelectElement).value;
		selectedMinistryId = value ? Number(value) : undefined;
	}
</script>

<div>
	<Breadcrumbs />
	<PageHeader title="Calendar" subtitle="View all parish events across ministries" />

	<!-- Controls bar -->
	<div class="flex flex-col sm:flex-row items-start sm:items-center justify-between gap-3 mb-6">
		<!-- Navigation -->
		<div class="flex items-center gap-2">
			<button
				onclick={prevPeriod}
				class="p-2 rounded-sm text-brand-text-secondary hover:text-brand-primary hover:bg-brand-bg-muted transition-colors"
				aria-label="Previous"
			>
				<ChevronLeft class="w-5 h-5" />
			</button>
			<button
				onclick={goToToday}
				class="px-3 py-1.5 text-sm font-medium rounded-sm border border-brand-border text-brand-text-secondary hover:text-brand-primary hover:border-brand-accent transition-colors"
			>
				Today
			</button>
			<button
				onclick={nextPeriod}
				class="p-2 rounded-sm text-brand-text-secondary hover:text-brand-primary hover:bg-brand-bg-muted transition-colors"
				aria-label="Next"
			>
				<ChevronRight class="w-5 h-5" />
			</button>
			<h2 class="text-lg font-semibold text-brand-primary ml-2">{formattedPeriod}</h2>
		</div>

		<!-- View toggle + filter -->
		<div class="flex items-center gap-3">
			<!-- Ministry filter -->
			<select
				onchange={handleMinistryFilter}
				class="text-sm border border-brand-border rounded-sm px-2 py-1.5 bg-white text-brand-primary focus:ring-2 focus:ring-brand-accent focus:border-transparent"
			>
				<option value="">All Ministries</option>
				{#each ministries as m (m.id)}
					<option value={m.id}>{m.name}</option>
				{/each}
			</select>

			<!-- View toggle -->
			<div class="flex items-center gap-0.5 bg-brand-bg-muted rounded-sm p-0.5">
				{#each ['month', 'week', 'day'] as view}
					<button
						onclick={() => (activeView = view as 'month' | 'week' | 'day')}
						class="px-3 py-1.5 text-sm font-medium rounded-sm transition-colors capitalize
							{activeView === view
								? 'bg-white text-brand-primary shadow-sm'
								: 'text-brand-text-secondary hover:text-brand-primary'}"
					>
						{view}
					</button>
				{/each}
			</div>
		</div>
	</div>

	<!-- Calendar content -->
	{#if loading}
		<div class="bg-white rounded-lg border border-brand-border p-8">
			<div class="animate-pulse space-y-4">
				<div class="grid grid-cols-7 gap-2">
					{#each Array(7) as _}
						<div class="h-4 bg-brand-bg-muted rounded"></div>
					{/each}
				</div>
				{#each Array(6) as _}
					<div class="grid grid-cols-7 gap-2">
						{#each Array(7) as _}
							<div class="h-24 bg-brand-bg-muted rounded"></div>
						{/each}
					</div>
				{/each}
			</div>
		</div>
	{:else if activeView === 'month'}
		<CalendarGrid {events} {currentDate} onEventClick={handleEventClick} onDateClick={handleDateClick} />
	{:else if activeView === 'week'}
		{@const weekEvents = events}
		<div class="bg-white rounded-lg border border-brand-border overflow-hidden">
			<div class="divide-y divide-brand-border">
				{#each (() => {
					const { date_from } = getWeekRange(currentDate);
					const start = new Date(date_from + 'T00:00:00');
					return Array.from({ length: 7 }, (_, i) => {
						const d = new Date(start);
						d.setDate(start.getDate() + i);
						return d;
					});
				})() as day}
					{@const dateKey = formatDateKey(day)}
					{@const dayEvents = weekEvents.filter((e) => e.event_date === dateKey)}
					<div class="p-4">
						<div class="flex items-center gap-3 mb-2">
							<span class="text-sm font-semibold text-brand-primary">
								{day.toLocaleDateString('en-NZ', { weekday: 'short', month: 'short', day: 'numeric' })}
							</span>
							{#if dayEvents.length === 0}
								<span class="text-xs text-brand-text-muted">No events</span>
							{/if}
						</div>
						{#each dayEvents as event (event.id)}
							<button
								onclick={() => handleEventClick(event)}
								class="w-full text-left px-3 py-2 rounded-sm hover:bg-brand-bg-subtle transition-colors mb-1 border border-brand-border"
							>
								<div class="flex items-center justify-between">
									<span class="text-sm font-medium text-brand-primary">{event.title}</span>
									<span class="text-xs text-brand-text-muted">{event.start_time || ''}</span>
								</div>
								<span class="text-xs text-brand-accent">{event.ministry_name}</span>
							</button>
						{/each}
					</div>
				{/each}
			</div>
		</div>
	{:else}
		{@const dayKey = formatDateKey(currentDate)}
		{@const dayEvents = events.filter((e) => e.event_date === dayKey)}
		<div class="bg-white rounded-lg border border-brand-border overflow-hidden">
			{#if dayEvents.length === 0}
				<div class="p-8 text-center">
					<CalendarIcon class="mx-auto h-10 w-10 text-brand-text-muted" />
					<p class="mt-2 text-sm text-brand-text-secondary">No events on this day</p>
				</div>
			{:else}
				<div class="divide-y divide-brand-border">
					{#each dayEvents as event (event.id)}
						<button
							onclick={() => handleEventClick(event)}
							class="w-full text-left px-6 py-4 hover:bg-brand-bg-subtle transition-colors"
						>
							<div class="flex items-center justify-between">
								<div>
									<h3 class="text-sm font-medium text-brand-primary">{event.title}</h3>
									<p class="text-xs text-brand-accent mt-0.5">{event.ministry_name}</p>
									{#if event.location}
										<p class="text-xs text-brand-text-muted mt-0.5">{event.location}</p>
									{/if}
								</div>
								<div class="text-right">
									{#if event.start_time}
										<span class="text-sm text-brand-text-secondary">{event.start_time}</span>
										{#if event.end_time}
											<span class="text-xs text-brand-text-muted"> – {event.end_time}</span>
										{/if}
									{/if}
								</div>
							</div>
						</button>
					{/each}
				</div>
			{/if}
		</div>
	{/if}

	<!-- Event detail modal -->
	{#if selectedEvent}
		<EventDetailModal event={selectedEvent} onClose={() => (selectedEvent = null)} />
	{/if}
</div>
