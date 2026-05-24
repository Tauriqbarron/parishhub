<script lang="ts">
	import { UserPlus, AlertTriangle, Check, X, Loader } from 'lucide-svelte';
	import { rosterApi } from '$lib/api/roster';

	interface Props {
		/** The person's first name for the message */
		firstName: string;
		/** The missing role's name */
		roleName: string;
		/** The missing role's ID */
		roleId: number;
		/** The person's database ID */
		personId: number;
		/** Called after role is assigned and the assignment should be retried */
		onResolved: () => void;
		/** Called when user dismisses the prompt */
		onDismiss: () => void;
	}

	let { firstName, roleName, roleId, personId, onResolved, onDismiss }: Props = $props();

	let status = $state<'idle' | 'assigning' | 'success' | 'error'>('idle');
	let errorMessage = $state('');

	async function handleAssign() {
		status = 'assigning';
		errorMessage = '';
		try {
			await rosterApi.assignRole(roleId, personId);
			status = 'success';
			// Brief pause so user sees the success state, then retry the assignment
			setTimeout(() => onResolved(), 600);
		} catch (e: any) {
			status = 'error';
			errorMessage = e?.message || 'Failed to assign role. Please try again.';
		}
	}
</script>

<div class="role-prompt" class:success={status === 'success'} class:error={status === 'error'}>
	<div class="prompt-body">
		{#if status === 'success'}
			<Check class="icon" />
			<span class="message">Role assigned! Retrying assignment…</span>
		{:else if status === 'error'}
			<AlertTriangle class="icon" />
			<span class="message">{errorMessage}</span>
		{:else}
			<AlertTriangle class="icon" />
			<span class="message">
				<strong>{firstName}</strong> doesn't have the <strong>{roleName}</strong> role. Assign now?
			</span>
		{/if}
	</div>

	<div class="prompt-actions">
		{#if status === 'success'}
			<span class="spinner"><Loader class="icon-sm spin" /></span>
		{:else if status === 'error'}
			<button class="btn-retry" onclick={handleAssign}>
				<UserPlus class="icon-sm" /> Retry
			</button>
			<button class="btn-dismiss" onclick={onDismiss}>
				<X class="icon-sm" /> Dismiss
			</button>
		{:else}
			<button class="btn-primary-inline" onclick={handleAssign} disabled={status === 'assigning'}>
				{#if status === 'assigning'}
					<Loader class="icon-sm spin" /> Assigning…
				{:else}
					<UserPlus class="icon-sm" /> Assign Role
				{/if}
			</button>
			<button class="btn-dismiss" onclick={onDismiss} disabled={status === 'assigning'}>
				<X class="icon-sm" /> Dismiss
			</button>
		{/if}
	</div>
</div>

<style>
	.role-prompt {
		display: flex;
		align-items: center;
		justify-content: space-between;
		gap: 1rem;
		padding: 0.875rem 1rem;
		margin: 0.5rem 0;
		background: #fffbeb;
		border: 1px solid #fde68a;
		border-radius: 0.5rem;
		font-size: 0.875rem;
		transition: all var(--transition-fast);
	}

	.role-prompt.success {
		background: #ecfdf5;
		border-color: #a7f3d0;
	}

	.role-prompt.error {
		background: #fef2f2;
		border-color: #fecaca;
	}

	.prompt-body {
		display: flex;
		align-items: center;
		gap: 0.5rem;
		min-width: 0;
	}

	:global(.icon) {
		width: 1.125rem;
		height: 1.125rem;
		flex-shrink: 0;
		color: #d97706;
	}

	.success :global(.icon) {
		color: #059669;
	}

	.error :global(.icon) {
		color: #dc2626;
	}

	.message {
		color: #92400e;
		line-height: 1.5;
	}

	.success .message {
		color: #065f46;
	}

	.error .message {
		color: #991b1b;
	}

	.message strong {
		font-weight: 600;
	}

	.prompt-actions {
		display: flex;
		align-items: center;
		gap: 0.5rem;
		flex-shrink: 0;
	}

	.btn-primary-inline {
		display: inline-flex;
		align-items: center;
		gap: 0.375rem;
		padding: 0.375rem 0.75rem;
		background: #d97706;
		color: white;
		border: none;
		border-radius: 0.375rem;
		font-size: 0.8125rem;
		font-weight: 500;
		cursor: pointer;
		transition: background var(--transition-fast);
		white-space: nowrap;
	}

	.btn-primary-inline:hover:not(:disabled) {
		background: #b45309;
	}

	.btn-primary-inline:disabled {
		opacity: 0.6;
		cursor: not-allowed;
	}

	.btn-retry {
		display: inline-flex;
		align-items: center;
		gap: 0.375rem;
		padding: 0.375rem 0.75rem;
		background: #dc2626;
		color: white;
		border: none;
		border-radius: 0.375rem;
		font-size: 0.8125rem;
		font-weight: 500;
		cursor: pointer;
		transition: background var(--transition-fast);
		white-space: nowrap;
	}

	.btn-retry:hover {
		background: #b91c1c;
	}

	.btn-dismiss {
		display: inline-flex;
		align-items: center;
		gap: 0.375rem;
		padding: 0.375rem 0.75rem;
		background: transparent;
		color: var(--color-text-secondary);
		border: 1px solid var(--color-border);
		border-radius: 0.375rem;
		font-size: 0.8125rem;
		font-weight: 500;
		cursor: pointer;
		transition: all var(--transition-fast);
		white-space: nowrap;
	}

	.btn-dismiss:hover:not(:disabled) {
		background: var(--color-bg-subtle);
		color: var(--color-text);
	}

	.btn-dismiss:disabled {
		opacity: 0.4;
		cursor: not-allowed;
	}

	:global(.icon-sm) {
		width: 0.875rem;
		height: 0.875rem;
	}

	:global(.spin) {
		animation: spin 0.8s linear infinite;
	}

	.spinner {
		display: flex;
		align-items: center;
		color: #059669;
	}

	@keyframes spin {
		to {
			transform: rotate(360deg);
		}
	}

	@media (max-width: 480px) {
		.role-prompt {
			flex-direction: column;
			align-items: flex-start;
		}
		.prompt-actions {
			width: 100%;
			justify-content: flex-end;
		}
	}
</style>
