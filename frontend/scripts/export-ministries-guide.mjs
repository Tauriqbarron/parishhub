// Builds the leaders-and-members edition of the user guide for the ParishHub Ministries app
// (Tauriqbarron/parishhub-ministries), from the same source as the admin /help page.
//
//   node scripts/export-ministries-guide.mjs <ministries-repo>/public/help
//
// Writes index.html plus the screenshots it uses into the target folder.

import { JSDOM } from 'jsdom';
import fs from 'node:fs';
import path from 'node:path';
import { fileURLToPath } from 'node:url';

const IMAGE_BASE = '/ministries/help/img/';
const APP_LINK = '<a class="app-link" href="/ministries/">&larr; Back to Ministries</a>';

const COVER = {
	title: 'ParishHub Ministries Guide',
	eyebrow: 'Guide for ministry leaders and members',
	heading: 'ParishHub Ministries',
	lede: "ParishHub Ministries is where your ministry keeps its events, its member list and its rosters. You can see when you're rostered on, take an open slot, and swap with someone if you can't make it."
};

/** Parts renumber once Part A (the parish office) is removed. */
const PART_LETTERS = { B: 'A', C: 'B' };

/**
 * @param {string} guideHtml source of src/lib/help/guide.html
 * @param {string} searchJs source of src/lib/help/guide-search.js
 * @returns {{ html: string, images: string[] }}
 */
export function exportMinistriesGuide(guideHtml, searchJs) {
	const withSlots = guideHtml
		.replace('<!--HELP:APP-LINK-->', () => APP_LINK)
		.replace(
			'<!--HELP:SEARCH-SCRIPT-->',
			() => `<script type="module">\n${searchJs}\ninitGuideSearch(document);\n</script>`
		);
	const dom = new JSDOM(
		`<!doctype html><html lang="en-NZ"><head></head><body>${withSlots}</body></html>`
	);
	const doc = dom.window.document;

	// The source starts with its <title>, meta, links and <style>; move them into <head>.
	for (const el of Array.from(
		doc.body.querySelectorAll(':scope > title, :scope > meta, :scope > link, :scope > style')
	)) {
		doc.head.appendChild(el);
	}
	const charset = doc.createElement('meta');
	charset.setAttribute('charset', 'utf-8');
	const viewport = doc.createElement('meta');
	viewport.name = 'viewport';
	viewport.content = 'width=device-width, initial-scale=1, viewport-fit=cover';
	doc.head.prepend(charset, viewport);

	doc.querySelectorAll('[data-only="office"]').forEach((el) => el.remove());

	// Links into removed sections become plain text.
	doc.querySelectorAll('a[href^="#"]').forEach((a) => {
		const id = a.getAttribute('href')?.slice(1);
		if (id && !doc.getElementById(id)) a.replaceWith(...Array.from(a.childNodes));
	});

	doc.title = COVER.title;
	const cover = doc.getElementById('start');
	if (cover) {
		const eyebrow = cover.querySelector('.eyebrow');
		const heading = cover.querySelector('h1');
		const lede = cover.querySelector('.lede');
		if (eyebrow) eyebrow.textContent = COVER.eyebrow;
		if (heading) heading.textContent = COVER.heading;
		if (lede) lede.textContent = COVER.lede;
	}
	const brand = doc.querySelector('.toc .brand');
	if (brand?.lastChild) brand.lastChild.textContent = ' ParishHub Ministries Guide ';

	// Renumber part letters in visible text (not inside the search script).
	const walker = doc.createTreeWalker(doc.body, dom.window.NodeFilter.SHOW_TEXT);
	for (let node = walker.nextNode(); node; node = walker.nextNode()) {
		if (node.parentElement?.closest('script, style')) continue;
		node.textContent = (node.textContent ?? '').replace(
			/\bPart ([BC])\b/g,
			(_, letter) => `Part ${PART_LETTERS[/** @type {'B' | 'C'} */ (letter)]}`
		);
	}

	const images = Array.from(
		new Set(
			Array.from(doc.querySelectorAll('img[src^="img/"]')).map((img) =>
				(img.getAttribute('src') ?? '').slice('img/'.length)
			)
		)
	).sort();

	// The app serves the guide at /ministries/help (no trailing slash), so relative img/ paths
	// would resolve to /ministries/img/. Point them at the folder they are copied to.
	doc.querySelectorAll('img[src^="img/"]').forEach((img) => {
		img.setAttribute('src', `${IMAGE_BASE}${img.getAttribute('src')?.slice('img/'.length)}`);
	});

	return { html: dom.serialize(), images };
}

function main() {
	const out = process.argv[2];
	if (!out) {
		console.error('Usage: node scripts/export-ministries-guide.mjs <output-folder>');
		process.exit(1);
	}
	const root = path.resolve(path.dirname(fileURLToPath(import.meta.url)), '..');
	const guide = fs.readFileSync(path.join(root, 'src/lib/help/guide.html'), 'utf8');
	const search = fs.readFileSync(path.join(root, 'src/lib/help/guide-search.js'), 'utf8');
	const { html, images } = exportMinistriesGuide(guide, search);

	fs.rmSync(path.join(out, 'img'), { recursive: true, force: true });
	fs.mkdirSync(path.join(out, 'img'), { recursive: true });
	fs.writeFileSync(path.join(out, 'index.html'), html);
	for (const file of images) {
		fs.copyFileSync(path.join(root, 'static/help/img', file), path.join(out, 'img', file));
	}
	console.log(`Wrote ${path.join(out, 'index.html')} and ${images.length} images`);
}

if (process.argv[1] && path.resolve(process.argv[1]) === fileURLToPath(import.meta.url)) main();
