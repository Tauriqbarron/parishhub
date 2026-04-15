import { writable, get } from 'svelte/store';
import { ministryApi, type Ministry, type MinistryDetail, type MinistryFilters } from '$lib/api';

interface MinistriesState {
	ministries: Ministry[];
	total: number;
	page: number;
	pages: number;
	perPage: number;
	loading: boolean;
	error: string | null;
	filters: MinistryFilters;
	selected: MinistryDetail | null;
}

const initialState: MinistriesState = {
	ministries: [],
	total: 0,
	page: 1,
	pages: 0,
	perPage: 20,
	loading: false,
	error: null,
	filters: {
		sort_by: 'name',
		sort_order: 'asc'
	},
	selected: null
};

function createMinistriesStore() {
	const { subscribe, set, update } = writable<MinistriesState>(initialState);

	return {
		subscribe,

		async fetchList(filters: MinistryFilters = {}) {
			update((state) => ({ ...state, loading: true, error: null }));
			try {
				const mergedFilters = { ...initialState.filters, ...filters };
				const response = await ministryApi.list(mergedFilters);
				update((state) => ({
					...state,
					ministries: response.items,
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
					error: err instanceof Error ? err.message : 'Failed to load ministries'
				}));
			}
		},

		async fetchDetail(id: number) {
			update((state) => ({ ...state, loading: true, error: null }));
			try {
				const ministry = await ministryApi.get(id);
				update((state) => ({
					...state,
					selected: ministry,
					loading: false
				}));
			} catch (err) {
				update((state) => ({
					...state,
					loading: false,
					error: err instanceof Error ? err.message : `Failed to load ministry ${id}`
				}));
			}
		},

		async load(filters: MinistryFilters = {}) {
			await this.fetchList(filters);
		},

		setFilters(filters: Partial<MinistryFilters>) {
			update((state) => ({
				...state,
				filters: { ...state.filters, ...filters, page: 1 }
			}));
			this.fetchList(get({ subscribe }).filters);
		},

		setPage(page: number) {
			update((state) => ({ ...state, filters: { ...state.filters, page } }));
			this.fetchList(get({ subscribe }).filters);
		},

		clearSelected() {
			update((state) => ({ ...state, selected: null }));
		}
	};
}

export const ministriesStore = createMinistriesStore();
