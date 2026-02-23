import type { PreviewCompetitionModel, ApiError } from "~/types/api";

/**
 * Composable for managing preview competitions state
 * Used for public browsing without authentication
 */
export const useCompetitionsPreview = () => {
  const competitions = ref<PreviewCompetitionModel[]>([]);
  const total = ref(0);
  const currentPage = ref(1);
  const loading = ref(false);
  const error = ref<ApiError | null>(null);

  const hasMore = computed(() => competitions.value.length < total.value);

  const loadMore = async () => {
    if (!hasMore.value || loading.value) return;

    loading.value = true;
    error.value = null;

    const api = useApi();
    const { data, error: apiError } = await api.getPreviewCompetitions(
      currentPage.value + 1,
    );

    if (apiError) {
      error.value = apiError;
    } else if (data) {
      competitions.value = [...competitions.value, ...data.items];
      total.value = data.total;
      currentPage.value = data.page;
    }

    loading.value = false;
  };

  const reset = async () => {
    loading.value = true;
    error.value = null;
    competitions.value = [];
    currentPage.value = 1;
    total.value = 0;

    const api = useApi();
    const { data, error: apiError } = await api.getPreviewCompetitions(1);

    if (apiError) {
      error.value = apiError;
    } else if (data) {
      competitions.value = data.items;
      total.value = data.total;
      currentPage.value = data.page;
    }

    loading.value = false;
  };

  return {
    competitions,
    total,
    currentPage,
    loading,
    error,
    hasMore,
    loadMore,
    reset,
  };
};
