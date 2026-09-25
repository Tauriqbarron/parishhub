# ParishHub User Guide

The guide for the parish office, ministry leaders and members.

- **In the app:** signed-in admins open it from the **Help** button in the header. The button links to `/help#<section>` for the page they're on, and the guide has a search box.
- **Source:** `frontend/src/lib/help/guide.html`. The screenshots it uses are in `frontend/static/help/img/`.
- **PDF:** not kept in git (6 MB). Generate it from `/help` as below.

## Editing the guide

1. Edit `frontend/src/lib/help/guide.html`. Each task is a `<section class="task" id="…">`. The search indexes these sections, and the Help button links to their ids.
2. If you rename or remove a section id, update `frontend/src/lib/help/anchors.ts`. A test fails if a route points at an id that doesn't exist.
3. Reference images as `img/<file>.png` and include their `width` and `height`. The width and height stop the page shifting after a deep link has jumped to a section.
4. Run `npm test -- src/tests/help` in `frontend/`.

## What's public

Only sign-in and account setup help is public. Everything else needs a sign-in.

| Page                       | Who can open it                                                                                                     | Built from                                        |
| -------------------------- | ------------------------------------------------------------------------------------------------------------------- | ------------------------------------------------- |
| `/help` (admin)            | Signed-in admins on the allowlist                                                                                   | `guide.html`, served by `routes/help/+server.ts`  |
| `/help/sign-in` (admin)    | Anyone                                                                                                              | `sign-in.generated.html`                          |
| `/ministries/help`         | Signed-in Ministries users. The page fetches the guide with the user's token; the server checks it with the backend | Ministries repo `src/help/guide.generated.ts`     |
| `/ministries/help/sign-in` | Anyone                                                                                                              | Ministries repo `public/help-assets/sign-in.html` |

Sections and FAQ entries go on the public pages by tag:

- `data-public="office"` puts it on the admin sign-in page.
- `data-public="ministries"` puts it on the Ministries one.
- `data-public="both"` puts it on both.

`data-only="office"` keeps an element out of the Ministries edition.

The screenshot files are the exception to "everything needs a sign-in". They're plain static files in both apps, so anyone with the exact URL can open them. They show demo data only.

## Regenerating the generated files

After editing `guide.html`, run from `frontend/`:

```bash
npm run export:guides -- --ministries ../../parishhub-ministries
```

This rewrites `sign-in.generated.html` here, and the guide, sign-in page and screenshots in the Ministries repo. Commit both repos. A test fails if `sign-in.generated.html` is out of date.

## Regenerating the PDF

Open `/help` while signed in and print to PDF (A4, background graphics on). The print styles hide the contents list and the search box, and keep each task on one page.

## Screenshots

The screenshots come from a local demo database with made-up people. Don't use screenshots of production data.
