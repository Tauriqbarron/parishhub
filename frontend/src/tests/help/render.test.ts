import { describe, it, expect } from 'vitest';
import { renderGuide } from '$lib/help/render';
import searchScript from '$lib/help/guide-search.js?raw';

describe('renderGuide', () => {
	const html = renderGuide();

	it('returns a full HTML document with the guide styles in head', () => {
		expect(html.startsWith('<!doctype html>')).toBe(true);
		const head = html.slice(0, html.indexOf('</head>'));
		expect(head).toContain('<title>ParishHub User Guide</title>');
		expect(head).toContain('</style>');
	});

	it('points images at /help/img', () => {
		expect(html).toContain('src="/help/img/admin-dashboard.png"');
		expect(html).not.toContain('src="img/');
	});

	it('adds the link back to ParishHub', () => {
		expect(html).toContain('<a class="app-link" href="/">');
		expect(html).not.toContain('<!--HELP:');
	});

	it('inlines the search script unchanged', () => {
		expect(html).toContain(searchScript);
		expect(html).toContain('initGuideSearch(document);');
	});

	it('does not treat $ sequences in the script as replacement patterns', () => {
		const out = renderGuide('<style></style><!--HELP:SEARCH-SCRIPT-->', "x.replace(/a/, '$&-$1')");
		expect(out).toContain("x.replace(/a/, '$&-$1')");
	});
});
