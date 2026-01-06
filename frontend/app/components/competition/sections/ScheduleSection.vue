<script setup lang="ts">
import type { CompetitionSchedule } from '~/types/api';

/**
 * Секция с информацией о расписании соревнования
 */

interface Props {
  schedule: CompetitionSchedule;
}

defineProps<Props>();

const { t } = useI18n();
const { formatDateRange } = useCompetitionFormatters();
</script>

<template>
  <UCard>
    <template #header>
      <h2 class="text-xl font-semibold">{{ t('competition.detail.schedule') }}</h2>
    </template>
    <div class="space-y-4">
      <div>
        <h3 class="font-medium mb-2">{{ t('competition.detail.registration') }}</h3>
        <p class="text-gray-700 dark:text-gray-300">
          {{ formatDateRange(schedule.registration_start, schedule.registration_end) }}
        </p>
      </div>

      <div v-if="schedule.team_formation_start && schedule.team_formation_end">
        <h3 class="font-medium mb-2">{{ t('competition.detail.teamFormation') }}</h3>
        <p class="text-gray-700 dark:text-gray-300">
          {{ formatDateRange(schedule.team_formation_start, schedule.team_formation_end) }}
        </p>
      </div>
    </div>
  </UCard>
</template>
