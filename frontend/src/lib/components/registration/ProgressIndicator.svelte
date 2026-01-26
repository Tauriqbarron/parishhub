<script lang="ts">
	interface Props {
		steps: string[];
		currentStep: number;
	}

	let { steps, currentStep }: Props = $props();
</script>

<nav aria-label="Registration progress" class="mb-8">
	<ol class="flex items-center justify-between">
		{#each steps as step, index}
			<li class="flex items-center {index < steps.length - 1 ? 'flex-1' : ''}">
				<div class="flex flex-col items-center">
					<div
						class="w-10 h-10 rounded-full flex items-center justify-center text-sm font-medium
						{index < currentStep
							? 'bg-green-600 text-white'
							: index === currentStep
								? 'bg-blue-600 text-white'
								: 'bg-gray-200 text-gray-600'}"
					>
						{#if index < currentStep}
							<svg class="w-5 h-5" fill="currentColor" viewBox="0 0 20 20">
								<path
									fill-rule="evenodd"
									d="M16.707 5.293a1 1 0 010 1.414l-8 8a1 1 0 01-1.414 0l-4-4a1 1 0 011.414-1.414L8 12.586l7.293-7.293a1 1 0 011.414 0z"
									clip-rule="evenodd"
								/>
							</svg>
						{:else}
							{index + 1}
						{/if}
					</div>
					<span
						class="mt-2 text-xs font-medium text-center hidden sm:block
						{index <= currentStep ? 'text-gray-900' : 'text-gray-500'}"
					>
						{step}
					</span>
				</div>
				{#if index < steps.length - 1}
					<div
						class="flex-1 h-0.5 mx-2 sm:mx-4
						{index < currentStep ? 'bg-green-600' : 'bg-gray-200'}"
					></div>
				{/if}
			</li>
		{/each}
	</ol>
	<p class="mt-4 text-sm text-center text-gray-600 sm:hidden">
		Step {currentStep + 1} of {steps.length}: {steps[currentStep]}
	</p>
</nav>
