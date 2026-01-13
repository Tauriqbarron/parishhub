import { writable } from 'svelte/store';
import { householdApi, type Household, type HouseholdFilters } from '$lib/api';

interface HouseholdsState {
	households: Household[];
	total: number;
	page: number;
	pages: number;
	perPage: number;
	loading: boolean;
	error: string | null;
	filters: HouseholdFilters;
}

const initialState: HouseholdsState = {
	households: [],
	total: 0,
	page: 1,
	pages: 0,
	perPage: 20,
	loading: false,
	error: null,
	filters: {
		sort_by: 'name',
		sort_order: 'asc'
	}
};

function createHouseholdsStore() {
	const { subscribe, set, update } = writable<HouseholdsState>(initialState);

	return {
		subscribe,

		async load(filters: HouseholdFilters = {}) {
			update((state) => ({ ...state, loading: true, error: null }));

			try {
				const mergedFilters = { ...initialState.filters, ...filters };
				const response = await householdApi.list(mergedFilters);

				update((state) => ({
					...state,
					households: response.items,
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
					error: err instanceof Error ? err.message : 'Failed to load households'
				}));
			}
		},

		async setPage(page: number) {
			update((state) => {
				this.load({ ...state.filters, page });
				return state;
			});
		},

		async setFilters(filters: Partial<HouseholdFilters>) {
			update((state) => {
				const newFilters = { ...state.filters, ...filters, page: 1 };
				this.load(newFilters);
				return state;
			});
		},

		async setSort(sortBy: HouseholdFilters['sort_by'], sortOrder: HouseholdFilters['sort_order']) {
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

export const householdsStore = createHouseholdsStore();
