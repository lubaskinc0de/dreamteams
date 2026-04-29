import { defineStore } from "pinia";
import type {
  AdminBlockUserInput,
  AdminUserDetails,
  AdminUserListItem,
  AdminUserRole,
  ApiError,
} from "~/types/api";

export const useAdminUsersStore = defineStore("adminUsers", {
  state: () => ({
    users: [] as AdminUserListItem[],
    total: 0,
    page: 1,
    search: "",
    isAdminFilter: null as boolean | null,
    isBlockedFilter: null as boolean | null,
    roleFilter: null as AdminUserRole | null,
    loading: false,
    detailLoading: false,
    actionLoading: false,
    error: null as ApiError | null,
    currentUser: null as AdminUserDetails | null,
  }),

  actions: {
    async fetchUsers(page: number = 1) {
      this.loading = true;
      this.error = null;

      const api = useApi();
      const { data, error } = await api.listAdminUsers({
        page,
        search: this.search.trim() || undefined,
        is_admin: this.isAdminFilter ?? undefined,
        is_blocked: this.isBlockedFilter ?? undefined,
        role: this.roleFilter ?? undefined,
      });

      if (error) {
        this.error = error;
      } else if (data) {
        this.users = data.items;
        this.total = data.total;
        this.page = data.page;
      }

      this.loading = false;
    },

    async fetchUser(userId: string) {
      this.detailLoading = true;
      this.error = null;

      const api = useApi();
      const { data, error } = await api.readAdminUser(userId);

      if (error) {
        this.error = error;
        this.currentUser = null;
      } else {
        this.currentUser = data;
      }

      this.detailLoading = false;
    },

    async applyFilters() {
      this.page = 1;
      await this.fetchUsers(1);
    },

    async blockUser(userId: string, input: AdminBlockUserInput) {
      this.actionLoading = true;
      this.error = null;

      const api = useApi();
      const { error } = await api.blockAdminUser(userId, input);

      if (error) {
        this.error = error;
        this.actionLoading = false;
        return false;
      }

      await this.refreshAfterAction(userId);
      this.actionLoading = false;
      return true;
    },

    async unblockUser(userId: string) {
      this.actionLoading = true;
      this.error = null;

      const api = useApi();
      const { error } = await api.unblockAdminUser(userId);

      if (error) {
        this.error = error;
        this.actionLoading = false;
        return false;
      }

      await this.refreshAfterAction(userId);
      this.actionLoading = false;
      return true;
    },

    async refreshAfterAction(userId: string) {
      await this.fetchUsers(this.page);
      if (this.currentUser?.user.id === userId) {
        await this.fetchUser(userId);
      }
    },

    clearError() {
      this.error = null;
    },
  },
});
