import { defineStore } from "pinia";
import type { ApiError, CompetitionTag, CompetitionTagForm } from "~/types/api";

export const useAdminTagsStore = defineStore("adminTags", {
  state: () => ({
    tags: [] as CompetitionTag[],
    total: 0,
    page: 1,
    search: "",
    loading: false,
    loadingMore: false,
    creating: false,
    deleting: false,
    error: null as ApiError | null,
  }),

  getters: {
    hasMore: (state) => state.tags.length < state.total,
  },

  actions: {
    async fetchTags(page: number = 1, append = false) {
      if (append) {
        this.loadingMore = true;
      } else {
        this.loading = true;
      }
      this.error = null;

      const api = useApi();
      const { data, error } = await api.listAdminTags({
        page,
        search: this.search.trim() || undefined,
      });

      if (error) {
        this.error = error;
      } else if (data) {
        this.tags = append ? [...this.tags, ...data.items] : data.items;
        this.total = data.total;
        this.page = data.page;
      }

      if (append) {
        this.loadingMore = false;
      } else {
        this.loading = false;
      }
    },

    async applyFilters() {
      this.page = 1;
      await this.fetchTags(1);
    },

    async loadNextPage() {
      if (!this.hasMore || this.loading || this.loadingMore) return;
      await this.fetchTags(this.page + 1, true);
    },

    async createTag(form: CompetitionTagForm) {
      this.creating = true;
      this.error = null;

      const api = useApi();
      const { error } = await api.createAdminTag(form);

      if (error) {
        this.error = error;
        this.creating = false;
        return false;
      }

      await this.fetchTags(1);
      this.creating = false;
      return true;
    },

    async deleteTag(tagId: string) {
      this.deleting = true;
      this.error = null;

      const api = useApi();
      const { error } = await api.deleteAdminTag(tagId);

      if (error) {
        this.error = error;
        this.deleting = false;
        return false;
      }

      this.tags = this.tags.filter((tag) => tag.id !== tagId);
      this.total = Math.max(0, this.total - 1);
      this.deleting = false;
      return true;
    },

    clearError() {
      this.error = null;
    },
  },
});
