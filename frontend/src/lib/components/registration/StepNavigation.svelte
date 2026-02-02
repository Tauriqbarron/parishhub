<script lang="ts">
	interface Props {
		currentStep: number;
		totalSteps: number;
		onPrevious: () => void;
		onNext: () => void;
		onSubmit: () => void;
		isSubmitting?: boolean;
		validateCurrentStep?: () => boolean;
		showValidationError?: boolean;
	}

	let {
		currentStep,
		totalSteps,
		onPrevious,
		onNext,
		onSubmit,
		isSubmitting = false,
		validateCurrentStep,
		showValidationError = false
	}: Props = $props();

	let isFirstStep = $derived(currentStep === 0);
	let isLastStep = $derived(currentStep === totalSteps - 1);

	function handleNext() {
		if (validateCurrentStep && !validateCurrentStep()) {
			return;
		}
		onNext();
	}
</script>

<div class="flex justify-between pt-6 border-t border-gray-200">
	<button
		type="button"
		onclick={onPrevious}
		disabled={isFirstStep}
		class="px-4 py-2 text-sm font-medium rounded-md
			{isFirstStep
			? 'text-gray-400 bg-gray-100 cursor-not-allowed'
			: 'text-gray-700 bg-white border border-gray-300 hover:bg-gray-50'}"
	>
		Previous
	</button>

	{#if isLastStep}
		<button
			type="button"
			onclick={onSubmit}
			disabled={isSubmitting}
			class="px-6 py-2 text-sm font-medium text-white bg-green-600 rounded-md hover:bg-green-700 disabled:bg-green-400 disabled:cursor-not-allowed"
		>
			{isSubmitting ? 'Submitting...' : 'Submit Registration'}
		</button>
	{:else}
		<div class="flex items-center space-x-3">
			{#if showValidationError}
				<p class="text-sm text-red-600">Please complete all required fields before continuing.</p>
			{/if}
			<button
				type="button"
				onclick={handleNext}
				class="px-6 py-2 text-sm font-medium text-white bg-blue-600 rounded-md hover:bg-blue-700"
			>
				Next
			</button>
		</div>
	{/if}
</div>
