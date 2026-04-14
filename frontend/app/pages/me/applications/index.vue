<script setup lang="ts">
import { useMyApplicationsStore } from '~/stores/myApplications';

const { t } = useI18n();
const router = useRouter();
const store = useMyApplicationsStore();

useSeoMeta({ title: t('myApplications.title') });

onMounted(async () => {
  await store.fetchMyApplications();
});

const statusColor = (status: string) => {
  if (status === 'accepted') return 'success';
  if (status === 'rejected') return 'error';
  return 'warning';
};
</script>

<template>
  <UPage>
    <UPageBody>
      <UContainer class="!max-w-5xl">
        <!-- Header -->
        <div class="flex items-center justify-between mb-6">
          <h1 class="text-2xl font-bold text-gray-900 dark:text-white">
            {{ t('myApplications.title') }}
          </h1>
          <UBadge v-if="!store.loading" variant="soft" :label="String(store.total)" />
        </div>

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
          :title="t('myApplications.empty')"
          :description="t('myApplications.emptyDescription')"
          icon="i-heroicons-inbox"
        />

        <!-- List -->
        <div v-else class="space-y-3">
          <UCard
            v-for="app in store.applications"
            :key="app.id"
            class="cursor-pointer hover:shadow-md transition-shadow"
            @click="router.push(`/me/applications/${app.id}`)"
          >
            <div class="flex items-center justify-between">
              <div class="flex-1 min-w-0">
                <div class="flex items-center gap-2 mb-1">
                  <span class="text-xs text-gray-400">
                    {{ t('myApplications.competition') }}: <span class="font-mono">{{ app.competition_id }}</span>
                  </span>
                </div>
                <div class="flex flex-wrap gap-1">
                  <UBadge
                    v-for="domain in app.domains"
                    :key="domain"
                    size="xs"
                    variant="soft"
                    :label="domain"
                  />
                </div>
                <p class="text-xs text-gray-400 mt-1">
                  {{ t('myApplications.submittedAt') }}: {{ new Date(app.created_at).toLocaleDateString() }}
                </p>
              </div>
              <UBadge
                :color="statusColor(app.status)"
                variant="subtle"
                :label="t('myApplications.status.' + app.status)"
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
            @update:page="(p) => store.fetchMyApplications(p)"
          />
        </div>
      </UContainer>
    </UPageBody>
  </UPage>
</template>
