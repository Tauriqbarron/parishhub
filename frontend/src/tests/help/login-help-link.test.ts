import { describe, it, expect, vi } from 'vitest';
import { render, screen } from '@testing-library/svelte';
import { readable } from 'svelte/store';

vi.mock('$app/stores', () => ({ page: readable({ url: new URL('http://localhost/login') }) }));
vi.mock('@auth/sveltekit/client', () => ({ signIn: vi.fn() }));

import LoginPage from '../../routes/login/+page.svelte';

describe('Login page', () => {
	it('links to the public access help', () => {
		render(LoginPage);
		const link = screen.getByTestId('login-help-link');
		expect(link).toHaveTextContent('How to get access');
		expect(link).toHaveAttribute('href', '/help/sign-in');
	});
});
