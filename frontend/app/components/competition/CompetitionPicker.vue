<script setup lang="ts">
import { useCompetitionStore } from '~/stores/competition';
import { useInfiniteScroll } from '@vueuse/core';

const props = defineProps<{
  title: string;
  description: string;
}>();

const emit = defineEmits<{
  select: [id: string];
}>();

const competitionStore = useCompetitionStore();
const { t } = useI18n();

onMounted(() => {
  competitionStore.fetchCompetitions(1);
});

useInfiniteScroll(
  () => (import.meta.client ? window : null),
  () => { competitionStore.loadNextPage(); },
  {
    distance: 200,
    canLoadMore: () => competitionStore.hasMorePages && !competitionStore.loading,
  },
);
</script>

<template>
  <UPage>
    <UPageBody>
      <UContainer class="!max-w-7xl">
        <div class="mb-6">
          <h1 class="text-2xl font-bold text-gray-900 dark:text-white">{{ props.title }}</h1>
          <p class="text-sm text-gray-500 dark:text-gray-400 mt-1">{{ props.description }}</p>
        </div>

        <UAlert
          v-if="competitionStore.error && !competitionStore.loading"
          color="error"
          variant="soft"
          :title="t('apiErrors.' + competitionStore.error.code)"
          icon="i-heroicons-exclamation-circle"
          class="mb-4"
        />

        <!-- Loading skeletons -->
        <div v-if="competitionStore.loading && competitionStore.competitions.length === 0" class="grid grid-cols-2 md:grid-cols-3 lg:grid-cols-4 gap-3">
          <USkeleton v-for="i in 8" :key="i" class="h-10 w-full rounded-lg" />
        </div>

        <!-- Empty state -->
        <div
          v-else-if="!competitionStore.loading && competitionStore.competitions.length === 0 && !competitionStore.error"
          class="text-center py-16"
        >
          <UIcon name="i-heroicons-trophy" class="mx-auto h-12 w-12 text-gray-400 dark:text-gray-600 mb-4" />
          <h3 class="text-lg font-semibold text-gray-900 dark:text-white mb-2">{{ t('competitions.empty') }}</h3>
          <p class="text-gray-600 dark:text-gray-400">{{ t('competitions.emptyDescription') }}</p>
        </div>

        <!-- Competition buttons -->
        <template v-else>
          <div class="grid grid-cols-2 md:grid-cols-3 lg:grid-cols-4 gap-3">
            <button
              v-for="competition in competitionStore.competitions"
              :key="competition.id"
              class="text-left px-4 py-3 rounded-lg border border-gray-200 dark:border-gray-700 bg-white dark:bg-gray-800 hover:border-primary-400 dark:hover:border-primary-500 hover:shadow-sm transition-all truncate text-sm font-medium text-gray-900 dark:text-white"
              @click="emit('select', competition.id)"
            >
              {{ competition.title }}
            </button>
          </div>
          <UProgress
            v-if="competitionStore.loading"
            indeterminate
            size="xs"
            class="mt-2"
          />
        </template>
      </UContainer>
    </UPageBody>
  </UPage>
</template>
