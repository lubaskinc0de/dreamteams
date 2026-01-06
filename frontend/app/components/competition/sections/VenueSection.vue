<script setup lang="ts">
import type { CompetitionVenue } from '~/types/api';

/**
 * Секция с информацией о месте проведения соревнования
 */

interface Props {
  venue: CompetitionVenue;
}

defineProps<Props>();

const { t } = useI18n();
const { getFormatLabel } = useCompetitionFormatters();
</script>

<template>
  <UCard>
    <template #header>
      <h2 class="text-xl font-semibold">{{ t('competition.detail.venue') }}</h2>
    </template>
    <div class="space-y-3">
      <div>
        <h3 class="text-sm font-medium text-gray-500 dark:text-gray-400 mb-1">
          {{ t('competition.form.venue.format.label') }}
        </h3>
        <p class="text-gray-900 dark:text-white">
          {{ getFormatLabel(venue.format) }}
        </p>
      </div>

      <div v-if="venue.location">
        <h3 class="text-sm font-medium text-gray-500 dark:text-gray-400 mb-1">
          {{ t('competition.form.venue.location.label') }}
        </h3>
        <p class="text-gray-900 dark:text-white">
          {{ venue.location }}
        </p>
      </div>
    </div>
  </UCard>
</template>
