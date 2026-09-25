import { describe, it, expect } from 'vitest';
import guide from '$lib/help/guide.html?raw';
import { helpHref, helpSectionFor, DEFAULT_HELP_SECTION } from '$lib/help/anchors';

describe('helpSectionFor', () => {
	it.each([
		['/', 'office-sign-in'],
		['/people', 'find-person'],
		['/people/', 'find-person'],
		['/people/new', 'add-person'],
		['/people/42', 'person-record'],
		['/households', 'households'],
		['/households/3', 'households'],
		['/ministries/new', 'ministries-admin'],
		['/ministries/1', 'ministries-admin'],
		['/rosters/instances/9', 'rosters-admin'],
		['/analytics', 'analytics'],
		['/analytics/attendance', 'attendance'],
		['/analytics/attendance/new', 'attendance'],
		['/analytics/births/new', 'birth-death'],
		['/analytics/deaths/new', 'birth-death'],
		['/settings', 'registration'],
		['/settings/mass-times', 'mass-times'],
		['/register', 'registration'],
		['/announcements/new', 'not-yet'],
		['/notifications', 'not-yet'],
		['/calendar', 'not-yet']
	])('maps %s to #%s', (path, section) => {
		expect(helpSectionFor(path)).toBe(section);
	});

	it('falls back to the parish office part for unknown routes', () => {
		expect(helpSectionFor('/something-new')).toBe(DEFAULT_HELP_SECTION);
	});

	it('builds a /help link with the section anchor', () => {
		expect(helpHref('/people/new')).toBe('/help#add-person');
	});

	it('only points at sections that exist in the guide', () => {
		const paths = [
			'/',
			'/people',
			'/people/new',
			'/people/1',
			'/households',
			'/ministries',
			'/rosters',
			'/analytics',
			'/analytics/attendance',
			'/analytics/births/new',
			'/settings',
			'/settings/mass-times',
			'/register',
			'/calendar',
			'/nope'
		];
		for (const path of paths) {
			expect(guide, `missing id for ${path}`).toContain(`id="${helpSectionFor(path)}"`);
		}
	});
});
