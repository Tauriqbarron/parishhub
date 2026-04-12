<script lang="ts">
	import { onMount, onDestroy } from 'svelte';
	import {
		Chart,
		LineController,
		CategoryScale,
		LinearScale,
		PointElement,
		LineElement,
		Tooltip,
		Legend,
		Filler
	} from 'chart.js';

	Chart.register(
		LineController,
		CategoryScale,
		LinearScale,
		PointElement,
		LineElement,
		Tooltip,
		Legend,
		Filler
	);

	interface Props {
		labels: string[];
		datasets: Array<{
			label: string;
			data: number[];
			borderColor?: string;
			fill?: boolean;
		}>;
		title?: string;
	}

	let { labels, datasets, title }: Props = $props();

	let canvas: HTMLCanvasElement;
	let chart: Chart | null = null;

	onMount(() => {
		chart = new Chart(canvas, {
			type: 'line',
			data: {
				labels,
				datasets: datasets.map((ds, i) => ({
					label: ds.label,
					data: ds.data,
					borderColor:
						ds.borderColor || ['#D97706', '#059669', '#8B5CF6', '#EC4899', '#F59E0B'][i % 5],
					backgroundColor: ds.fill
						? `${ds.borderColor || ['#D97706', '#059669', '#8B5CF6', '#EC4899', '#F59E0B'][i % 5]}20`
						: undefined,
					fill: ds.fill ?? false,
					tension: 0.3
				}))
			},
			options: {
				responsive: true,
				maintainAspectRatio: false,
				plugins: {
					legend: {
						display: datasets.length > 1,
						position: 'top'
					}
				},
				scales: {
					y: {
						beginAtZero: true
					}
				}
			}
		});
	});

	onDestroy(() => {
		if (chart) {
			chart.destroy();
		}
	});

	$effect(() => {
		if (chart) {
			chart.data.labels = labels;
			chart.data.datasets = datasets.map((ds, i) => ({
				label: ds.label,
				data: ds.data,
				borderColor:
					ds.borderColor || ['#D97706', '#059669', '#8B5CF6', '#EC4899', '#F59E0B'][i % 5],
				backgroundColor: ds.fill
					? `${ds.borderColor || ['#D97706', '#059669', '#8B5CF6', '#EC4899', '#F59E0B'][i % 5]}20`
					: undefined,
				fill: ds.fill ?? false,
				tension: 0.3
			}));
			chart.update();
		}
	});
</script>

<div class="bg-white rounded-lg shadow p-6">
	{#if title}
		<h3 class="text-lg font-medium text-brand-primary mb-4">{title}</h3>
	{/if}
	<div class="h-64">
		<canvas bind:this={canvas}></canvas>
	</div>
</div>
