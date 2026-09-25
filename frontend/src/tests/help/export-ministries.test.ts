import { describe, it, expect } from 'vitest';
import guide from '$lib/help/guide.html?raw';
import searchScript from '$lib/help/guide-search.js?raw';
import { exportMinistriesGuide } from '../../../scripts/export-ministries-guide.mjs';

const { html, images } = exportMinistriesGuide(guide, searchScript) as {
	html: string;
	images: string[];
};
const doc = new DOMParser().parseFromString(html, 'text/html');

describe('exportMinistriesGuide', () => {
	it('drops everything marked office-only', () => {
		expect(doc.querySelector('[data-only="office"]')).toBeNull();
		for (const id of ['h-office', 'admin-access', 'sacrament', 'appendix-admins']) {
			expect(doc.getElementById(id), id).toBeNull();
		}
	});

	it('keeps the leader and member sections', () => {
		for (const id of ['sign-in', 'accept', 'take-slot', 'swap', 'add-member', 'template', 'faq']) {
			expect(doc.getElementById(id), id).not.toBeNull();
		}
	});

	it('leaves no links pointing at removed sections', () => {
		const dangling = Array.from(doc.querySelectorAll<HTMLAnchorElement>('a[href^="#"]'))
			.map((a) => a.getAttribute('href')!.slice(1))
			.filter((id) => !doc.getElementById(id));
		expect(dangling).toEqual([]);
	});

	it('renumbers the parts once Part A is gone', () => {
		const parts = Array.from(doc.querySelectorAll<HTMLElement>('section.part h2')).map(
			(h) => h.textContent
		);
		expect(parts).toContain('Part A: For members');
		expect(parts).toContain('Part B: For leaders and co-leaders');
		expect(doc.body.textContent).not.toMatch(/Part C\b/);
	});

	it('uses the Ministries title, cover and back link', () => {
		expect(doc.title).toBe('ParishHub Ministries Guide');
		expect(doc.querySelector('#start h1')?.textContent).toBe('ParishHub Ministries');
		expect(doc.querySelector('.app-link')?.getAttribute('href')).toBe('/ministries/');
	});

	it('puts the styles in head and inlines the search script', () => {
		expect(doc.head.querySelector('style')).not.toBeNull();
		expect(doc.head.querySelector('meta[name="viewport"]')).not.toBeNull();
		expect(html).toContain('initGuideSearch(document);');
		expect(html).not.toContain('<!--HELP:');
	});

	it('points images at the folder the app serves them from', () => {
		const srcs = Array.from(doc.querySelectorAll('img')).map((img) => img.getAttribute('src'));
		expect(srcs.length).toBeGreaterThan(20);
		expect(srcs.every((src) => src?.startsWith('/ministries/help/img/'))).toBe(true);
	});

	it('lists only the screenshots the edition uses', () => {
		expect(images).toContain('member-rosters-pending.png');
		expect(images.some((f) => f.startsWith('admin-'))).toBe(false);
	});
});
