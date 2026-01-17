<script setup lang="ts">
import type { Milestone } from '~/types/api';

/**
 * Секция с вехами соревнования
 */

interface Props {
  milestones: Milestone[];
}

defineProps<Props>();

const { t } = useI18n();
const { formatDate, formatTime } = useCompetitionFormatters();
</script>

<template>
  <UCard v-if="milestones.length > 0">
    <template #header>
      <h2 class="text-xl font-semibold">{{ t('competition.detail.milestones') }}</h2>
    </template>
    <div class="space-y-3">
      <div
        v-for="(milestone, index) in milestones"
        :key="index"
        class="flex items-center gap-4 p-3 rounded-lg bg-gray-50 dark:bg-gray-800"
      >
        <UIcon name="i-heroicons-flag" class="size-5 text-primary-500" />
        <div class="flex-1">
          <p class="font-medium text-gray-900 dark:text-white">{{ milestone.title }}</p>
          <p class="text-sm text-gray-500 dark:text-gray-400">
            {{ formatDate(milestone.timestamp) }} {{ formatTime(milestone.timestamp) }}
          </p>
        </div>
      </div>
    </div>
  </UCard>
</template>
