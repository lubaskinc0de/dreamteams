import { defineStore } from "pinia";
import type { ProfileModel, ApiError } from "~/types/api";

export const useUserStore = defineStore("user", {
  state: () => ({
    profile: null as ProfileModel | null,
    loading: false,
    error: null as ApiError | null,
  }),

  getters: {
    isOrganizer: (state) => state.profile?.organizer !== null,
    organizer: (state) => state.profile?.organizer,
  },

  actions: {
    async fetchProfile() {
      this.loading = true;
      this.error = null;

      const api = useApi();
      const { data, error } = await api.getUserProfile();

      if (error) {
        this.error = error;
      } else {
        this.profile = data;
      }

      this.loading = false;
    },

    clearError() {
      this.error = null;
    },
  },
});
