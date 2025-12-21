import { defineStore } from "pinia";
import type { OrganizerForm, CreatedOrganizer, ApiError } from "~/types/api";
import { UI_TEXT } from "~/constants/ui-text";

export const useOrganizerStore = defineStore("organizer", {
  state: () => ({
    registrationSuccess: false,
    createdOrganizer: null as CreatedOrganizer | null,
    loading: false,
    error: null as ApiError | null,
  }),

  actions: {
    async registerOrganizer(form: OrganizerForm) {
      this.loading = true;
      this.error = null;
      this.registrationSuccess = false;

      const api = useApi();
      const { data, error } = await api.registerOrganizer(form);

      if (error) {
        this.error = error;
      } else {
        this.createdOrganizer = data;
        this.registrationSuccess = true;

        // Show success toast notification
        const toast = useToast();
        toast.add({
          title: UI_TEXT.toast.registrationSuccess.title,
          description: UI_TEXT.toast.registrationSuccess.description,
          icon: "i-heroicons-check-circle",
          color: "success",
          duration: 5000,
        });

        // Update user profile after successful registration
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
