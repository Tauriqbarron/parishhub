import { describe, it, expect } from 'vitest';
import guide from '$lib/help/guide.html?raw';
import searchScript from '$lib/help/guide-search.js?raw';
import signInGenerated from '$lib/help/sign-in.generated.html?raw';
import {
	buildSignInPage,
	exportMinistriesGuide,
	MINISTRIES_IMAGE_BASE
} from '../../../scripts/export-guides.mjs';

const parse = (html: string) => new DOMParser().parseFromString(html, 'text/html');
const danglingLinks = (doc: Document) =>
	Array.from(doc.querySelectorAll<HTMLAnchorElement>('a[href^="#"]'))
		.map((a) => a.getAttribute('href')!.slice(1))
		.filter((id) => !doc.getElementById(id));

describe('exportMinistriesGuide', () => {
	const { html, images } = exportMinistriesGuide(guide, searchScript);
	const doc = parse(html);

	it('drops everything marked office-only', () => {
		expect(doc.querySelector('[data-only="office"]')).toBeNull();
		for (const id of ['h-office', 'admin-access', 'sacrament', 'appendix-admins']) {
			expect(doc.getElementById(id), id).toBeNull();
		}
	});

	it('keeps the leader and member sections, including Google account setup', () => {
		for (const id of [
			'sign-in',
			'google-account',
			'accept',
			'take-slot',
			'swap',
			'add-member',
			'template',
			'faq'
		]) {
			expect(doc.getElementById(id), id).not.toBeNull();
		}
	});

	it('leaves no links pointing at removed sections', () => {
		expect(danglingLinks(doc)).toEqual([]);
	});

	it('renumbers the parts once Part A is gone', () => {
		const parts = Array.from(doc.querySelectorAll<HTMLElement>('section.part h2')).map(
			(h) => h.textContent
		);
		expect(parts).toContain('Part A: For members');
		expect(parts).toContain('Part B: For leaders and co-leaders');
		expect(doc.body.textContent).not.toMatch(/Part C\b/);
	});

	it('uses the Ministries cover, and a back link that leaves the frame it is shown in', () => {
		expect(doc.title).toBe('ParishHub Ministries Guide');
		expect(doc.querySelector('#start h1')?.textContent).toBe('ParishHub Ministries');
		const back = doc.querySelector('.app-link');
		expect(back?.getAttribute('href')).toBe('/ministries/');
		expect(back?.getAttribute('target')).toBe('_top');
	});

	it('inlines the search script and points images at the assets folder', () => {
		expect(html).toContain('initGuideSearch(document);');
		const srcs = Array.from(doc.querySelectorAll('img')).map((img) => img.getAttribute('src'));
		expect(srcs.every((src) => src?.startsWith(MINISTRIES_IMAGE_BASE))).toBe(true);
		expect(images).toContain('member-rosters-pending.png');
		expect(images.some((f: string) => f.startsWith('admin-'))).toBe(false);
	});
});

describe.each([
	[
		'office',
		['admin-access', 'google-account', 'problems'],
		['find-person', 'sign-in', 'accept'],
		'/login'
	],
	[
		'ministries',
		['sign-in', 'google-account', 'problems'],
		['admin-access', 'accept', 'add-member'],
		'/ministries/login'
	]
] as const)('buildSignInPage(%s)', (audience, included, excluded, back) => {
	const { html } = buildSignInPage(guide, audience);
	const doc = parse(html);

	it('contains only the sign-in and account setup help', () => {
		for (const id of included) expect(doc.getElementById(id), id).not.toBeNull();
		for (const id of excluded) expect(doc.getElementById(id), id).toBeNull();
		expect(doc.querySelectorAll('section.task').length).toBe(included.length);
	});

	it('includes only the sign-in questions from the FAQ', () => {
		const questions = Array.from(doc.querySelectorAll('#problems summary')).map(
			(s) => s.textContent
		);
		expect(questions.length).toBeGreaterThan(0);
		expect(questions.join(' ')).toMatch(/sign in/i);
		expect(questions.join(' ')).not.toMatch(/RSVP|notifications|swap/i);
	});

	it('has no search, no contents list and no dangling links', () => {
		expect(doc.querySelector('script')).toBeNull();
		expect(doc.querySelector('.toc')).toBeNull();
		expect(danglingLinks(doc)).toEqual([]);
	});

	it('links back to the sign-in page', () => {
		expect(doc.querySelector('a.back')?.getAttribute('href')).toBe(back);
	});
});

describe('generated files', () => {
	it('sign-in.generated.html is up to date with guide.html (run npm run export:guides)', () => {
		expect(signInGenerated).toBe(buildSignInPage(guide, 'office').html);
	});
});
