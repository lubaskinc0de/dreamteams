import { defineStore } from "pinia";
import type { InviteModel, InviteForm, CreatedInvite, ApiError } from "~/types/api";

export const useInvitesStore = defineStore("invites", {
  state: () => ({
    invites: [] as InviteModel[],
    total: 0,
    page: 1,
    loading: false,
    issuing: false,
    error: null as ApiError | null,
    issuedInvite: null as CreatedInvite | null,
  }),

  actions: {
    async fetchInvites(page: number = 1) {
      this.loading = true;
      this.error = null;

      const api = useApi();
      const { data, error } = await api.listInvites(page);

      if (error) {
        this.error = error;
      } else if (data) {
        this.invites = data.items;
        this.total = data.total;
        this.page = data.page;
      }

      this.loading = false;
    },

    async issueInvite(form: InviteForm) {
      this.issuing = true;
      this.error = null;
      this.issuedInvite = null;

      const api = useApi();
      const { data, error } = await api.issueInvite(form);

      if (error) {
        this.error = error;
      } else if (data) {
        this.issuedInvite = data;
        await this.fetchInvites(this.page);
      }

      this.issuing = false;
    },

    async revokeInvite(inviteId: string) {
      this.error = null;

      const api = useApi();
      const { error } = await api.revokeInvite(inviteId);

      if (error) {
        this.error = error;
        return false;
      }

      const invite = this.invites.find((i) => i.id === inviteId);
      if (invite) {
        invite.is_revoked = true;
      }

      return true;
    },

    clearError() {
      this.error = null;
    },

    clearIssuedInvite() {
      this.issuedInvite = null;
    },
  },
});
