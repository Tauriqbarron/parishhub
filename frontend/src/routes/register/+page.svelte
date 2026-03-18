<script lang="ts">
	import { onMount } from 'svelte';
	import { registrationSessionStore } from '$lib/stores/registrationSession';
	import type { RegistrationType } from '$lib/stores/registrationSession';
	import ProgressIndicator from '$lib/components/registration/ProgressIndicator.svelte';
	import StepNavigation from '$lib/components/registration/StepNavigation.svelte';
	import RegistrationTypeStep from '$lib/components/registration/RegistrationTypeStep.svelte';
	import HouseholdStep from '$lib/components/registration/HouseholdStep.svelte';
	import FamilyMembersStep from '$lib/components/registration/FamilyMembersStep.svelte';
	import RelationshipsStep from '$lib/components/registration/RelationshipsStep.svelte';
	import IndividualInfoStep from '$lib/components/registration/IndividualInfoStep.svelte';
	import SacramentsStep from '$lib/components/registration/SacramentsStep.svelte';
	import ConsentStep from '$lib/components/registration/ConsentStep.svelte';
	import ReviewStep from '$lib/components/registration/ReviewStep.svelte';

	const householdSteps = [
		'Registration Type',
		'Household Info',
		'Add Family Members',
		'Relationships',
		'Sacraments',
		'Consent',
		'Review'
	];

	const individualSteps = [
		'Registration Type',
		'Your Information',
		'Sacraments',
		'Consent',
		'Review'
	];

	let registrationType = $state<RegistrationType>(null);
	let currentStep = $state(0);
	let isSubmitting = $state(false);
	let registrationComplete = $state(false);
	// eslint-disable-next-line @typescript-eslint/no-explicit-any
	let stepComponents: Record<number, any> = {};
	let showValidationError = $state(false);

	let steps = $derived(
		registrationType === 'individual'
			? individualSteps
			: registrationType === 'household'
				? householdSteps
				: ['Registration Type']
	);

	onMount(() => {
		const session = registrationSessionStore.initSession();
		registrationType = session.registrationType;
		currentStep = session.currentStep;
	});

	// Keep registrationType in sync with store
	$effect(() => {
		const unsubscribe = registrationSessionStore.subscribe((s) => {
			if (s.registrationType !== registrationType) {
				registrationType = s.registrationType;
			}
		});
		return unsubscribe;
	});

	function goToPrevious() {
		if (currentStep > 0) {
			// If going back to step 0 (registration type), reset the type
			if (currentStep === 1) {
				registrationSessionStore.setRegistrationType(null);
			}
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
			showValidationError = false;
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
		isSubmitting = false;
	}

	let isLastStep = $derived(currentStep === steps.length - 1);
</script>

<svelte:head>
	<title>Chaplaincy Registration</title>
</svelte:head>

<div class="min-h-screen bg-gray-50">
	<div class="max-w-3xl mx-auto px-4 py-8">
		<div class="text-center mb-8">
			<h1 class="text-3xl font-bold text-gray-900">Chaplaincy Registration</h1>
			<p class="mt-2 text-gray-600">Welcome! Please complete the registration form below.</p>
		</div>

		<div class="bg-white rounded-lg shadow-lg p-6">
			{#if registrationComplete}
				<div class="text-center py-12">
					<div class="mx-auto w-16 h-16 bg-green-100 rounded-full flex items-center justify-center mb-4">
						<svg class="w-8 h-8 text-green-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
							<path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M5 13l4 4L19 7" />
						</svg>
					</div>
					<h2 class="text-2xl font-bold text-gray-900 mb-2">Registration Submitted!</h2>
					<p class="text-gray-600 mb-4">
						Thank you for registering with our chaplaincy. We will review your information and be in touch shortly.
					</p>
					<p class="text-gray-500 text-sm">
						If you need to make any changes or additions, please contact us at
						<a href="mailto:dataadmin@fssp.nz" class="text-blue-600 hover:text-blue-800 underline">dataadmin@fssp.nz</a>.
					</p>
				</div>
			{:else}
				<ProgressIndicator {steps} {currentStep} />

				<div class="min-h-[300px] py-6">
					{#if currentStep === 0}
						<RegistrationTypeStep bind:this={stepComponents[0]} />
					{:else if registrationType === 'household'}
						{#if currentStep === 1}
							<HouseholdStep bind:this={stepComponents[1]} />
						{:else if currentStep === 2}
							<FamilyMembersStep bind:this={stepComponents[2]} />
						{:else if currentStep === 3}
							<RelationshipsStep bind:this={stepComponents[3]} />
						{:else if currentStep === 4}
							<SacramentsStep bind:this={stepComponents[4]} />
						{:else if currentStep === 5}
							<ConsentStep bind:this={stepComponents[5]} />
						{:else if currentStep === 6}
							<ReviewStep on:goToStep={(e) => goToStep(e.detail)} on:complete={handleComplete} />
						{/if}
					{:else if registrationType === 'individual'}
						{#if currentStep === 1}
							<IndividualInfoStep bind:this={stepComponents[1]} />
						{:else if currentStep === 2}
							<SacramentsStep bind:this={stepComponents[2]} />
						{:else if currentStep === 3}
							<ConsentStep bind:this={stepComponents[3]} />
						{:else if currentStep === 4}
							<ReviewStep on:goToStep={(e) => goToStep(e.detail)} on:complete={handleComplete} />
						{/if}
					{/if}
				</div>

				{#if !isLastStep}
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
			{/if}
		</div>
	</div>
</div>
