/** Admin routes mapped to the guide section that explains them. First match wins, so list specific paths first. */
const ROUTE_SECTIONS: [RegExp, string][] = [
	[/^\/people\/new\/?$/, 'add-person'],
	[/^\/people\/[^/]+/, 'person-record'],
	[/^\/people\/?$/, 'find-person'],
	[/^\/households/, 'households'],
	[/^\/ministries/, 'ministries-admin'],
	[/^\/rosters/, 'rosters-admin'],
	[/^\/analytics\/attendance/, 'attendance'],
	[/^\/analytics\/(births|deaths)/, 'birth-death'],
	[/^\/analytics/, 'analytics'],
	[/^\/settings\/mass-times/, 'mass-times'],
	[/^\/settings/, 'registration'],
	[/^\/register/, 'registration'],
	[/^\/(announcements|notifications|calendar)/, 'not-yet'],
	[/^\/?$/, 'office-sign-in']
];

/** Default section when a route has no specific help. */
export const DEFAULT_HELP_SECTION = 'h-office';

export function helpSectionFor(pathname: string): string {
	return ROUTE_SECTIONS.find(([pattern]) => pattern.test(pathname))?.[1] ?? DEFAULT_HELP_SECTION;
}

export function helpHref(pathname: string): string {
	return `/help#${helpSectionFor(pathname)}`;
}
