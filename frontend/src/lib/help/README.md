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

## Regenerating the PDF

Open `/help` while signed in and print to PDF (A4, background graphics on). The print styles hide the contents list and the search box, and keep each task on one page.

## Screenshots

The screenshots come from a local demo database with made-up people. Don't use screenshots of production data.
