<script lang="ts">
	interface Props {
		page: number;
		pages: number;
		total: number;
		perPage: number;
		onPageChange: (page: number) => void;
	}

	let { page, pages, total, perPage, onPageChange }: Props = $props();

	const startItem = $derived((page - 1) * perPage + 1);
	const endItem = $derived(Math.min(page * perPage, total));

	function goToPage(newPage: number) {
		if (newPage >= 1 && newPage <= pages && newPage !== page) {
			onPageChange(newPage);
		}
	}

	const visiblePages = $derived(() => {
		const delta = 2;
		const range: number[] = [];
		const rangeWithDots: (number | string)[] = [];

		for (let i = Math.max(2, page - delta); i <= Math.min(pages - 1, page + delta); i++) {
			range.push(i);
		}

		if (page - delta > 2) {
			rangeWithDots.push(1, '...');
		} else {
			rangeWithDots.push(1);
		}

		rangeWithDots.push(...range);

		if (page + delta < pages - 1) {
			rangeWithDots.push('...', pages);
		} else if (pages > 1) {
			rangeWithDots.push(pages);
		}

		return rangeWithDots;
	});
</script>

{#if pages > 0}
	<div
		class="flex items-center justify-between border-t border-brand-border bg-white px-4 py-3 sm:px-6"
	>
		<div class="flex flex-1 justify-between sm:hidden">
			<button
				onclick={() => goToPage(page - 1)}
				disabled={page === 1}
				class="relative inline-flex items-center rounded-sm border border-brand-border bg-white px-4 py-2 text-sm font-medium text-brand-text-secondary hover:bg-brand-bg-muted disabled:opacity-50 disabled:cursor-not-allowed"
			>
				Previous
			</button>
			<button
				onclick={() => goToPage(page + 1)}
				disabled={page === pages}
				class="relative ml-3 inline-flex items-center rounded-sm border border-brand-border bg-white px-4 py-2 text-sm font-medium text-brand-text-secondary hover:bg-brand-bg-muted disabled:opacity-50 disabled:cursor-not-allowed"
			>
				Next
			</button>
		</div>
		<div class="hidden sm:flex sm:flex-1 sm:items-center sm:justify-between">
			<div>
				<p class="text-sm text-brand-text-secondary">
					Showing <span class="font-medium">{startItem}</span> to
					<span class="font-medium">{endItem}</span> of
					<span class="font-medium">{total}</span> results
				</p>
			</div>
			<div>
				<nav class="isolate inline-flex -space-x-px rounded-sm shadow-sm" aria-label="Pagination">
					<button
						onclick={() => goToPage(page - 1)}
						disabled={page === 1}
						class="relative inline-flex items-center rounded-l-md px-2 py-2 text-brand-text-muted ring-1 ring-inset ring-brand-border hover:bg-brand-bg-muted focus:z-20 focus:outline-offset-0 disabled:opacity-50 disabled:cursor-not-allowed"
					>
						<span class="sr-only">Previous</span>
						<svg class="h-5 w-5" viewBox="0 0 20 20" fill="currentColor" aria-hidden="true">
							<path
								fill-rule="evenodd"
								d="M12.79 5.23a.75.75 0 01-.02 1.06L8.832 10l3.938 3.71a.75.75 0 11-1.04 1.08l-4.5-4.25a.75.75 0 010-1.08l4.5-4.25a.75.75 0 011.06.02z"
								clip-rule="evenodd"
							/>
						</svg>
					</button>

					{#each visiblePages() as pageNum, i (i)}
						{#if pageNum === '...'}
							<span
								class="relative inline-flex items-center px-4 py-2 text-sm font-semibold text-brand-text-secondary ring-1 ring-inset ring-brand-border"
							>
								...
							</span>
						{:else}
							<button
								onclick={() => goToPage(pageNum as number)}
								class="relative inline-flex items-center px-4 py-2 text-sm font-semibold {page ===
								pageNum
									? 'z-10 bg-brand-accent text-white focus-visible:outline focus-visible:outline-2 focus-visible:outline-offset-2 focus-visible:outline-brand-accent'
									: 'text-brand-primary ring-1 ring-inset ring-brand-border hover:bg-brand-bg-muted focus:z-20 focus:outline-offset-0'}"
							>
								{pageNum}
							</button>
						{/if}
					{/each}

					<button
						onclick={() => goToPage(page + 1)}
						disabled={page === pages}
						class="relative inline-flex items-center rounded-r-md px-2 py-2 text-brand-text-muted ring-1 ring-inset ring-brand-border hover:bg-brand-bg-muted focus:z-20 focus:outline-offset-0 disabled:opacity-50 disabled:cursor-not-allowed"
					>
						<span class="sr-only">Next</span>
						<svg class="h-5 w-5" viewBox="0 0 20 20" fill="currentColor" aria-hidden="true">
							<path
								fill-rule="evenodd"
								d="M7.21 14.77a.75.75 0 01.02-1.06L11.168 10 7.23 6.29a.75.75 0 111.04-1.08l4.5 4.25a.75.75 0 010 1.08l-4.5 4.25a.75.75 0 01-1.06-.02z"
								clip-rule="evenodd"
							/>
						</svg>
					</button>
				</nav>
			</div>
		</div>
	</div>
{/if}
