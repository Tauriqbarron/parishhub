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

<div class="flex justify-between pt-6 border-t border-brand-border">
	<button
		type="button"
		onclick={onPrevious}
		disabled={isFirstStep}
		class="px-4 py-2 text-sm font-medium rounded-md
			{isFirstStep
			? 'text-brand-text-muted bg-brand-bg-muted cursor-not-allowed'
			: 'text-brand-text-secondary bg-white border border-brand-border hover:bg-brand-bg-subtle'}"
	>
		Previous
	</button>

	{#if isLastStep}
		<button
			type="button"
			onclick={onSubmit}
			disabled={isSubmitting}
			class="px-6 py-2 text-sm font-medium text-white bg-brand-success rounded-md hover:bg-brand-success/90 disabled:bg-brand-success/50 disabled:cursor-not-allowed"
		>
			{isSubmitting ? 'Submitting...' : 'Submit Registration'}
		</button>
	{:else}
		<div class="flex items-center space-x-3">
			{#if showValidationError}
				<p class="text-sm text-brand-error">
					Please complete all required fields before continuing.
				</p>
			{/if}
			<button
				type="button"
				onclick={handleNext}
				class="px-6 py-2 text-sm font-medium text-white bg-brand-accent rounded-md hover:bg-brand-accent/90"
			>
				Next
			</button>
		</div>
	{/if}
</div>
