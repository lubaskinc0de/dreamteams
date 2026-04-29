import { defineStore } from "pinia";
import type { ApplicationModel, ApiError, ApplicationStatus, SortOrder } from "~/types/api";
import { useNotificationsStore } from "~/stores/notifications";

export const useCompetitionApplicationsStore = defineStore("competitionApplications", {
  state: () => ({
    applications: [] as ApplicationModel[],
    total: 0,
    page: 1,
    loading: false,
    currentApplication: null as ApplicationModel | null,
    acting: false,
    error: null as ApiError | null,
    sortOrder: "desc" as SortOrder,
    statusFilter: null as ApplicationStatus | null,
    exporting: false,
    exportErrorMessage: null as string | null,
  }),

  actions: {
    getExportErrorMessage(error: ApiError | null): string {
      const { $i18n } = useNuxtApp();
      if (!error) {
        return $i18n.t("apiErrors.UNKNOWN_ERROR");
      }

      const key = `apiErrors.${error.code}`;
      const translated = $i18n.t(key);
      return translated !== key ? translated : (error.message || $i18n.t("apiErrors.UNKNOWN_ERROR"));
    },

    async fetchApplications(competitionId: string, page: number = 1) {
      this.loading = true;
      this.error = null;

      const api = useApi();
      const { data, error } = await api.listApplicationsByCompetition(
        competitionId,
        page,
        this.sortOrder,
        this.statusFilter ?? undefined,
      );

      if (error) {
        this.error = error;
      } else if (data) {
        this.applications = data.items;
        this.total = data.total;
        this.page = data.page;
      }

      this.loading = false;
    },

    async setStatusFilter(competitionId: string, status: ApplicationStatus | null) {
      this.statusFilter = status;
      this.page = 1;
      await this.fetchApplications(competitionId, 1);
    },

    async toggleSortOrder(competitionId: string) {
      this.sortOrder = this.sortOrder === "desc" ? "asc" : "desc";
      this.page = 1;
      await this.fetchApplications(competitionId, 1);
    },

    async fetchApplication(applicationId: string) {
      this.loading = true;
      this.error = null;

      const api = useApi();
      const { data, error } = await api.readApplication(applicationId);

      if (error) {
        this.error = error;
      } else {
        this.currentApplication = data;
      }

      this.loading = false;
    },

    async accept(applicationId: string): Promise<boolean> {
      this.acting = true;
      this.error = null;

      const api = useApi();
      const { error } = await api.acceptApplication(applicationId);

      this.acting = false;

      if (error) {
        this.error = error;
        return false;
      }

      if (this.currentApplication?.id === applicationId) {
        this.currentApplication = { ...this.currentApplication, status: "accepted" };
      }

      const item = this.applications.find((a) => a.id === applicationId);
      if (item) {
        item.status = "accepted";
      }

      return true;
    },

    async reject(applicationId: string): Promise<boolean> {
      this.acting = true;
      this.error = null;

      const api = useApi();
      const { error } = await api.rejectApplication(applicationId);

      this.acting = false;

      if (error) {
        this.error = error;
        return false;
      }

      if (this.currentApplication?.id === applicationId) {
        this.currentApplication = { ...this.currentApplication, status: "rejected" };
      }

      const item = this.applications.find((a) => a.id === applicationId);
      if (item) {
        item.status = "rejected";
      }

      return true;
    },

    clearError() {
      this.error = null;
    },

    async exportApplications(competitionId: string): Promise<boolean> {
      const { $i18n } = useNuxtApp();
      const notifications = useNotificationsStore();
      const api = useApi();

      this.exporting = true;
      this.exportErrorMessage = null;

      const { data: createdJob, error } = await api.createExportJob({
        competition_id: competitionId,
        application_status: this.statusFilter,
      });

      if (error || !createdJob) {
        this.exporting = false;
        this.exportErrorMessage = this.getExportErrorMessage(error);
        return false;
      }

      const pollDelayMs = 1500;

      while (true) {
        await new Promise((resolve) => setTimeout(resolve, pollDelayMs));

        const { data: job, error: pollError } = await api.readExportJob(createdJob.job_id);

        if (pollError || !job) {
          this.exporting = false;
          this.exportErrorMessage = this.getExportErrorMessage(pollError);
          return false;
        }

        if (job.status_kind === "pending") {
          continue;
        }

        this.exporting = false;

        if (job.status_kind === "failed") {
          this.exportErrorMessage = job.status_reason ?? $i18n.t("apiErrors.UNKNOWN_ERROR");
          notifications.add({
            title: $i18n.t("applications.export.failedTitle"),
            description: this.exportErrorMessage,
            icon: "i-heroicons-exclamation-circle",
            color: "error",
          });
          return false;
        }

        if (job.file_url) {
          window.open(job.file_url, "_blank", "noopener,noreferrer");
        }

        notifications.add({
          title: $i18n.t("applications.export.successTitle"),
          description: $i18n.t("applications.export.successDescription"),
          icon: "i-heroicons-arrow-down-tray",
          color: "success",
        });
        return true;
      }
    },
  },
});
