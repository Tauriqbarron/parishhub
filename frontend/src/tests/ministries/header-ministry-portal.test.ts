import { describe, it, expect, vi } from 'vitest';
import { render, screen } from '@testing-library/svelte';
import { readable } from 'svelte/store';

vi.mock('$app/stores', () => ({
	page: readable({ url: new URL('http://localhost/people') })
}));
vi.mock('@auth/sveltekit/client', () => ({ signOut: vi.fn() }));
vi.mock('$stores/notifications', () => ({
	unreadCount: readable(0),
	startPolling: vi.fn(),
	stopPolling: vi.fn()
}));

import Header from '$components/Header.svelte';

describe('Header ministry portal link', () => {
	it('reaches the ministries app in the same tab', () => {
		render(Header, { props: { session: { user: { email: 'office@example.org' }, expires: '' } } });
		const link = screen.getByTestId('ministry-portal-link');
		expect(link).toHaveAttribute('href', '/ministries');
		expect(link).not.toHaveAttribute('target');
		expect(link).toHaveAccessibleName('Open the Ministry Portal');
	});

	it('forces a full page load so the nginx proxy serves the ministries app', () => {
		render(Header, { props: { session: { user: { email: 'office@example.org' }, expires: '' } } });
		expect(screen.getByTestId('ministry-portal-link')).toHaveAttribute('data-sveltekit-reload');
	});
});
