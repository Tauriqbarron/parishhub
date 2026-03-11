<script lang="ts">
	import { onMount } from 'svelte';
	import { registrationSessionStore } from '$lib/stores/registrationSession';
	import ProgressIndicator from '$lib/components/registration/ProgressIndicator.svelte';
	import StepNavigation from '$lib/components/registration/StepNavigation.svelte';
	import HouseholdStep from '$lib/components/registration/HouseholdStep.svelte';
	import FamilyMembersStep from '$lib/components/registration/FamilyMembersStep.svelte';
	import RelationshipsStep from '$lib/components/registration/RelationshipsStep.svelte';
	import SacramentsStep from '$lib/components/registration/SacramentsStep.svelte';
	import ReviewStep from '$lib/components/registration/ReviewStep.svelte';

	const steps = ['Household Info', 'Add Family Members', 'Relationships', 'Sacraments', 'Review'];

	let currentStep = $state(0);
	let isSubmitting = $state(false);
	let registrationComplete = $state(false);
	// eslint-disable-next-line @typescript-eslint/no-explicit-any
	let stepComponents: Record<number, any> = {};
	let showValidationError = $state(false);

	onMount(() => {
		const session = registrationSessionStore.initSession();
		currentStep = session.currentStep;
	});

	function goToPrevious() {
		if (currentStep > 0) {
			currentStep--;
			registrationSessionStore.setCurrentStep(currentStep);
		}
	}

	function validateCurrentStep(): boolean {
		const currentStepComponent = stepComponents[currentStep];
		if (!currentStepComponent) {
			return false;
		}

		const isValid = currentStepComponent.isValid();
		if (!isValid) {
			showValidationError = true;
			// Hide error message after user interaction
			setTimeout(() => {
				showValidationError = false;
			}, 5000);
		} else {
			showValidationError = false;
		}

		return isValid;
	}

	function goToNext() {
		if (!validateCurrentStep()) {
			return;
		}

		if (currentStep < steps.length - 1) {
			currentStep++;
			registrationSessionStore.setCurrentStep(currentStep);
			showValidationError = false; // Reset error when changing steps
		}
	}

	function goToStep(step: number) {
		currentStep = step;
		registrationSessionStore.setCurrentStep(step);
	}

	function handleComplete() {
		registrationComplete = true;
	}

	async function handleSubmit() {
		isSubmitting = true;
		// Submission is handled by ReviewStep
		isSubmitting = false;
	}
</script>

<svelte:head>
	<title>Parish Registration</title>
</svelte:head>

<div class="min-h-screen bg-gray-50">
	<div class="max-w-3xl mx-auto px-4 py-8">
		<div class="text-center mb-8">
			<h1 class="text-3xl font-bold text-gray-900">Parish Registration</h1>
			<p class="mt-2 text-gray-600">Welcome! Please complete the registration form below.</p>
		</div>

		<div class="bg-white rounded-lg shadow-lg p-6">
			<ProgressIndicator {steps} {currentStep} />

			<div class="min-h-[300px] py-6">
				{#if currentStep === 0}
					<HouseholdStep bind:this={stepComponents[0]} />
				{:else if currentStep === 1}
					<FamilyMembersStep bind:this={stepComponents[1]} />
				{:else if currentStep === 2}
					<RelationshipsStep bind:this={stepComponents[2]} />
				{:else if currentStep === 3}
					<SacramentsStep bind:this={stepComponents[3]} />
				{:else if currentStep === 4}
					<ReviewStep on:goToStep={(e) => goToStep(e.detail)} on:complete={handleComplete} />
				{/if}
			</div>

			{#if currentStep < 4 && !registrationComplete}
				<StepNavigation
					{currentStep}
					totalSteps={steps.length}
					onPrevious={goToPrevious}
					onNext={goToNext}
					onSubmit={handleSubmit}
					{isSubmitting}
					{validateCurrentStep}
					{showValidationError}
				/>
			{/if}
		</div>
	</div>
</div>
