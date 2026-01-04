import { defineStore } from "pinia";
import type {
  CompetitionForm,
  CreatedCompetition,
  CompetitionModel,
  CompetitionsList,
  CompetitionSortBy,
  SortOrder,
  ApiError,
} from "~/types/api";

export const useCompetitionStore = defineStore("competition", {
  state: () => ({
    competitions: [] as CompetitionModel[],
    currentCompetition: null as CompetitionModel | null,
    total: 0,
    currentPage: 1,
    sortBy: "created_at" as CompetitionSortBy,
    sortOrder: "desc" as SortOrder,
    loading: false,
    creationSuccess: false,
    createdCompetition: null as CreatedCompetition | null,
    error: null as ApiError | null,
  }),

  getters: {
    hasCompetitions: (state) => state.competitions.length > 0,
  },

  actions: {
    async fetchCompetitions(
      page?: number,
      sortBy?: CompetitionSortBy,
      sortOrder?: SortOrder,
    ) {
      this.loading = true;
      this.error = null;

      const api = useApi();
      const { data, error } = await api.listCompetitions(
        page || this.currentPage,
        sortBy || this.sortBy,
        sortOrder || this.sortOrder,
      );

      if (error) {
        this.error = error;
      } else if (data) {
        this.competitions = data.items;
        this.total = data.total;
        this.currentPage = data.page;
        if (sortBy) this.sortBy = sortBy;
        if (sortOrder) this.sortOrder = sortOrder;
      }

      this.loading = false;
    },

    async createCompetition(form: CompetitionForm) {
      const { $i18n } = useNuxtApp();
      const toast = useToast();
      const api = useApi();

      this.loading = true;
      this.error = null;
      this.creationSuccess = false;

      const { data, error } = await api.createCompetition(form);

      if (error) {
        this.error = error;
      } else {
        this.createdCompetition = data;
        this.creationSuccess = true;

        toast.add({
          title: $i18n.t("toast.competitionCreated.title"),
          description: $i18n.t("toast.competitionCreated.description"),
          icon: "i-heroicons-check-circle",
          color: "success",
          duration: 5000,
        });

        // Refresh the list
        await this.fetchCompetitions();
      }

      this.loading = false;
    },

    async fetchCompetition(competitionId: string) {
      this.loading = true;
      this.error = null;

      const api = useApi();
      const { data, error } = await api.getCompetition(competitionId);

      if (error) {
        this.error = error;
      } else {
        this.currentCompetition = data;
      }

      this.loading = false;
    },

    clearError() {
      this.error = null;
    },

    reset() {
      this.creationSuccess = false;
      this.createdCompetition = null;
      this.error = null;
    },
  },
});
