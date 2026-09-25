// Builds the generated guide files from src/lib/help/guide.html.
//
//   node scripts/export-guides.mjs                         admin sign-in page only
//   node scripts/export-guides.mjs --ministries <repo>     also the ParishHub Ministries files
//
// Admin app (this repo):
//   src/lib/help/sign-in.generated.html   public sign-in and access help, served at /help/sign-in
// Ministries app (Tauriqbarron/parishhub-ministries):
//   src/help/guide.generated.ts           full leaders-and-members guide, served only to signed-in users
//   public/help-assets/sign-in.html       public sign-in help, served at /ministries/help/sign-in
//   public/help-assets/img/               screenshots used by both

import { JSDOM } from 'jsdom';
import fs from 'node:fs';
import path from 'node:path';
import { fileURLToPath } from 'node:url';

export const MINISTRIES_IMAGE_BASE = '/ministries/help-assets/img/';
export const ADMIN_IMAGE_BASE = '/help/img/';

const MINISTRIES_COVER = {
	title: 'ParishHub Ministries Guide',
	eyebrow: 'Guide for ministry leaders and members',
	heading: 'ParishHub Ministries',
	lede: "ParishHub Ministries is where your ministry keeps its events, its member list and its rosters. You can see when you're rostered on, take an open slot, and swap with someone if you can't make it."
};

const SIGN_IN_PAGES = {
	office: {
		title: 'Getting access to ParishHub',
		heading: 'Getting access to ParishHub',
		lede: 'ParishHub at parishhub.net is for parish office staff and clergy. You need a Google account, and your ParishHub administrator has to add its email to the approved list.',
		backHref: '/login',
		backLabel: 'Back to sign in',
		imageBase: ADMIN_IMAGE_BASE
	},
	ministries: {
		title: 'Signing in to ParishHub Ministries',
		heading: 'Signing in to ParishHub Ministries',
		lede: 'ParishHub Ministries is for ministry leaders and members. You sign in with a Google account, and your ministry leader has to add you to a ministry first.',
		backHref: '/ministries/login',
		backLabel: 'Back to sign in',
		imageBase: MINISTRIES_IMAGE_BASE
	}
};

/** Parts renumber once Part A (the parish office) is removed. */
const PART_LETTERS = { B: 'A', C: 'B' };

/** @param {string} html */
function parse(html) {
	const dom = new JSDOM(
		`<!doctype html><html lang="en-NZ"><head></head><body>${html}</body></html>`
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
	return { dom, doc };
}

/**
 * Links to sections that aren't on the page become plain text.
 * @param {Document} doc
 */
function unwrapDanglingLinks(doc) {
	doc.querySelectorAll('a[href^="#"]').forEach((a) => {
		const id = a.getAttribute('href')?.slice(1);
		if (id && !doc.getElementById(id)) a.replaceWith(...Array.from(a.childNodes));
	});
}

/**
 * @param {Document} doc
 * @param {string} base
 */
function pointImagesAt(doc, base) {
	doc.querySelectorAll('img[src^="img/"]').forEach((img) => {
		img.setAttribute('src', `${base}${img.getAttribute('src')?.slice('img/'.length)}`);
	});
}

/**
 * @param {Document} doc
 * @param {string} base
 */
function imagesIn(doc, base) {
	return Array.from(
		new Set(
			Array.from(doc.querySelectorAll('img'))
				.map((img) => img.getAttribute('src') ?? '')
				.filter((src) => src.startsWith(base))
				.map((src) => src.slice(base.length))
		)
	).sort();
}

/**
 * The leaders-and-members edition: everything except the parish office content.
 * @param {string} guideHtml source of src/lib/help/guide.html
 * @param {string} searchJs source of src/lib/help/guide-search.js
 * @returns {{ html: string, images: string[] }}
 */
export function exportMinistriesGuide(guideHtml, searchJs) {
	const withSlots = guideHtml
		.replace(
			'<!--HELP:APP-LINK-->',
			() => '<a class="app-link" href="/ministries/" target="_top">&larr; Back to Ministries</a>'
		)
		.replace(
			'<!--HELP:SEARCH-SCRIPT-->',
			() => `<script type="module">\n${searchJs}\ninitGuideSearch(document);\n</script>`
		);
	const { dom, doc } = parse(withSlots);

	doc.querySelectorAll('[data-only="office"]').forEach((el) => el.remove());
	unwrapDanglingLinks(doc);

	doc.title = MINISTRIES_COVER.title;
	const cover = doc.getElementById('start');
	if (cover) {
		const eyebrow = cover.querySelector('.eyebrow');
		const heading = cover.querySelector('h1');
		const lede = cover.querySelector('.lede');
		if (eyebrow) eyebrow.textContent = MINISTRIES_COVER.eyebrow;
		if (heading) heading.textContent = MINISTRIES_COVER.heading;
		if (lede) lede.textContent = MINISTRIES_COVER.lede;
	}
	const brand = doc.querySelector('.toc .brand');
	if (brand?.lastChild) brand.lastChild.textContent = ' ParishHub Ministries Guide ';

	// Renumber part letters in visible text (not inside the search script).
	const walker = doc.createTreeWalker(doc.body, dom.window.NodeFilter.SHOW_TEXT);
	for (let node = walker.nextNode(); node; node = walker.nextNode()) {
		if (node.parentElement?.closest('script, style')) continue;
		node.textContent = (node.textContent ?? '').replace(
			/\bPart ([BC])\b/g,
			(_, /** @type {'B' | 'C'} */ letter) => `Part ${PART_LETTERS[letter]}`
		);
	}

	// Served at /ministries/help, so relative img/ paths would resolve to /ministries/img/.
	pointImagesAt(doc, MINISTRIES_IMAGE_BASE);
	return { html: dom.serialize(), images: imagesIn(doc, MINISTRIES_IMAGE_BASE) };
}

/**
 * The public page: only the sections tagged data-public for this app (or "both"), plus the
 * matching sign-in questions from the FAQ. Everything else stays behind sign-in.
 * @param {string} guideHtml
 * @param {'office' | 'ministries'} audience
 * @returns {{ html: string, images: string[] }}
 */
export function buildSignInPage(guideHtml, audience) {
	const page = SIGN_IN_PAGES[audience];
	const { doc } = parse(guideHtml);
	const wanted = (/** @type {Element} */ el) =>
		[audience, 'both'].includes(el.getAttribute('data-public') ?? '');

	const sections = Array.from(doc.querySelectorAll('section.task[data-public]')).filter(wanted);
	const questions = Array.from(doc.querySelectorAll('details[data-public]')).filter(wanted);

	const out = new JSDOM('<!doctype html><html lang="en-NZ"><head></head><body></body></html>')
		.window.document;
	for (const el of Array.from(doc.head.children)) out.head.appendChild(out.importNode(el, true));
	out.title = page.title;
	const narrow = out.createElement('style');
	narrow.textContent =
		'.page { display: block; max-width: 760px; } .cover { padding-top: 24px; } .back { display: inline-block; margin-top: 24px; font-weight: 600; text-decoration: none; }';
	out.head.appendChild(narrow);

	const wrapper = out.createElement('div');
	wrapper.className = 'page';
	const main = out.createElement('main');
	wrapper.appendChild(main);
	out.body.appendChild(wrapper);

	const back = out.createElement('a');
	back.className = 'back';
	back.href = page.backHref;
	back.innerHTML = `&larr; ${page.backLabel}`;
	main.appendChild(back);

	const header = out.createElement('header');
	header.className = 'cover';
	const eyebrow = out.createElement('div');
	eyebrow.className = 'eyebrow';
	eyebrow.textContent = 'Help';
	const heading = out.createElement('h1');
	heading.textContent = page.heading;
	const lede = out.createElement('p');
	lede.className = 'lede';
	lede.textContent = page.lede;
	header.append(eyebrow, heading, lede);
	main.appendChild(header);

	const part = out.createElement('section');
	part.className = 'part';
	for (const section of sections) {
		const copy = out.importNode(section, true);
		copy.removeAttribute('data-public');
		part.appendChild(copy);
	}
	if (questions.length) {
		const faq = out.createElement('section');
		faq.className = 'task';
		faq.id = 'problems';
		const title = out.createElement('h3');
		title.textContent = 'Problems signing in';
		const list = out.createElement('div');
		list.className = 'faq';
		for (const q of questions) {
			const copy = out.importNode(q, true);
			copy.removeAttribute('data-public');
			list.appendChild(copy);
		}
		faq.append(title, list);
		part.appendChild(faq);
	}
	const after = out.createElement('p');
	after.className = 'meta';
	after.style.marginTop = '24px';
	after.textContent = 'Once you are signed in, open Help for the full guide.';
	part.appendChild(after);
	main.appendChild(part);

	unwrapDanglingLinks(out);
	pointImagesAt(out, page.imageBase);
	return {
		html: `<!doctype html>\n${out.documentElement.outerHTML}\n`,
		images: imagesIn(out, page.imageBase)
	};
}

function main() {
	const root = path.resolve(path.dirname(fileURLToPath(import.meta.url)), '..');
	const read = (/** @type {string} */ p) => fs.readFileSync(path.join(root, p), 'utf8');
	const guide = read('src/lib/help/guide.html');
	const search = read('src/lib/help/guide-search.js');

	const office = buildSignInPage(guide, 'office');
	fs.writeFileSync(path.join(root, 'src/lib/help/sign-in.generated.html'), office.html);
	console.log('Wrote src/lib/help/sign-in.generated.html');

	const flag = process.argv.indexOf('--ministries');
	if (flag === -1) return;
	const repo = process.argv[flag + 1];
	if (!repo) {
		console.error('Usage: node scripts/export-guides.mjs --ministries <ministries-repo>');
		process.exit(1);
	}

	const full = exportMinistriesGuide(guide, search);
	const signIn = buildSignInPage(guide, 'ministries');
	const assets = path.join(repo, 'public/help-assets');
	fs.rmSync(assets, { recursive: true, force: true });
	fs.rmSync(path.join(repo, 'public/help'), { recursive: true, force: true });
	fs.mkdirSync(path.join(assets, 'img'), { recursive: true });
	fs.mkdirSync(path.join(repo, 'src/help'), { recursive: true });

	fs.writeFileSync(
		path.join(repo, 'src/help/guide.generated.ts'),
		`// Generated by scripts/export-guides.mjs in Tauriqbarron/parishhub. Do not edit.\n` +
			`export const GUIDE_HTML = ${JSON.stringify(full.html)};\n`
	);
	fs.writeFileSync(path.join(assets, 'sign-in.html'), signIn.html);
	const images = Array.from(new Set([...full.images, ...signIn.images])).sort();
	for (const file of images) {
		fs.copyFileSync(path.join(root, 'static/help/img', file), path.join(assets, 'img', file));
	}
	console.log(`Wrote the Ministries guide, sign-in page and ${images.length} images to ${repo}`);
}

if (process.argv[1] && path.resolve(process.argv[1]) === fileURLToPath(import.meta.url)) main();
