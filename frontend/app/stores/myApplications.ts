import { defineStore } from "pinia";
import type { ApplicationModel, SubmitApplicationForm, CreatedApplication, ApiError } from "~/types/api";

export const useMyApplicationsStore = defineStore("myApplications", {
  state: () => ({
    applications: [] as ApplicationModel[],
    total: 0,
    page: 1,
    loading: false,
    currentApplication: null as ApplicationModel | null,
    submitting: false,
    withdrawing: false,
    error: null as ApiError | null,
  }),

  actions: {
    async fetchMyApplications(page: number = 1) {
      this.loading = true;
      this.error = null;

      const api = useApi();
      const { data, error } = await api.listMyApplications(page);

      if (error) {
        this.error = error;
      } else if (data) {
        this.applications = data.items;
        this.total = data.total;
        this.page = data.page;
      }

      this.loading = false;
    },

    async fetchMyApplication(applicationId: string) {
      this.loading = true;
      this.error = null;

      const api = useApi();
      const { data, error } = await api.readMyApplication(applicationId);

      if (error) {
        this.error = error;
      } else {
        this.currentApplication = data;
      }

      this.loading = false;
    },

    async submit(competitionId: string, form: SubmitApplicationForm): Promise<{ success: boolean; data: CreatedApplication | null }> {
      this.submitting = true;
      this.error = null;

      const api = useApi();
      const { data, error } = await api.submitApplication(competitionId, form);

      this.submitting = false;

      if (error) {
        this.error = error;
        return { success: false, data: null };
      }

      return { success: true, data };
    },

    async withdraw(applicationId: string): Promise<boolean> {
      this.withdrawing = true;
      this.error = null;

      const api = useApi();
      const { error } = await api.withdrawApplication(applicationId);

      this.withdrawing = false;

      if (error) {
        this.error = error;
        return false;
      }

      this.applications = this.applications.filter((a) => a.id !== applicationId);
      if (this.currentApplication?.id === applicationId) {
        this.currentApplication = null;
      }

      return true;
    },

    clearError() {
      this.error = null;
    },
  },
});
