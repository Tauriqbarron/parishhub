<script lang="ts">
	import { onMount, onDestroy } from 'svelte';
	import {
		Chart,
		BarController,
		CategoryScale,
		LinearScale,
		BarElement,
		Tooltip,
		Legend
	} from 'chart.js';

	Chart.register(BarController, CategoryScale, LinearScale, BarElement, Tooltip, Legend);

	interface Props {
		labels: string[];
		datasets: Array<{
			label: string;
			data: number[];
			backgroundColor?: string;
		}>;
		title?: string;
	}

	let { labels, datasets, title }: Props = $props();

	let canvas: HTMLCanvasElement;
	let chart: Chart | null = null;

	onMount(() => {
		chart = new Chart(canvas, {
			type: 'bar',
			data: {
				labels,
				datasets: datasets.map((ds, i) => ({
					label: ds.label,
					data: ds.data,
					backgroundColor:
						ds.backgroundColor || ['#3B82F6', '#10B981', '#8B5CF6', '#EC4899', '#F59E0B'][i % 5]
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
				backgroundColor:
					ds.backgroundColor || ['#3B82F6', '#10B981', '#8B5CF6', '#EC4899', '#F59E0B'][i % 5]
			}));
			chart.update();
		}
	});
</script>

<div class="bg-white rounded-lg shadow p-6">
	{#if title}
		<h3 class="text-lg font-medium text-gray-900 mb-4">{title}</h3>
	{/if}
	<div class="h-64">
		<canvas bind:this={canvas}></canvas>
	</div>
</div>
