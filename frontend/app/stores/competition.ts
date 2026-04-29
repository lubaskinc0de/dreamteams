import { defineStore } from "pinia";
import { useNotificationsStore } from "~/stores/notifications";
import type {
  CompetitionForm,
  UpdateCompetitionGeneralInfoForm,
  RescheduleCompetitionForm,
  ChangeCompetitionArchiveStatusForm,
  CreatedCompetition,
  CompetitionModel,
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
    hasMorePages: (state) => state.competitions.length < state.total,
  },

  actions: {
    async fetchCompetitions(
      page?: number,
      sortBy?: CompetitionSortBy,
      sortOrder?: SortOrder,
      isArchived?: boolean,
      reset = true,
      search?: string,
    ) {
      this.loading = true;
      this.error = null;

      const api = useApi();
      const { data, error } = await api.listCompetitions(
        page || this.currentPage,
        sortBy || this.sortBy,
        sortOrder || this.sortOrder,
        isArchived,
        search,
      );

      if (error) {
        this.error = error;
      } else if (data) {
        if (reset) {
          this.competitions = data.items;
        } else {
          // Append to existing competitions for infinite scroll
          this.competitions = [...this.competitions, ...data.items];
        }
        this.total = data.total;
        this.currentPage = data.page;
        if (sortBy) this.sortBy = sortBy;
        if (sortOrder) this.sortOrder = sortOrder;
      }

      this.loading = false;
    },

    async loadNextPage(isArchived?: boolean, search?: string) {
      if (!this.hasMorePages || this.loading) return;
      await this.fetchCompetitions(this.currentPage + 1, undefined, undefined, isArchived, false, search);
    },

    async updateCompetitionGeneralInfo(
      competitionId: string,
      form: UpdateCompetitionGeneralInfoForm,
    ) {
      const api = useApi();

      this.loading = true;
      this.error = null;

      const { error } = await api.updateCompetitionGeneralInfo(competitionId, form);

      if (error) {
        this.error = error;
        this.loading = false;
        return { success: false, error };
      }

      await this.fetchCompetition(competitionId);

      this.loading = false;
      return { success: true, error: null };
    },

    async rescheduleCompetition(
      competitionId: string,
      form: RescheduleCompetitionForm,
    ) {
      const api = useApi();

      this.loading = true;
      this.error = null;

      const { error } = await api.rescheduleCompetition(competitionId, form);

      if (error) {
        this.error = error;
        this.loading = false;
        return { success: false, error };
      }

      await this.fetchCompetition(competitionId);

      this.loading = false;
      return { success: true, error: null };
    },

    async changeCompetitionArchiveStatus(
      competitionId: string,
      form: ChangeCompetitionArchiveStatusForm,
    ) {
      const api = useApi();

      this.loading = true;
      this.error = null;

      const { error } = await api.changeCompetitionArchiveStatus(competitionId, form);

      if (error) {
        this.error = error;
        this.loading = false;
        return { success: false, error };
      }

      await this.fetchCompetition(competitionId);

      this.loading = false;
      return { success: true, error: null };
    },

    async deleteCompetition(competitionId: string) {
      this.loading = true;
      this.error = null;

      const api = useApi();
      const { error } = await api.deleteCompetition(competitionId);

      if (error) {
        this.error = error;
        this.loading = false;
        return { success: false, error };
      }

      // Remove from local state
      this.competitions = this.competitions.filter((c) => c.id !== competitionId);
      this.total = Math.max(0, this.total - 1);

      this.loading = false;
      return { success: true, error: null };
    },

    async createCompetition(form: CompetitionForm) {
      const { $i18n } = useNuxtApp();
      const notifications = useNotificationsStore();
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

        notifications.add({
          title: $i18n.t("toast.competitionCreated.title"),
          description: $i18n.t("toast.competitionCreated.description"),
          icon: "i-heroicons-check-circle",
          color: "success",
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
