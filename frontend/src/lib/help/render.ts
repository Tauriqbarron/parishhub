import guide from './guide.html?raw';
import searchScript from './guide-search.js?raw';

const APP_LINK = '<a class="app-link" href="/">&larr; Back to ParishHub</a>';

/**
 * The guide is authored with images at `img/…` so the same file renders standalone next to its
 * images. In the app the images live under `/help/img/`.
 */
export function renderGuide(source: string = guide, script: string = searchScript): string {
	// The guide opens with its <title>, meta, font links and <style>; those belong in <head>.
	const headEnd = source.indexOf('</style>') + '</style>'.length;
	const head = source.slice(0, headEnd);
	const body = source
		.slice(headEnd)
		.replaceAll('src="img/', 'src="/help/img/')
		.replace('<!--HELP:APP-LINK-->', () => APP_LINK)
		// Function replacements, so `$&` and `$1` inside the script are not treated as patterns.
		.replace(
			'<!--HELP:SEARCH-SCRIPT-->',
			() => `<script type="module">\n${script}\ninitGuideSearch(document);\n</script>`
		);
	return `<!doctype html>
<html lang="en-NZ">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1, viewport-fit=cover">
<link rel="icon" href="/favicon.svg">
${head}
</head>
<body>
${body}
</body>
</html>`;
}
