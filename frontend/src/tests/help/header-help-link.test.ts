import { describe, it, expect, vi } from 'vitest';
import { render, screen } from '@testing-library/svelte';
import { readable } from 'svelte/store';

vi.mock('$app/stores', () => ({
	page: readable({ url: new URL('http://localhost/people/new') })
}));
vi.mock('@auth/sveltekit/client', () => ({ signOut: vi.fn() }));
vi.mock('$stores/notifications', () => ({
	unreadCount: readable(0),
	startPolling: vi.fn(),
	stopPolling: vi.fn()
}));

import Header from '$components/Header.svelte';

describe('Header help link', () => {
	it('opens the guide in a new tab at the section for the current page', () => {
		render(Header, { props: { session: { user: { email: 'office@example.org' }, expires: '' } } });
		const link = screen.getByTestId('help-link');
		expect(link).toHaveAttribute('href', '/help#add-person');
		expect(link).toHaveAttribute('target', '_blank');
		expect(link).toHaveAttribute('rel', 'noopener');
		expect(link).toHaveAccessibleName('Help for this page (opens in a new tab)');
	});
});
