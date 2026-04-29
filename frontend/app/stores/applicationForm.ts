import { defineStore } from "pinia";
import type { ApplicationFormModel, ApplicationFormInput, CreatedApplicationForm, ApiError } from "~/types/api";

export const useApplicationFormStore = defineStore("applicationForm", {
  state: () => ({
    form: null as ApplicationFormModel | null,
    loading: false,
    saving: false,
    deleting: false,
    error: null as ApiError | null,
  }),

  actions: {
    async fetchForm(competitionId: string) {
      this.loading = true;
      this.error = null;

      const api = useApi();
      const { data, error } = await api.getApplicationForm(competitionId);

      if (error) {
        this.error = error;
      } else {
        this.form = data;
      }

      this.loading = false;
    },

    async createForm(competitionId: string, input: ApplicationFormInput): Promise<{ success: boolean; data: CreatedApplicationForm | null }> {
      this.saving = true;
      this.error = null;

      const api = useApi();
      const { data, error } = await api.createApplicationForm(competitionId, input);

      this.saving = false;

      if (error) {
        this.error = error;
        return { success: false, data: null };
      }

      await this.fetchForm(competitionId);
      return { success: true, data };
    },

    async deleteForm(competitionId: string): Promise<boolean> {
      this.deleting = true;
      this.error = null;

      const api = useApi();
      const { error } = await api.deleteApplicationForm(competitionId);

      this.deleting = false;

      if (error) {
        this.error = error;
        return false;
      }

      this.form = null;
      return true;
    },

    clearError() {
      this.error = null;
    },
  },
});
