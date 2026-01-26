<script lang="ts">
	import { onMount } from 'svelte';
	import { registrationSessionStore } from '$lib/stores/registrationSession';
	import ProgressIndicator from '$lib/components/registration/ProgressIndicator.svelte';
	import StepNavigation from '$lib/components/registration/StepNavigation.svelte';
	import ReviewStep from '$lib/components/registration/ReviewStep.svelte';

	const steps = ['Household Info', 'Add Family Members', 'Relationships', 'Sacraments', 'Review'];

	let currentStep = $state(0);
	let isSubmitting = $state(false);
	let registrationComplete = $state(false);

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

	function goToNext() {
		if (currentStep < steps.length - 1) {
			currentStep++;
			registrationSessionStore.setCurrentStep(currentStep);
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
					<div class="text-center text-gray-500">
						<h2 class="text-xl font-semibold text-gray-900 mb-4">Household Information</h2>
						<p>Household form will be implemented here.</p>
					</div>
				{:else if currentStep === 1}
					<div class="text-center text-gray-500">
						<h2 class="text-xl font-semibold text-gray-900 mb-4">Add Family Members</h2>
						<p>Family member form will be implemented here.</p>
					</div>
				{:else if currentStep === 2}
					<div class="text-center text-gray-500">
						<h2 class="text-xl font-semibold text-gray-900 mb-4">Relationships</h2>
						<p>Relationship form will be implemented here.</p>
					</div>
				{:else if currentStep === 3}
					<div class="text-center text-gray-500">
						<h2 class="text-xl font-semibold text-gray-900 mb-4">Sacraments</h2>
						<p>Sacrament form will be implemented here.</p>
					</div>
				{:else if currentStep === 4}
					<ReviewStep
						on:goToStep={(e) => goToStep(e.detail)}
						on:complete={handleComplete}
					/>
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
				/>
			{/if}
		</div>
	</div>
</div>
