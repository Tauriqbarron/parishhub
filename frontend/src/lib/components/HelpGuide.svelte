<script lang="ts">
	interface Props {
		currentStep: number;
	}

	let { currentStep }: Props = $props();

	const stepHelp = [
		{
			title: 'Household Information',
			content: 'Enter your household details. This is typically your family name and home address.',
			tips: [
				'Use your family surname for the household name',
				'Enter the address where your family resides',
				'Include a phone number where you can be reached'
			]
		},
		{
			title: 'Family Members',
			content: 'Add all members of your household who should be registered with the parish.',
			tips: [
				'Include all family members living at this address',
				'Designate one adult as the Head of Household',
				'Date of birth is used to determine eligibility for sacraments'
			]
		},
		{
			title: 'Family Relationships',
			content: 'Define how family members are related to each other.',
			tips: [
				'Select each pair of family members',
				'Choose the appropriate relationship type',
				'Common relationships include spouse, parent, child, sibling'
			]
		},
		{
			title: 'Sacraments',
			content: 'Record the sacraments each family member has received.',
			tips: [
				'Enter dates as accurately as possible',
				'Godparent fields can be family members or external names',
				'Skip any sacraments that have not been received'
			]
		},
		{
			title: 'Review & Submit',
			content: 'Review all information before submitting your registration.',
			tips: [
				'Double-check all names and dates',
				'Verify contact information is correct',
				'You can go back to previous steps to make corrections'
			]
		}
	];

	const currentHelp = $derived(stepHelp[currentStep] || stepHelp[0]);
</script>

<aside class="bg-blue-50 border-l-4 border-blue-400 p-4 rounded-r-lg">
	<h3 class="font-bold text-blue-900 text-lg mb-2">{currentHelp.title}</h3>
	<p class="text-blue-800 mb-3">{currentHelp.content}</p>
	<ul class="space-y-1 mb-4">
		{#each currentHelp.tips as tip}
			<li class="text-blue-700 text-sm flex items-start">
				<span class="mr-2">•</span>
				<span>{tip}</span>
			</li>
		{/each}
	</ul>

	<div class="mt-4 p-3 bg-green-50 border border-green-200 rounded">
		<p class="text-green-800 text-sm">
			<strong>Your progress is automatically saved.</strong>
			You can close this page and return later - your information will still be here.
		</p>
	</div>
</aside>
