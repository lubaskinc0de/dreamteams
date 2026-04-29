import { defineStore } from "pinia";
import type {
  OrganizerForm,
  UpdateOrganizerForm,
  CreatedOrganizer,
  ApiError,
} from "~/types/api";
import { useNotificationsStore } from "~/stores/notifications";

export const useOrganizerStore = defineStore("organizer", {
  state: () => ({
    registrationSuccess: false,
    updateSuccess: false,
    createdOrganizer: null as CreatedOrganizer | null,
    loading: false,
    error: null as ApiError | null,
  }),

  actions: {
    async registerOrganizer(form: OrganizerForm) {
      const { $i18n } = useNuxtApp();
      const notifications = useNotificationsStore();
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

        notifications.add({
          title: $i18n.t("toast.registrationSuccess.title"),
          description: $i18n.t("toast.registrationSuccess.description"),
          icon: "i-heroicons-check-circle",
          color: "success",
        });

        const userStore = useUserStore();
        await userStore.fetchProfile();
      }

      this.loading = false;
    },

    async updateOrganizer(form: UpdateOrganizerForm) {
      const { $i18n } = useNuxtApp();
      const notifications = useNotificationsStore();
      const api = useApi();

      this.loading = true;
      this.error = null;
      this.updateSuccess = false;

      const { error } = await api.updateOrganizer(form);

      if (error) {
        this.error = error;
      } else {
        this.updateSuccess = true;

        notifications.add({
          title: $i18n.t("toast.profileUpdated.title"),
          description: $i18n.t("toast.profileUpdated.description"),
          icon: "i-heroicons-check-circle",
          color: "success",
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
      this.updateSuccess = false;
      this.createdOrganizer = null;
      this.error = null;
    },
  },
});
