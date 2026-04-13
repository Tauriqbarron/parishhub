<script lang="ts">
	import { registrationSessionStore } from '$lib/stores/registrationSession';
	import type {
		RegistrationMember,
		RegistrationMemberSacrament
	} from '$lib/stores/registrationSession';

	interface Props {
		member: RegistrationMember;
	}

	let { member }: Props = $props();

	const sacramentTypes = [
		{ value: 'baptism', label: 'Baptism' },
		{ value: 'first_communion', label: 'First Communion' },
		{ value: 'confirmation', label: 'Confirmation' },
		{ value: 'marriage', label: 'Marriage' },
		{ value: 'holy_orders', label: 'Holy Orders' },
		{ value: 'anointing', label: 'Anointing of the Sick' }
	] as const;

	const sacramentColors: Record<string, { bg: string; text: string; border: string }> = {
		baptism: { bg: 'bg-blue-50', text: 'text-blue-700', border: 'border-blue-200' },
		first_communion: { bg: 'bg-purple-50', text: 'text-purple-700', border: 'border-purple-200' },
		confirmation: { bg: 'bg-green-50', text: 'text-green-700', border: 'border-green-200' },
		marriage: { bg: 'bg-pink-50', text: 'text-pink-700', border: 'border-pink-200' },
		holy_orders: { bg: 'bg-amber-50', text: 'text-amber-700', border: 'border-amber-200' },
		anointing: { bg: 'bg-teal-50', text: 'text-teal-700', border: 'border-teal-200' }
	};

	let expanded = $state(false);
	let addingType = $state<string | null>(null);
	let editingIndex = $state<number | null>(null);

	let formDate = $state('');
	let formChurch = $state('');
	let formMinister = $state('');

	let formGodfather = $state('');
	let formGodfatherTempId = $state('');
	let formGodmother = $state('');
	let formGodfatherTempId2 = $state('');

	let formSponsor = $state('');
	let formSponsorTempId = $state('');
	let formConfirmationName = $state('');

	let formSpouse = $state('');
	let formSpouseTempId = $state('');
	let formWitness1 = $state('');
	let formWitness1TempId = $state('');
	let formWitness2 = $state('');
	let formWitness2TempId = $state('');

	let members = $state(registrationSessionStore.getSession().members);

	$effect(() => {
		const unsubscribe = registrationSessionStore.subscribe((session) => {
			members = session.members;
		});
		return unsubscribe;
	});

	function getMemberName(m: RegistrationMember): string {
		return `${m.firstName} ${m.lastName}`.trim() || 'Unnamed Member';
	}

	function getOtherMembers(): RegistrationMember[] {
		return members.filter((m) => m.tempId !== member.tempId);
	}

	function getSacramentByType(type: string): RegistrationMemberSacrament | undefined {
		return member.sacraments.find((s) => s.type === type);
	}

	function getSacramentLabel(type: string): string {
		return sacramentTypes.find((t) => t.value === type)?.label || type;
	}

	function resetForm(): void {
		formDate = '';
		formChurch = '';
		formMinister = '';
		formGodfather = '';
		formGodfatherTempId = '';
		formGodmother = '';
		formGodfatherTempId2 = '';
		formSponsor = '';
		formSponsorTempId = '';
		formConfirmationName = '';
		formSpouse = '';
		formSpouseTempId = '';
		formWitness1 = '';
		formWitness1TempId = '';
		formWitness2 = '';
		formWitness2TempId = '';
		addingType = null;
		editingIndex = null;
	}

	function startAdd(type: string): void {
		resetForm();
		addingType = type;
	}

	function startEdit(index: number): void {
		const sacrament = member.sacraments[index];
		if (!sacrament) return;

		resetForm();
		editingIndex = index;
		addingType = sacrament.type;
		formDate = sacrament.date;
		formChurch = (sacrament.additionalData.church as string) || '';
		formMinister = (sacrament.additionalData.minister as string) || '';

		if (sacrament.type === 'baptism') {
			formGodfather = (sacrament.additionalData.godfather as string) || '';
			formGodfatherTempId = (sacrament.additionalData.godfatherTempId as string) || '';
			formGodmother = (sacrament.additionalData.godmother as string) || '';
			formGodfatherTempId2 = (sacrament.additionalData.godmotherTempId as string) || '';
		} else if (sacrament.type === 'confirmation') {
			formSponsor = (sacrament.additionalData.sponsor as string) || '';
			formSponsorTempId = (sacrament.additionalData.sponsorTempId as string) || '';
			formConfirmationName = (sacrament.additionalData.confirmationName as string) || '';
		} else if (sacrament.type === 'marriage') {
			formSpouse = (sacrament.additionalData.spouse as string) || '';
			formSpouseTempId = (sacrament.additionalData.spouseTempId as string) || '';
			formWitness1 = (sacrament.additionalData.witness1 as string) || '';
			formWitness1TempId = (sacrament.additionalData.witness1TempId as string) || '';
			formWitness2 = (sacrament.additionalData.witness2 as string) || '';
			formWitness2TempId = (sacrament.additionalData.witness2TempId as string) || '';
		}
	}

	function buildAdditionalData(): Record<string, unknown> {
		const data: Record<string, unknown> = {};
		if (formChurch) data.church = formChurch;
		if (formMinister) data.minister = formMinister;

		if (addingType === 'baptism') {
			if (formGodfatherTempId) {
				data.godfatherTempId = formGodfatherTempId;
				const m = members.find((m) => m.tempId === formGodfatherTempId);
				if (m) data.godfather = getMemberName(m);
			} else if (formGodfather) {
				data.godfather = formGodfather;
			}
			if (formGodfatherTempId2) {
				data.godmotherTempId = formGodfatherTempId2;
				const m = members.find((m) => m.tempId === formGodfatherTempId2);
				if (m) data.godmother = getMemberName(m);
			} else if (formGodmother) {
				data.godmother = formGodmother;
			}
		} else if (addingType === 'confirmation') {
			if (formSponsorTempId) {
				data.sponsorTempId = formSponsorTempId;
				const m = members.find((m) => m.tempId === formSponsorTempId);
				if (m) data.sponsor = getMemberName(m);
			} else if (formSponsor) {
				data.sponsor = formSponsor;
			}
			if (formConfirmationName) data.confirmationName = formConfirmationName;
		} else if (addingType === 'marriage') {
			if (formSpouseTempId) {
				data.spouseTempId = formSpouseTempId;
				const m = members.find((m) => m.tempId === formSpouseTempId);
				if (m) data.spouse = getMemberName(m);
			} else if (formSpouse) {
				data.spouse = formSpouse;
			}
			if (formWitness1TempId) {
				data.witness1TempId = formWitness1TempId;
				const m = members.find((m) => m.tempId === formWitness1TempId);
				if (m) data.witness1 = getMemberName(m);
			} else if (formWitness1) {
				data.witness1 = formWitness1;
			}
			if (formWitness2TempId) {
				data.witness2TempId = formWitness2TempId;
				const m = members.find((m) => m.tempId === formWitness2TempId);
				if (m) data.witness2 = getMemberName(m);
			} else if (formWitness2) {
				data.witness2 = formWitness2;
			}
		}

		return data;
	}

	function saveSacrament(): void {
		if (!addingType || !formDate) return;

		const newSacrament: RegistrationMemberSacrament = {
			type: addingType,
			date: formDate,
			additionalData: buildAdditionalData()
		};

		let updatedSacraments: RegistrationMemberSacrament[];
		if (editingIndex !== null) {
			updatedSacraments = [...member.sacraments];
			updatedSacraments[editingIndex] = newSacrament;
		} else {
			updatedSacraments = [...member.sacraments, newSacrament];
		}

		registrationSessionStore.updateMember(member.tempId, {
			sacraments: updatedSacraments
		});

		resetForm();
	}

	function removeSacrament(index: number): void {
		const updatedSacraments = member.sacraments.filter((_, i) => i !== index);
		registrationSessionStore.updateMember(member.tempId, {
			sacraments: updatedSacraments
		});
	}

	function formatDate(date: string): string {
		return new Date(date).toLocaleDateString('en-NZ', {
			year: 'numeric',
			month: 'short',
			day: 'numeric'
		});
	}

	function getPersonDisplay(
		data: Record<string, unknown>,
		tempIdKey: string,
		nameKey: string
	): string | null {
		const name = data[nameKey] as string | undefined;
		return name || null;
	}
</script>

<div class="border rounded-lg bg-white shadow-sm">
	<button
		type="button"
		onclick={() => (expanded = !expanded)}
		class="w-full px-4 py-3 flex items-center justify-between text-left bg-brand-bg-subtle transition-colors"
	>
		<div class="flex items-center gap-3">
			<span class="font-medium text-brand-primary">{getMemberName(member)}</span>
			{#if member.sacraments.length > 0}
				<span class="text-xs bg-brand-accent/10 text-brand-primary px-2 py-0.5 rounded-full">
					{member.sacraments.length} sacrament{member.sacraments.length !== 1 ? 's' : ''}
				</span>
			{/if}
		</div>
		<svg
			class="w-5 h-5 text-brand-text-muted transition-transform {expanded ? 'rotate-180' : ''}"
			fill="none"
			stroke="currentColor"
			viewBox="0 0 24 24"
		>
			<path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M19 9l-7 7-7-7" />
		</svg>
	</button>

	{#if expanded}
		<div class="px-4 pb-4 border-t border-brand-border">
			<div class="mt-4 space-y-3">
				{#each member.sacraments as sacrament, index}
					{@const colors = sacramentColors[sacrament.type] || sacramentColors.baptism}
					<div
						class="flex items-start justify-between p-3 rounded-lg {colors.bg} {colors.border} border"
					>
						<div>
							<div class="font-medium {colors.text}">{getSacramentLabel(sacrament.type)}</div>
							<div class="text-sm {colors.text} opacity-75">
								{formatDate(sacrament.date)}
								{#if sacrament.additionalData.church}
									<span class="mx-1">-</span>
									{sacrament.additionalData.church}
								{/if}
							</div>
							{#if sacrament.additionalData.minister}
								<div class="text-sm {colors.text} opacity-75">
									Minister: {sacrament.additionalData.minister}
								</div>
							{/if}
							{#if sacrament.type === 'baptism'}
								{#if getPersonDisplay(sacrament.additionalData, 'godfatherTempId', 'godfather')}
									<div class="text-sm {colors.text} opacity-75">
										Godfather: {getPersonDisplay(
											sacrament.additionalData,
											'godfatherTempId',
											'godfather'
										)}
									</div>
								{/if}
								{#if getPersonDisplay(sacrament.additionalData, 'godmotherTempId', 'godmother')}
									<div class="text-sm {colors.text} opacity-75">
										Godmother: {getPersonDisplay(
											sacrament.additionalData,
											'godmotherTempId',
											'godmother'
										)}
									</div>
								{/if}
							{:else if sacrament.type === 'confirmation'}
								{#if getPersonDisplay(sacrament.additionalData, 'sponsorTempId', 'sponsor')}
									<div class="text-sm {colors.text} opacity-75">
										Sponsor: {getPersonDisplay(
											sacrament.additionalData,
											'sponsorTempId',
											'sponsor'
										)}
									</div>
								{/if}
								{#if sacrament.additionalData.confirmationName}
									<div class="text-sm {colors.text} opacity-75">
										Confirmation Name: {sacrament.additionalData.confirmationName}
									</div>
								{/if}
							{:else if sacrament.type === 'marriage'}
								{#if getPersonDisplay(sacrament.additionalData, 'spouseTempId', 'spouse')}
									<div class="text-sm {colors.text} opacity-75">
										Spouse: {getPersonDisplay(sacrament.additionalData, 'spouseTempId', 'spouse')}
									</div>
								{/if}
								{#if getPersonDisplay(sacrament.additionalData, 'witness1TempId', 'witness1')}
									<div class="text-sm {colors.text} opacity-75">
										Witness 1: {getPersonDisplay(
											sacrament.additionalData,
											'witness1TempId',
											'witness1'
										)}
									</div>
								{/if}
								{#if getPersonDisplay(sacrament.additionalData, 'witness2TempId', 'witness2')}
									<div class="text-sm {colors.text} opacity-75">
										Witness 2: {getPersonDisplay(
											sacrament.additionalData,
											'witness2TempId',
											'witness2'
										)}
									</div>
								{/if}
							{/if}
						</div>
						<div class="flex items-center gap-1">
							<button
								type="button"
								onclick={() => startEdit(index)}
								class="p-1.5 rounded hover:bg-white/50 {colors.text} transition-colors"
								title="Edit"
							>
								<svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
									<path
										stroke-linecap="round"
										stroke-linejoin="round"
										stroke-width="2"
										d="M11 5H6a2 2 0 00-2 2v11a2 2 0 002 2h11a2 2 0 002-2v-5m-1.414-9.414a2 2 0 112.828 2.828L11.828 15H9v-2.828l8.586-8.586z"
									/>
								</svg>
							</button>
							<button
								type="button"
								onclick={() => removeSacrament(index)}
								class="p-1.5 rounded hover:bg-red-100 text-red-600 transition-colors"
								title="Delete"
							>
								<svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
									<path
										stroke-linecap="round"
										stroke-linejoin="round"
										stroke-width="2"
										d="M19 7l-.867 12.142A2 2 0 0116.138 21H7.862a2 2 0 01-1.995-1.858L5 7m5 4v6m4-6v6m1-10V4a1 1 0 00-1-1h-4a1 1 0 00-1 1v3M4 7h16"
									/>
								</svg>
							</button>
						</div>
					</div>
				{/each}
			</div>

			{#if addingType}
				{@const colors = sacramentColors[addingType] || sacramentColors.baptism}
				<div class="mt-4 p-4 border rounded-lg {colors.bg} {colors.border}">
					<h4 class="font-medium {colors.text} mb-3">
						{editingIndex !== null ? 'Edit' : 'Add'}
						{getSacramentLabel(addingType)}
					</h4>

					<div class="space-y-3">
						<div>
							<label for="date-{member.tempId}" class="block text-sm text-brand-primary mb-1">
								Date Received <span class="text-red-500">*</span>
							</label>
							<input
								type="date"
								id="date-{member.tempId}"
								bind:value={formDate}
								class="w-full border border-brand-border rounded px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-brand-accent"
							/>
						</div>

						<div>
							<label for="church-{member.tempId}" class="block text-sm text-brand-primary mb-1">
								Church/Location
							</label>
							<input
								type="text"
								id="church-{member.tempId}"
								bind:value={formChurch}
								placeholder="e.g., St. Mary's Cathedral"
								class="w-full border border-brand-border rounded px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-brand-accent"
							/>
						</div>

						<div>
							<label for="minister-{member.tempId}" class="block text-sm text-brand-primary mb-1">
								Minister/Celebrant
							</label>
							<input
								type="text"
								id="minister-{member.tempId}"
								bind:value={formMinister}
								placeholder="e.g., Fr. John Smith"
								class="w-full border border-brand-border rounded px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-brand-accent"
							/>
						</div>

						{#if addingType === 'baptism'}
							<div class="grid grid-cols-1 md:grid-cols-2 gap-3">
								<div>
									<label
										for="godfather-{member.tempId}"
										class="block text-sm text-brand-primary mb-1"
									>
										Godfather
									</label>
									<select
										id="godfather-select-{member.tempId}"
										bind:value={formGodfatherTempId}
										onchange={() => {
											if (formGodfatherTempId) formGodfather = '';
										}}
										class="w-full border border-brand-border rounded px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-brand-accent mb-1"
									>
										<option value="">Select household member...</option>
										{#each getOtherMembers() as m}
											<option value={m.tempId}>{getMemberName(m)}</option>
										{/each}
									</select>
									<input
										type="text"
										id="godfather-{member.tempId}"
										bind:value={formGodfather}
										oninput={() => {
											if (formGodfather) formGodfatherTempId = '';
										}}
										placeholder="Or enter name..."
										class="w-full border border-brand-border rounded px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-brand-accent"
									/>
								</div>
								<div>
									<label
										for="godmother-{member.tempId}"
										class="block text-sm text-brand-primary mb-1"
									>
										Godmother
									</label>
									<select
										id="godmother-select-{member.tempId}"
										bind:value={formGodfatherTempId2}
										onchange={() => {
											if (formGodfatherTempId2) formGodmother = '';
										}}
										class="w-full border border-brand-border rounded px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-brand-accent mb-1"
									>
										<option value="">Select household member...</option>
										{#each getOtherMembers() as m}
											<option value={m.tempId}>{getMemberName(m)}</option>
										{/each}
									</select>
									<input
										type="text"
										id="godmother-{member.tempId}"
										bind:value={formGodmother}
										oninput={() => {
											if (formGodmother) formGodfatherTempId2 = '';
										}}
										placeholder="Or enter name..."
										class="w-full border border-brand-border rounded px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-brand-accent"
									/>
								</div>
							</div>
						{:else if addingType === 'confirmation'}
							<div class="grid grid-cols-1 md:grid-cols-2 gap-3">
								<div>
									<label
										for="sponsor-{member.tempId}"
										class="block text-sm text-brand-primary mb-1"
									>
										Sponsor
									</label>
									<select
										id="sponsor-select-{member.tempId}"
										bind:value={formSponsorTempId}
										onchange={() => {
											if (formSponsorTempId) formSponsor = '';
										}}
										class="w-full border border-brand-border rounded px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-brand-accent mb-1"
									>
										<option value="">Select household member...</option>
										{#each getOtherMembers() as m}
											<option value={m.tempId}>{getMemberName(m)}</option>
										{/each}
									</select>
									<input
										type="text"
										id="sponsor-{member.tempId}"
										bind:value={formSponsor}
										oninput={() => {
											if (formSponsor) formSponsorTempId = '';
										}}
										placeholder="Or enter name..."
										class="w-full border border-brand-border rounded px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-brand-accent"
									/>
								</div>
								<div>
									<label
										for="confirmation-name-{member.tempId}"
										class="block text-sm text-brand-primary mb-1"
									>
										Confirmation Name
									</label>
									<input
										type="text"
										id="confirmation-name-{member.tempId}"
										bind:value={formConfirmationName}
										placeholder="e.g., Joseph"
										class="w-full border border-brand-border rounded px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-brand-accent"
									/>
								</div>
							</div>
						{:else if addingType === 'marriage'}
							<div>
								<label for="spouse-{member.tempId}" class="block text-sm text-brand-primary mb-1">
									Spouse
								</label>
								<select
									id="spouse-select-{member.tempId}"
									bind:value={formSpouseTempId}
									onchange={() => {
										if (formSpouseTempId) formSpouse = '';
									}}
									class="w-full border border-brand-border rounded px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-brand-accent mb-1"
								>
									<option value="">Select household member...</option>
									{#each getOtherMembers() as m}
										<option value={m.tempId}>{getMemberName(m)}</option>
									{/each}
								</select>
								<input
									type="text"
									id="spouse-{member.tempId}"
									bind:value={formSpouse}
									oninput={() => {
										if (formSpouse) formSpouseTempId = '';
									}}
									placeholder="Or enter spouse name..."
									class="w-full border border-brand-border rounded px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-brand-accent"
								/>
							</div>
							<div class="grid grid-cols-1 md:grid-cols-2 gap-3">
								<div>
									<label
										for="witness1-{member.tempId}"
										class="block text-sm text-brand-primary mb-1"
									>
										Witness 1
									</label>
									<select
										id="witness1-select-{member.tempId}"
										bind:value={formWitness1TempId}
										onchange={() => {
											if (formWitness1TempId) formWitness1 = '';
										}}
										class="w-full border border-brand-border rounded px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-brand-accent mb-1"
									>
										<option value="">Select household member...</option>
										{#each getOtherMembers() as m}
											<option value={m.tempId}>{getMemberName(m)}</option>
										{/each}
									</select>
									<input
										type="text"
										id="witness1-{member.tempId}"
										bind:value={formWitness1}
										oninput={() => {
											if (formWitness1) formWitness1TempId = '';
										}}
										placeholder="Or enter name..."
										class="w-full border border-brand-border rounded px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-brand-accent"
									/>
								</div>
								<div>
									<label
										for="witness2-{member.tempId}"
										class="block text-sm text-brand-primary mb-1"
									>
										Witness 2
									</label>
									<select
										id="witness2-select-{member.tempId}"
										bind:value={formWitness2TempId}
										onchange={() => {
											if (formWitness2TempId) formWitness2 = '';
										}}
										class="w-full border border-brand-border rounded px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-brand-accent mb-1"
									>
										<option value="">Select household member...</option>
										{#each getOtherMembers() as m}
											<option value={m.tempId}>{getMemberName(m)}</option>
										{/each}
									</select>
									<input
										type="text"
										id="witness2-{member.tempId}"
										bind:value={formWitness2}
										oninput={() => {
											if (formWitness2) formWitness2TempId = '';
										}}
										placeholder="Or enter name..."
										class="w-full border border-brand-border rounded px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-brand-accent"
									/>
								</div>
							</div>
						{/if}
					</div>

					<div class="flex gap-2 mt-4">
						<button
							type="button"
							onclick={saveSacrament}
							disabled={!formDate}
							class="px-4 py-2 bg-brand-accent text-white rounded text-sm hover:bg-brand-accent/90 disabled:bg-brand-bg-muted disabled:cursor-not-allowed focus:outline-none focus:ring-2 focus:ring-brand-accent"
						>
							{editingIndex !== null ? 'Update' : 'Add'} Sacrament
						</button>
						<button
							type="button"
							onclick={resetForm}
							class="px-4 py-2 border border-brand-border rounded text-sm bg-brand-bg-subtle focus:outline-none focus:ring-2 focus:ring-brand-accent"
						>
							Cancel
						</button>
					</div>
				</div>
			{:else}
				<div class="mt-4">
					<p class="text-sm text-brand-text-secondary mb-2">Add a sacrament:</p>
					<div class="flex flex-wrap gap-2">
						{#each sacramentTypes as type}
							{@const existing = getSacramentByType(type.value)}
							{@const colors = sacramentColors[type.value]}
							<button
								type="button"
								onclick={() => startAdd(type.value)}
								class="px-3 py-1.5 text-sm rounded-full border transition-colors {existing
									? colors.bg + ' ' + colors.border + ' ' + colors.text
									: 'bg-brand-bg-subtle border-brand-border text-brand-text-secondary hover:bg-brand-bg-muted'}"
							>
								{#if existing}
									<svg
										class="inline w-3 h-3 mr-1"
										fill="none"
										stroke="currentColor"
										viewBox="0 0 24 24"
									>
										<path
											stroke-linecap="round"
											stroke-linejoin="round"
											stroke-width="2"
											d="M5 13l4 4L19 7"
										/>
									</svg>
								{:else}
									<svg
										class="inline w-3 h-3 mr-1"
										fill="none"
										stroke="currentColor"
										viewBox="0 0 24 24"
									>
										<path
											stroke-linecap="round"
											stroke-linejoin="round"
											stroke-width="2"
											d="M12 4v16m8-8H4"
										/>
									</svg>
								{/if}
								{type.label}
							</button>
						{/each}
					</div>
				</div>
			{/if}
		</div>
	{/if}
</div>
