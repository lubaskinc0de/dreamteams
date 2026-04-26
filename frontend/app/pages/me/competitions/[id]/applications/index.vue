<script setup lang="ts">
import { useCompetitionApplicationsStore } from '~/stores/competitionApplications';
import type { ApplicationStatus } from '~/types/api';

const { t } = useI18n();
const route = useRoute();
const router = useRouter();
const store = useCompetitionApplicationsStore();
const { navigateBack } = useBackNavigation('/me/competitions/applications');

const competitionId = computed(() => route.params.id as string);

useSeoMeta({ title: t('applications.title') });

onMounted(async () => {
  await store.fetchApplications(competitionId.value);
});

const statusColor = (status: string) => {
  if (status === 'accepted') return 'success';
  if (status === 'rejected') return 'error';
  return 'warning';
};

const goToApplication = (applicationId: string) => {
  router.push(`/me/competitions/${competitionId.value}/applications/${applicationId}`);
};

const statusTabs = computed(() => [
  { value: 'all', label: t('applications.filter.all') },
  { value: 'pending', label: t('applications.filter.pending') },
  { value: 'accepted', label: t('applications.filter.accepted') },
  { value: 'rejected', label: t('applications.filter.rejected') },
]);

const activeTab = computed({
  get: () => store.statusFilter ?? 'all',
  set: (val: string) => {
    const next = val === 'all' ? null : (val as ApplicationStatus);
    store.setStatusFilter(competitionId.value, next);
  },
});

const exportLabel = computed(() => {
  if (store.exporting) {
    return t('applications.export.exporting');
  }

  if (store.statusFilter === null) {
    return t('applications.export.buttonAll');
  }

  return t('applications.export.button');
});

const exportHint = computed(() => (
  store.statusFilter === null
    ? t('applications.export.allHint')
    : t(`applications.export.hint.${store.statusFilter}`)
));
</script>

<template>
  <UPage>
    <UPageBody>
      <UContainer class="!max-w-5xl">
        <!-- Header -->
        <div class="flex items-center gap-4 mb-6">
          <UButton
            icon="i-heroicons-arrow-left"
            color="neutral"
            variant="ghost"
            @click="navigateBack()"
          />
          <h1 class="text-2xl font-bold text-gray-900 dark:text-white">
            {{ t('applications.title') }}
          </h1>
          <UBadge v-if="!store.loading" variant="soft" :label="String(store.total)" />
        </div>

        <!-- Filters + Sort -->
        <div class="flex flex-col sm:flex-row sm:items-center sm:justify-between gap-3 mb-4">
          <UTabs v-model="activeTab" :items="statusTabs" size="sm" variant="pill" />
          <div class="flex flex-col items-stretch sm:items-end gap-2">
            <div class="flex flex-wrap justify-end gap-2">
              <UButton
                icon="i-heroicons-arrow-down-tray"
                variant="soft"
                color="primary"
                size="sm"
                :loading="store.exporting"
                :disabled="store.exporting"
                :label="exportLabel"
                @click="store.exportApplications(competitionId)"
              />
              <UButton
                :icon="store.sortOrder === 'desc' ? 'i-heroicons-bars-arrow-down' : 'i-heroicons-bars-arrow-up'"
                variant="soft"
                color="neutral"
                size="sm"
                :label="store.sortOrder === 'desc' ? t('applications.sort.newest') : t('applications.sort.oldest')"
                @click="store.toggleSortOrder(competitionId)"
              />
            </div>
            <p class="text-xs text-gray-500 dark:text-gray-400">
              {{ exportHint }}
            </p>
          </div>
        </div>

        <UAlert
          v-if="store.exportErrorMessage"
          color="error"
          variant="soft"
          :title="t('applications.export.failedTitle')"
          :description="store.exportErrorMessage"
          icon="i-heroicons-exclamation-circle"
          class="mb-4"
        />

        <!-- Error -->
        <UAlert
          v-if="store.error && !store.loading"
          color="error"
          variant="soft"
          :title="t('apiErrors.' + store.error.code)"
          icon="i-heroicons-exclamation-circle"
          class="mb-4"
        />

        <!-- Loading -->
        <div v-if="store.loading" class="space-y-3">
          <USkeleton v-for="i in 5" :key="i" class="h-20 w-full rounded-lg" />
        </div>

        <!-- Empty -->
        <UAlert
          v-else-if="store.applications.length === 0 && !store.error"
          color="info"
          variant="soft"
          :title="t('applications.empty')"
          :description="t('applications.emptyDescription')"
          icon="i-heroicons-inbox"
        />

        <!-- List -->
        <div v-else class="space-y-3">
          <UCard
            v-for="app in store.applications"
            :key="app.id"
            class="cursor-pointer hover:shadow-md transition-shadow"
            @click="goToApplication(app.id)"
          >
            <div class="flex items-center justify-between gap-4">
              <div class="flex-1 min-w-0 space-y-2">
                <p class="text-lg font-semibold text-gray-900 dark:text-white truncate">
                  {{ app.participant.full_name }}
                </p>
                <div class="flex flex-wrap gap-1.5">
                  <UBadge
                    v-for="domain in app.domains"
                    :key="domain"
                    size="sm"
                    variant="soft"
                    :label="domain"
                  />
                </div>
                <p class="text-sm text-gray-500 dark:text-gray-400">
                  {{ t('applications.submittedAt') }}: {{ new Date(app.created_at).toLocaleDateString() }}
                </p>
              </div>
              <UBadge
                :color="statusColor(app.status)"
                variant="subtle"
                size="md"
                :label="t('applications.status.' + app.status)"
              />
            </div>
          </UCard>
        </div>

        <!-- Pagination -->
        <div v-if="store.total > 10" class="mt-6 flex justify-center">
          <UPagination
            :total="store.total"
            :page="store.page"
            :items-per-page="10"
            @update:page="(p) => store.fetchApplications(competitionId, p)"
          />
        </div>
      </UContainer>
    </UPageBody>
  </UPage>
</template>
