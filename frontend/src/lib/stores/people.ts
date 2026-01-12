import { writable } from 'svelte/store';
import { personApi, type PersonWithRelations, type PersonFilters } from '$lib/api';

interface PeopleState {
	persons: PersonWithRelations[];
	total: number;
	page: number;
	pages: number;
	perPage: number;
	loading: boolean;
	error: string | null;
	filters: PersonFilters;
}

const initialState: PeopleState = {
	persons: [],
	total: 0,
	page: 1,
	pages: 0,
	perPage: 20,
	loading: false,
	error: null,
	filters: {
		sort_by: 'last_name',
		sort_order: 'asc'
	}
};

function createPeopleStore() {
	const { subscribe, set, update } = writable<PeopleState>(initialState);

	return {
		subscribe,

		async load(filters: PersonFilters = {}) {
			update((state) => ({ ...state, loading: true, error: null }));

			try {
				const mergedFilters = { ...initialState.filters, ...filters };
				const response = await personApi.list(mergedFilters);

				const personsWithRelations = await Promise.all(
					response.items.map((person) => personApi.get(person.id))
				);

				update((state) => ({
					...state,
					persons: personsWithRelations,
					total: response.total,
					page: response.page,
					pages: response.pages,
					perPage: response.per_page,
					loading: false,
					filters: mergedFilters
				}));
			} catch (err) {
				update((state) => ({
					...state,
					loading: false,
					error: err instanceof Error ? err.message : 'Failed to load persons'
				}));
			}
		},

		async setPage(page: number) {
			update((state) => {
				this.load({ ...state.filters, page });
				return state;
			});
		},

		async setFilters(filters: Partial<PersonFilters>) {
			update((state) => {
				const newFilters = { ...state.filters, ...filters, page: 1 };
				this.load(newFilters);
				return state;
			});
		},

		async setSort(sortBy: PersonFilters['sort_by'], sortOrder: PersonFilters['sort_order']) {
			update((state) => {
				const newFilters = { ...state.filters, sort_by: sortBy, sort_order: sortOrder };
				this.load(newFilters);
				return state;
			});
		},

		reset() {
			set(initialState);
		}
	};
}

export const peopleStore = createPeopleStore();
