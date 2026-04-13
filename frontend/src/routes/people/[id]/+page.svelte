<script lang="ts">
	import { page } from '$app/stores';
	import { goto } from '$app/navigation';
	import {
		personApi,
		sacramentApi,
		relationshipApi,
		deathsApi,
		type PersonWithRelations,
		type Person,
		type FamilyTree,
		type Sacrament,
		type DeathWithPerson,
		type DeathCreate
	} from '$lib/api';
	import { toasts } from '$lib/stores/toast';
	import PersonHeader from '$lib/components/PersonHeader.svelte';
	import PersonalInfo from '$lib/components/PersonalInfo.svelte';
	import SacramentList from '$lib/components/SacramentList.svelte';
	import SacramentForm from '$lib/components/SacramentForm.svelte';
	import DeathRecord from '$lib/components/DeathRecord.svelte';
	import DeathForm from '$lib/components/DeathForm.svelte';
	import HouseholdCard from '$lib/components/HouseholdCard.svelte';
	import FamilyTreeCard from '$lib/components/FamilyTreeCard.svelte';
	import Breadcrumbs from '$lib/components/Breadcrumbs.svelte';

	let person = $state<PersonWithRelations | null>(null);
	let familyTree = $state<FamilyTree | null>(null);
	let loading = $state(true);
	let error = $state<string | null>(null);
	let isEditing = $state(false);
	let isSaving = $state(false);
	let showSacramentForm = $state(false);
	let editingSacrament = $state<Sacrament | null>(null);
	let showDeathForm = $state(false);
	let editingDeath = $state<DeathWithPerson | null>(null);

	// Form state for editing
	let editForm = $state<Partial<Person>>({});

	const personId = $derived(Number($page.params.id));

	async function loadPerson() {
		loading = true;
		error = null;

		try {
			const [personData, treeData] = await Promise.all([
				personApi.get(personId),
				relationshipApi.getFamilyTree(personId)
			]);
			person = personData;
			familyTree = treeData;
			resetEditForm();
		} catch (err) {
			error = err instanceof Error ? err.message : 'Failed to load person';
		} finally {
			loading = false;
		}
	}

	function resetEditForm() {
		if (person) {
			editForm = {
				first_name: person.first_name,
				middle_name: person.middle_name,
				last_name: person.last_name,
				date_of_birth: person.date_of_birth,
				gender: person.gender,
				email: person.email,
				phone: person.phone,
				address_line1: person.address_line1,
				address_line2: person.address_line2,
				city: person.city,
				postal_code: person.postal_code,
				notes: person.notes
			};
		}
	}

	function toggleEdit() {
		if (isEditing) {
			resetEditForm();
		}
		isEditing = !isEditing;
	}

	async function handleSave() {
		if (!person) return;

		isSaving = true;
		try {
			await personApi.update(person.id, editForm);
			await loadPerson();
			isEditing = false;
			toasts.success('Person updated successfully');
		} catch (err) {
			toasts.error(err instanceof Error ? err.message : 'Failed to update person');
		} finally {
			isSaving = false;
		}
	}

	function handleCancel() {
		resetEditForm();
		isEditing = false;
	}

	function handleAddSacrament() {
		editingSacrament = null;
		showSacramentForm = true;
	}

	function handleEditSacrament(sacrament: Sacrament) {
		editingSacrament = sacrament;
		showSacramentForm = true;
	}

	async function handleSacramentSave(data: {
		sacrament_type: Sacrament['sacrament_type'];
		date_received: string;
		notes: string | null;
		additional_data: Record<string, unknown> | null;
	}) {
		if (!person) return;

		try {
			if (editingSacrament) {
				await sacramentApi.update(editingSacrament.id, data);
				toasts.success('Sacrament updated successfully');
			} else {
				const result = await sacramentApi.create({
					person_id: person.id,
					...data
				});
				if (result.marriage_side_effects?.household_created) {
					const effects = result.marriage_side_effects;
					toasts.successWithActions(`New household "${effects.household_name}" created`, [
						{
							label: 'Edit',
							onClick: () => goto(`/households/${effects.household_id}`)
						},
						{
							label: 'Undo',
							onClick: async () => {
								try {
									await sacramentApi.undoMarriageHousehold(result.id);
									toasts.success('Household creation undone');
									await loadPerson();
								} catch {
									toasts.error('Failed to undo household creation');
								}
							}
						}
					]);
				} else {
					toasts.success('Sacrament added successfully');
				}
			}
			await loadPerson();
			showSacramentForm = false;
			editingSacrament = null;
		} catch (err) {
			toasts.error(err instanceof Error ? err.message : 'Failed to save sacrament');
		}
	}

	async function handleDeleteSacrament(sacrament: Sacrament) {
		if (!confirm('Are you sure you want to delete this sacrament record?')) return;

		try {
			await sacramentApi.delete(sacrament.id);
			toasts.success('Sacrament deleted successfully');
			await loadPerson();
		} catch (err) {
			toasts.error(err instanceof Error ? err.message : 'Failed to delete sacrament');
		}
	}

	function handleAddDeath() {
		editingDeath = null;
		showDeathForm = true;
	}

	function handleEditDeath() {
		editingDeath = person?.death ?? null;
		showDeathForm = true;
	}

	async function handleDeathSave(data: DeathCreate) {
		if (!person) return;

		try {
			if (person.death) {
				await deathsApi.update(person.death.id, data);
				toasts.success('Death record updated successfully');
			} else {
				await deathsApi.create(data);
				toasts.success('Death record created successfully');
			}
			await loadPerson();
			showDeathForm = false;
			editingDeath = null;
		} catch (err) {
			toasts.error(err instanceof Error ? err.message : 'Failed to save death record');
		}
	}

	async function handleDeleteDeath() {
		if (!person?.death) return;
		if (!confirm('Are you sure you want to delete this death record?')) return;

		try {
			await deathsApi.delete(person.death.id);
			toasts.success('Death record deleted successfully');
			await loadPerson();
		} catch (err) {
			toasts.error(err instanceof Error ? err.message : 'Failed to delete death record');
		}
	}

	async function handleRemoveRelationship(relationshipId: number) {
		if (!confirm('Are you sure you want to remove this relationship?')) return;

		try {
			await relationshipApi.delete(relationshipId);
			toasts.success('Relationship removed successfully');
			await loadPerson();
		} catch (err) {
			toasts.error(err instanceof Error ? err.message : 'Failed to remove relationship');
		}
	}

	$effect(() => {
		if (personId) {
			loadPerson();
		}
	});
</script>

<div>
	<Breadcrumbs
		items={[
			{ label: 'Dashboard', href: '/' },
			{ label: 'People', href: '/people' },
			{ label: person ? `${person.first_name} ${person.last_name}` : 'Person' }
		]}
	/>

	{#if loading}
		<!-- Loading skeleton -->
		<div class="animate-pulse space-y-6">
			<div class="bg-white rounded-lg shadow p-6">
				<div class="flex items-center justify-between">
					<div class="space-y-2">
						<div class="h-8 bg-brand-bg-muted rounded w-48"></div>
						<div class="h-4 bg-brand-bg-muted rounded w-64"></div>
					</div>
					<div class="h-10 bg-brand-bg-muted rounded w-20"></div>
				</div>
			</div>
			<div class="grid grid-cols-1 lg:grid-cols-2 gap-6">
				<div class="bg-white rounded-lg shadow p-6 h-64"></div>
				<div class="bg-white rounded-lg shadow p-6 h-64"></div>
			</div>
		</div>
	{:else if error}
		<!-- Error state -->
		<div class="bg-white rounded-lg shadow p-6 text-center">
			<svg
				class="mx-auto h-12 w-12 text-brand-error"
				fill="none"
				stroke="currentColor"
				viewBox="0 0 24 24"
			>
				<path
					stroke-linecap="round"
					stroke-linejoin="round"
					stroke-width="2"
					d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-3L13.732 4c-.77-1.333-2.694-1.333-3.464 0L3.34 16c-.77 1.333.192 3 1.732 3z"
				/>
			</svg>
			<h3 class="mt-2 text-sm font-medium text-brand-primary">Error loading person</h3>
			<p class="mt-1 text-sm text-brand-text-secondary">{error}</p>
			<div class="mt-6 flex justify-center gap-3">
				<button
					onclick={() => loadPerson()}
					class="inline-flex items-center px-4 py-2 border border-transparent text-sm font-medium rounded-sm text-white bg-brand-accent hover:opacity-90"
				>
					Try again
				</button>
				<button
					onclick={() => goto('/people')}
					class="inline-flex items-center px-4 py-2 border border-brand-border text-sm font-medium rounded-sm text-brand-primary bg-white hover:bg-brand-bg-subtle"
				>
					Go back
				</button>
			</div>
		</div>
	{:else if person}
		<!-- Person Header -->
		<PersonHeader
			{person}
			{isEditing}
			{isSaving}
			onToggleEdit={toggleEdit}
			onSave={handleSave}
			onCancel={handleCancel}
			onRecordDeath={handleAddDeath}
		/>

		<!-- Main content grid -->
		<div class="mt-6 grid grid-cols-1 lg:grid-cols-2 gap-6">
			<!-- Left column -->
			<div class="space-y-6">
				{#if person.death}
					<DeathRecord death={person.death} onEdit={handleEditDeath} onDelete={handleDeleteDeath} />
				{/if}

				<!-- Personal Info -->
				<PersonalInfo {person} {isEditing} bind:editForm />

				<!-- Household -->
				<HouseholdCard
					memberships={person.household_memberships}
					personId={person.id}
					onUpdate={loadPerson}
				/>
			</div>

			<!-- Right column -->
			<div class="space-y-6">
				<!-- Sacraments -->
				<SacramentList
					sacraments={person.sacraments}
					onAdd={handleAddSacrament}
					onEdit={handleEditSacrament}
					onDelete={handleDeleteSacrament}
				/>

				<!-- Family -->
				{#if familyTree}
					<FamilyTreeCard
						{familyTree}
						personId={person.id}
						onRemoveRelationship={handleRemoveRelationship}
						onUpdate={loadPerson}
					/>
				{/if}
			</div>
		</div>
	{/if}

	<!-- Sacrament Form Modal -->
	{#if showSacramentForm && person}
		<SacramentForm
			sacrament={editingSacrament}
			existingSacraments={person.sacraments}
			onSave={handleSacramentSave}
			onClose={() => {
				showSacramentForm = false;
				editingSacrament = null;
			}}
		/>
	{/if}

	<!-- Death Form Modal -->
	{#if showDeathForm && person}
		<DeathForm
			death={editingDeath}
			personId={person.id}
			onSave={handleDeathSave}
			onClose={() => {
				showDeathForm = false;
				editingDeath = null;
			}}
		/>
	{/if}
</div>
