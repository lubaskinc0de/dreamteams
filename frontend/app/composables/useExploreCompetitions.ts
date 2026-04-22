import type { ExploreCompetitionModel, ExploreCompetitionsFilters, ApiError } from "~/types/api";

export const useExploreCompetitions = () => {
  const competitions = ref<ExploreCompetitionModel[]>([]);
  const total = ref(0);
  const currentPage = ref(1);
  const loading = ref(false);
  const error = ref<ApiError | null>(null);
  const filters = ref<ExploreCompetitionsFilters>({ sort_by: "most_popular" });

  const hasMore = computed(() => competitions.value.length < total.value);

  const fetchPage = async (page: number, append: boolean) => {
    loading.value = true;
    error.value = null;

    const api = useApi();
    const { data, error: apiError } = await api.exploreCompetitions({
      ...filters.value,
      page,
    });

    if (apiError) {
      error.value = apiError;
    } else if (data) {
      competitions.value = append ? [...competitions.value, ...data.items] : data.items;
      total.value = data.total;
      currentPage.value = data.page;
    }

    loading.value = false;
  };

  const applyFilters = async (next: ExploreCompetitionsFilters) => {
    filters.value = { ...next, sort_by: next.sort_by ?? "most_popular" };
    await fetchPage(1, false);
  };

  const loadMore = async () => {
    if (!hasMore.value || loading.value) return;
    await fetchPage(currentPage.value + 1, true);
  };

  const reset = async () => {
    competitions.value = [];
    total.value = 0;
    currentPage.value = 1;
    await fetchPage(1, false);
  };

  return {
    competitions,
    total,
    currentPage,
    loading,
    error,
    hasMore,
    filters,
    applyFilters,
    loadMore,
    reset,
  };
};
