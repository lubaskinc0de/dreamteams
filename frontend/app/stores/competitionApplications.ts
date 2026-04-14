import { defineStore } from "pinia";
import type { ApplicationModel, ApplicationsList, ApiError } from "~/types/api";

export const useCompetitionApplicationsStore = defineStore("competitionApplications", {
  state: () => ({
    applications: [] as ApplicationModel[],
    total: 0,
    page: 1,
    loading: false,
    currentApplication: null as ApplicationModel | null,
    acting: false,
    error: null as ApiError | null,
  }),

  actions: {
    async fetchApplications(competitionId: string, page: number = 1) {
      this.loading = true;
      this.error = null;

      const api = useApi();
      const { data, error } = await api.listApplicationsByCompetition(competitionId, page);

      if (error) {
        this.error = error;
      } else if (data) {
        this.applications = data.items;
        this.total = data.total;
        this.page = data.page;
      }

      this.loading = false;
    },

    async fetchApplication(applicationId: string) {
      this.loading = true;
      this.error = null;

      const api = useApi();
      const { data, error } = await api.readApplication(applicationId);

      if (error) {
        this.error = error;
      } else {
        this.currentApplication = data;
      }

      this.loading = false;
    },

    async accept(applicationId: string): Promise<boolean> {
      this.acting = true;
      this.error = null;

      const api = useApi();
      const { error } = await api.acceptApplication(applicationId);

      this.acting = false;

      if (error) {
        this.error = error;
        return false;
      }

      if (this.currentApplication?.id === applicationId) {
        this.currentApplication = { ...this.currentApplication, status: "accepted" };
      }

      const item = this.applications.find((a) => a.id === applicationId);
      if (item) {
        item.status = "accepted";
      }

      return true;
    },

    async reject(applicationId: string): Promise<boolean> {
      this.acting = true;
      this.error = null;

      const api = useApi();
      const { error } = await api.rejectApplication(applicationId);

      this.acting = false;

      if (error) {
        this.error = error;
        return false;
      }

      if (this.currentApplication?.id === applicationId) {
        this.currentApplication = { ...this.currentApplication, status: "rejected" };
      }

      const item = this.applications.find((a) => a.id === applicationId);
      if (item) {
        item.status = "rejected";
      }

      return true;
    },

    clearError() {
      this.error = null;
    },
  },
});
