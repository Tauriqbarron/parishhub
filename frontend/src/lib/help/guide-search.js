// Client-side search for the ParishHub user guide.
// Plain JS so /help can inline it into the served HTML; the pure functions are unit-tested.

const MAX_RESULTS = 8;
const SNIPPET_RADIUS = 70;
const TEXT_BLOCKS = 'p, li, td, th, summary, figcaption';

/** @param {string} value */
export function normalise(value) {
	return value.toLowerCase().replace(/\s+/g, ' ').trim();
}

/** @param {string} query */
export function queryTerms(query) {
	return normalise(query)
		.split(' ')
		.filter((term) => term.length > 1);
}

/**
 * One entry per guide task, keyed by its anchor id.
 * @param {ParentNode} root
 * @returns {{ id: string, title: string, part: string, text: string }[]}
 */
export function buildIndex(root) {
	return Array.from(root.querySelectorAll('section.task[id]')).map((section) => {
		const title = section.querySelector('h3')?.textContent?.trim() ?? '';
		const part = section.closest('section.part')?.querySelector('h2')?.textContent?.trim() ?? '';
		// Read block by block so table cells and list items don't run together.
		const text = Array.from(section.querySelectorAll(TEXT_BLOCKS))
			.map((el) => (el.textContent ?? '').replace(/\s+/g, ' ').trim())
			.filter(Boolean)
			.join(' · ');
		return { id: section.id, title, part, text };
	});
}

/**
 * Every term must appear in the title or body. Title hits outrank body hits.
 * @param {{ id: string, title: string, part: string, text: string }[]} index
 * @param {string} query
 */
export function searchIndex(index, query) {
	const terms = queryTerms(query);
	if (terms.length === 0) return [];

	const results = [];
	for (const entry of index) {
		const title = entry.title.toLowerCase();
		const text = entry.text.toLowerCase();
		let score = 0;
		let matchesAll = true;
		for (const term of terms) {
			const inTitle = title.includes(term);
			const inText = text.includes(term);
			if (!inTitle && !inText) {
				matchesAll = false;
				break;
			}
			if (inTitle) score += 10;
			score += Math.min(text.split(term).length - 1, 5);
		}
		if (matchesAll) results.push({ ...entry, score });
	}
	return results.sort((a, b) => b.score - a.score).slice(0, MAX_RESULTS);
}

/** @param {string} value */
function escapeHtml(value) {
	return value
		.replace(/&/g, '&amp;')
		.replace(/</g, '&lt;')
		.replace(/>/g, '&gt;')
		.replace(/"/g, '&quot;');
}

/** @param {string} value */
function escapeRegExp(value) {
	return value.replace(/[.*+?^${}()|[\]\\]/g, '\\$&');
}

/**
 * Escaped text around the first matching term, with every term wrapped in <mark>.
 * @param {string} text
 * @param {string[]} terms
 */
export function snippet(text, terms) {
	const lower = text.toLowerCase();
	const first = terms.map((t) => lower.indexOf(t)).filter((i) => i >= 0);
	const at = first.length ? Math.min(...first) : 0;
	const start = Math.max(0, at - SNIPPET_RADIUS);
	const end = Math.min(text.length, at + SNIPPET_RADIUS * 2);
	let html = escapeHtml(text.slice(start, end));
	if (terms.length) {
		const pattern = new RegExp(
			`(${terms.map((t) => escapeRegExp(escapeHtml(t))).join('|')})`,
			'gi'
		);
		html = html.replace(pattern, '<mark>$1</mark>');
	}
	return `${start > 0 ? '…' : ''}${html}${end < text.length ? '…' : ''}`;
}

/**
 * Wires the search box. Expects #guide-search (input) and #guide-results (list container).
 * @param {Document} doc
 */
export function initGuideSearch(doc) {
	const inputEl = doc.getElementById('guide-search');
	const listEl = doc.getElementById('guide-results');
	if (!inputEl || !listEl) return;
	const input = /** @type {HTMLInputElement} */ (inputEl);
	const list = listEl;

	const index = buildIndex(doc);
	/** @type {ReturnType<typeof searchIndex>} */
	let results = [];
	let active = -1;

	function close() {
		list.hidden = true;
		list.innerHTML = '';
		input.setAttribute('aria-expanded', 'false');
		active = -1;
	}

	/** @param {string} id */
	function go(id) {
		close();
		input.blur();
		const target = doc.getElementById(id);
		if (!target) return;
		doc.defaultView?.history.replaceState(null, '', `#${id}`);
		const reduceMotion = doc.defaultView?.matchMedia?.('(prefers-reduced-motion: reduce)').matches;
		target.scrollIntoView({ block: 'start', behavior: reduceMotion ? 'instant' : 'smooth' });
		target.classList.remove('search-hit');
		void target.offsetWidth;
		target.classList.add('search-hit');
	}

	function render() {
		const terms = queryTerms(input.value);
		if (terms.length === 0) return close();
		results = searchIndex(index, input.value);
		active = results.length ? 0 : -1;
		list.hidden = false;
		input.setAttribute('aria-expanded', 'true');
		if (results.length === 0) {
			list.innerHTML = `<p class="search-empty">No sections match "${escapeHtml(input.value.trim())}". Try fewer or different words.</p>`;
			return;
		}
		list.innerHTML = results
			.map(
				(r, i) =>
					`<a class="search-result" role="option" id="guide-result-${i}" href="#${r.id}" data-id="${r.id}" aria-selected="${i === active}">` +
					`<span class="search-part">${escapeHtml(r.part)}</span>` +
					`<span class="search-title">${escapeHtml(r.title)}</span>` +
					`<span class="search-snippet">${snippet(r.text, terms)}</span></a>`
			)
			.join('');
	}

	function highlight() {
		list.querySelectorAll('.search-result').forEach((el, i) => {
			el.setAttribute('aria-selected', String(i === active));
			if (i === active) el.scrollIntoView({ block: 'nearest' });
		});
	}

	// Deep links (/help#section) jump before images and fonts settle; jump again once loaded.
	function jumpToHash() {
		const id = decodeURIComponent(doc.defaultView?.location.hash.slice(1) ?? '');
		if (id) doc.getElementById(id)?.scrollIntoView({ block: 'start', behavior: 'instant' });
	}
	if (doc.readyState === 'complete') jumpToHash();
	else doc.defaultView?.addEventListener('load', jumpToHash, { once: true });

	input.addEventListener('input', render);
	input.addEventListener('keydown', (event) => {
		if (event.key === 'ArrowDown' && results.length) {
			event.preventDefault();
			active = (active + 1) % results.length;
			highlight();
		} else if (event.key === 'ArrowUp' && results.length) {
			event.preventDefault();
			active = (active - 1 + results.length) % results.length;
			highlight();
		} else if (event.key === 'Enter' && active >= 0 && results[active]) {
			event.preventDefault();
			go(results[active].id);
		} else if (event.key === 'Escape') {
			input.value = '';
			close();
		}
	});
	list.addEventListener('click', (event) => {
		const link = /** @type {HTMLElement} */ (event.target).closest('.search-result');
		if (!link) return;
		event.preventDefault();
		go(link.getAttribute('data-id') ?? '');
	});
	doc.addEventListener('keydown', (event) => {
		const tag = /** @type {HTMLElement} */ (event.target).tagName;
		if (event.key === '/' && tag !== 'INPUT' && tag !== 'TEXTAREA') {
			event.preventDefault();
			input.focus();
		}
	});
	doc.addEventListener('click', (event) => {
		const target = /** @type {Node} */ (event.target);
		if (!list.contains(target) && target !== input) close();
	});
}
