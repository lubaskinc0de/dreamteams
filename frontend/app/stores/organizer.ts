import { defineStore } from "pinia";
import type { OrganizerForm, CreatedOrganizer, ApiError } from "~/types/api";

export const useOrganizerStore = defineStore("organizer", {
  state: () => ({
    registrationSuccess: false,
    createdOrganizer: null as CreatedOrganizer | null,
    loading: false,
    error: null as ApiError | null,
  }),

  actions: {
    async registerOrganizer(form: OrganizerForm) {
      const { $i18n } = useNuxtApp();
      const toast = useToast();
      const api = useApi();

      this.loading = true;
      this.error = null;
      this.registrationSuccess = false;

      const { data, error } = await api.registerOrganizer(form);

      if (error) {
        this.error = error;
      } else {
        this.createdOrganizer = data;
        this.registrationSuccess = true;

        toast.add({
          title: $i18n.t("toast.registrationSuccess.title"),
          description: $i18n.t("toast.registrationSuccess.description"),
          icon: "i-heroicons-check-circle",
          color: "success",
          duration: 5000,
        });

        const userStore = useUserStore();
        await userStore.fetchProfile();
      }

      this.loading = false;
    },

    clearError() {
      this.error = null;
    },

    reset() {
      this.registrationSuccess = false;
      this.createdOrganizer = null;
      this.error = null;
    },
  },
});
