import { defineStore } from "pinia";
import type { ParticipantForm, CreatedParticipant, ApiError } from "~/types/api";
import { useNotificationsStore } from "~/stores/notifications";

export const useParticipantStore = defineStore("participant", {
  state: () => ({
    registrationSuccess: false,
    createdParticipant: null as CreatedParticipant | null,
    loading: false,
    error: null as ApiError | null,
  }),

  actions: {
    async registerParticipant(form: ParticipantForm) {
      const { $i18n } = useNuxtApp();
      const notifications = useNotificationsStore();
      const api = useApi();

      this.loading = true;
      this.error = null;
      this.registrationSuccess = false;

      const { data, error } = await api.registerParticipant(form);

      if (error) {
        this.error = error;
      } else {
        this.createdParticipant = data;
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

    clearError() {
      this.error = null;
    },

    reset() {
      this.registrationSuccess = false;
      this.createdParticipant = null;
      this.error = null;
    },
  },
});
