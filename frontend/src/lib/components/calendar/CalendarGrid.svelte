<script lang="ts">
	import type { CalendarEvent } from '$lib/api';

	interface Props {
		events: CalendarEvent[];
		currentDate: Date;
		onEventClick?: (event: CalendarEvent) => void;
		onDateClick?: (date: string) => void;
	}

	let { events, currentDate, onEventClick, onDateClick }: Props = $props();

	const DAY_NAMES = ['Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat', 'Sun'];

	const MINISTRY_COLORS = [
		{ bg: 'bg-amber-100', text: 'text-amber-800', border: 'border-amber-200' },
		{ bg: 'bg-emerald-100', text: 'text-emerald-800', border: 'border-emerald-200' },
		{ bg: 'bg-blue-100', text: 'text-blue-800', border: 'border-blue-200' },
		{ bg: 'bg-rose-100', text: 'text-rose-800', border: 'border-rose-200' },
		{ bg: 'bg-violet-100', text: 'text-violet-800', border: 'border-violet-200' },
		{ bg: 'bg-cyan-100', text: 'text-cyan-800', border: 'border-cyan-200' },
		{ bg: 'bg-orange-100', text: 'text-orange-800', border: 'border-orange-200' },
		{ bg: 'bg-pink-100', text: 'text-pink-800', border: 'border-pink-200' }
	];

	function getMinistryColor(ministryId: number) {
		return MINISTRY_COLORS[ministryId % MINISTRY_COLORS.length];
	}

	function formatDateKey(date: Date): string {
		const y = date.getFullYear();
		const m = String(date.getMonth() + 1).padStart(2, '0');
		const d = String(date.getDate()).padStart(2, '0');
		return `${y}-${m}-${d}`;
	}

	function isToday(date: Date): boolean {
		const today = new Date();
		return (
			date.getDate() === today.getDate() &&
			date.getMonth() === today.getMonth() &&
			date.getFullYear() === today.getFullYear()
		);
	}

	function isPast(date: Date): boolean {
		const today = new Date();
		today.setHours(0, 0, 0, 0);
		const d = new Date(date);
		d.setHours(0, 0, 0, 0);
		return d < today;
	}

	interface CalendarDay {
		date: Date;
		dateKey: string;
		inCurrentMonth: boolean;
		events: CalendarEvent[];
	}

	const calendarDays = $derived.by(() => {
		const year = currentDate.getFullYear();
		const month = currentDate.getMonth();

		const firstDay = new Date(year, month, 1);
		let startOffset = firstDay.getDay() - 1;
		if (startOffset < 0) startOffset = 6;

		const eventMap = new Map<string, CalendarEvent[]>();
		for (const event of events) {
			const existing = eventMap.get(event.event_date) || [];
			existing.push(event);
			eventMap.set(event.event_date, existing);
		}

		const days: CalendarDay[] = [];
		const startDate = new Date(year, month, 1 - startOffset);

		for (let i = 0; i < 42; i++) {
			const d = new Date(startDate);
			d.setDate(startDate.getDate() + i);
			const dateKey = formatDateKey(d);
			days.push({
				date: d,
				dateKey,
				inCurrentMonth: d.getMonth() === month,
				events: eventMap.get(dateKey) || []
			});
		}

		return days;
	});

	const weeks = $derived.by(() => {
		const result: CalendarDay[][] = [];
		for (let i = 0; i < calendarDays.length; i += 7) {
			result.push(calendarDays.slice(i, i + 7));
		}
		return result;
	});

	const MAX_VISIBLE_EVENTS = 3;
</script>

<div class="bg-white rounded-lg border border-brand-border overflow-hidden">
	<!-- Day headers -->
	<div class="grid grid-cols-7 border-b border-brand-border">
		{#each DAY_NAMES as day}
			<div
				class="px-2 py-2 text-center text-xs font-semibold text-brand-text-secondary uppercase tracking-wider"
			>
				{day}
			</div>
		{/each}
	</div>

	<!-- Calendar grid -->
	{#each weeks as week, weekIdx}
		<div
			class="grid grid-cols-7 {weekIdx < weeks.length - 1 ? 'border-b border-brand-border' : ''}"
		>
			{#each week as day}
				<!-- svelte-ignore a11y_no_static_element_interactions -->
				<div
					class="min-h-[100px] md:min-h-[120px] p-1.5 text-left border-r border-brand-border last:border-r-0
						{isPast(day.date) ? 'bg-brand-bg-subtle' : ''}
						hover:bg-brand-bg-subtle transition-colors cursor-pointer focus-visible:outline-none
						focus-visible:ring-2 focus-visible:ring-brand-accent focus-visible:ring-inset"
					role="button"
					tabindex="0"
					onclick={() => onDateClick?.(day.dateKey)}
					onkeydown={(e) => {
						if (e.key === 'Enter' || e.key === ' ') {
							e.preventDefault();
							onDateClick?.(day.dateKey);
						}
					}}
				>
					<!-- Date number -->
					<div class="flex items-center justify-between mb-1">
						<span
							class="inline-flex items-center justify-center w-7 h-7 text-sm rounded-full
								{isToday(day.date)
								? 'bg-brand-accent text-white font-semibold'
								: day.inCurrentMonth
									? 'text-brand-primary font-medium'
									: 'text-brand-text-muted'}"
						>
							{day.date.getDate()}
						</span>
					</div>

					<!-- Events -->
					<div class="space-y-0.5">
						{#each day.events.slice(0, MAX_VISIBLE_EVENTS) as event (event.id)}
							{@const color = getMinistryColor(event.ministry_id)}
							<button
								type="button"
								class="w-full text-left px-1.5 py-0.5 rounded text-xs truncate
									{color.bg} {color.text} border {color.border}
									hover:opacity-80 transition-opacity cursor-pointer"
								onclick={(e) => {
									e.stopPropagation();
									onEventClick?.(event);
								}}
								title="{event.title} — {event.ministry_name}"
							>
								{#if event.start_time}
									<span class="font-medium">{event.start_time}</span>
								{/if}
								{event.title}
							</button>
						{/each}
						{#if day.events.length > MAX_VISIBLE_EVENTS}
							<span class="text-xs text-brand-text-muted px-1.5">
								+{day.events.length - MAX_VISIBLE_EVENTS} more
							</span>
						{/if}
					</div>
				</div>
			{/each}
		</div>
	{/each}
</div>
