import { writable, get } from 'svelte/store';
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

		async fetchList(filters: PersonFilters = {}) {
			update((state) => ({ ...state, loading: true, error: null }));
			try {
				const mergedFilters = { ...initialState.filters, ...filters };
				const response = await personApi.list(mergedFilters);
				update((state) => ({
					...state,
					persons: response.items as unknown as PersonWithRelations[],
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

		async fetchDetail(personId: number) {
			try {
				const person = await personApi.get(personId);
				update((state) => ({
					...state,
					persons: state.persons.map((p) => (p.id === personId ? person : p))
				}));
			} catch (err) {
				update((state) => ({
					...state,
					persons: state.persons.filter((p) => p.id !== personId),
					error: err instanceof Error ? err.message : `Failed to load person ${personId}`
				}));
			}
		},

		async load(filters: PersonFilters = {}) {
			await this.fetchList(filters);
			const { persons } = get(this);
			await Promise.all(persons.map((p) => this.fetchDetail(p.id)));
		},

		async setPage(page: number) {
			update((state) => {
				this.fetchList({ ...state.filters, page });
				return state;
			});
		},

		async setFilters(filters: Partial<PersonFilters>) {
			update((state) => {
				const newFilters = { ...state.filters, ...filters, page: 1 };
				this.fetchList(newFilters);
				return state;
			});
		},

		async setSort(sortBy: PersonFilters['sort_by'], sortOrder: PersonFilters['sort_order']) {
			update((state) => {
				const newFilters = { ...state.filters, sort_by: sortBy, sort_order: sortOrder };
				this.fetchList(newFilters);
				return state;
			});
		},

		reset() {
			set(initialState);
		}
	};
}

export const peopleStore = createPeopleStore();
