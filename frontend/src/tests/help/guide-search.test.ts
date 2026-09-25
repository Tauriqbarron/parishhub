import { describe, it, expect, beforeEach, vi } from 'vitest';
import guide from '$lib/help/guide.html?raw';
import {
	buildIndex,
	initGuideSearch,
	normalise,
	queryTerms,
	searchIndex,
	snippet
} from '$lib/help/guide-search.js';

const sampleIndex = [
	{
		id: 'sacrament',
		title: 'Record a sacrament',
		part: 'Part A',
		text: 'Choose the Sacrament Type and Date Received.'
	},
	{
		id: 'households',
		title: 'Households',
		part: 'Part A',
		text: 'Add a sacrament note to the household.'
	},
	{ id: 'swap', title: 'Swap with someone', part: 'Part B', text: 'Propose a swap on the roster.' }
];

describe('query handling', () => {
	it('normalises case and whitespace', () => {
		expect(normalise('  Add   PERSON ')).toBe('add person');
	});

	it('drops one-letter terms', () => {
		expect(queryTerms('a roster  x')).toEqual(['roster']);
	});
});

describe('searchIndex', () => {
	it('ranks title matches above body matches', () => {
		const ids = searchIndex(sampleIndex, 'sacrament').map((r) => r.id);
		expect(ids).toEqual(['sacrament', 'households']);
	});

	it('requires every term to match', () => {
		expect(searchIndex(sampleIndex, 'sacrament roster')).toEqual([]);
		expect(searchIndex(sampleIndex, 'swap roster').map((r) => r.id)).toEqual(['swap']);
	});

	it('returns nothing for an empty query', () => {
		expect(searchIndex(sampleIndex, '   ')).toEqual([]);
	});
});

describe('snippet', () => {
	it('marks matching terms', () => {
		expect(snippet('Tap Take Slot to join', ['slot'])).toBe('Tap Take <mark>Slot</mark> to join');
	});

	it('escapes HTML in guide text', () => {
		expect(snippet('<b>Reader</b> role', ['reader'])).toBe(
			'&lt;b&gt;<mark>Reader</mark>&lt;/b&gt; role'
		);
	});

	it('trims long text around the first match with ellipses', () => {
		const text = `${'x'.repeat(200)} target ${'y'.repeat(300)}`;
		const out = snippet(text, ['target']);
		expect(out.startsWith('…')).toBe(true);
		expect(out.endsWith('…')).toBe(true);
		expect(out).toContain('<mark>target</mark>');
	});
});

describe('the real guide', () => {
	beforeEach(() => {
		// jsdom has no layout, so scrolling is a no-op we only need to exist.
		Element.prototype.scrollIntoView = vi.fn();
		document.body.innerHTML = guide;
		initGuideSearch(document);
	});

	it('indexes every task section', () => {
		const index = buildIndex(document);
		expect(index.length).toBeGreaterThan(30);
		expect(index.find((e) => e.id === 'admin-access')?.part).toContain('Part A');
	});

	it('keeps table cells and paragraphs apart and leaves the heading out of the text', () => {
		const entry = buildIndex(document).find((e) => e.id === 'admin-access');
		expect(entry?.text).toContain('What you need · A Google account');
		expect(entry?.text.startsWith('Admin access')).toBe(false);
	});

	it('finds admin access when searching for google account', () => {
		const ids = searchIndex(buildIndex(document), 'google account').map((r) => r.id);
		expect(ids).toContain('admin-access');
	});

	it('shows results as the user types and jumps to one on Enter', () => {
		const input = document.getElementById('guide-search') as HTMLInputElement;
		const list = document.getElementById('guide-results') as HTMLElement;
		input.value = 'mass times';
		input.dispatchEvent(new Event('input'));
		expect(list.hidden).toBe(false);
		expect(list.querySelector('.search-result .search-title')?.textContent).toBe('Mass times');

		input.dispatchEvent(new KeyboardEvent('keydown', { key: 'Enter' }));
		expect(window.location.hash).toBe('#mass-times');
		expect(list.hidden).toBe(true);
	});

	it('scrolls to the section in the URL once the page has loaded', () => {
		window.history.replaceState(null, '', '#households');
		const target = document.getElementById('households')!;
		const spy = vi.fn();
		target.scrollIntoView = spy;
		initGuideSearch(document);
		expect(spy).toHaveBeenCalledWith({ block: 'start', behavior: 'instant' });
	});

	it('hides the results box until there is a query', () => {
		expect(document.getElementById('guide-results')?.hidden).toBe(true);
	});

	it('says so when nothing matches', () => {
		const input = document.getElementById('guide-search') as HTMLInputElement;
		input.value = 'zzqx';
		input.dispatchEvent(new Event('input'));
		expect(document.getElementById('guide-results')?.textContent).toContain('No sections match');
	});

	it('clears on Escape', () => {
		const input = document.getElementById('guide-search') as HTMLInputElement;
		input.value = 'roster';
		input.dispatchEvent(new Event('input'));
		input.dispatchEvent(new KeyboardEvent('keydown', { key: 'Escape' }));
		expect(input.value).toBe('');
		expect(document.getElementById('guide-results')?.hidden).toBe(true);
	});
});
