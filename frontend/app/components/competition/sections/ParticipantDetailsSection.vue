<script setup lang="ts">
import type { ParticipantLimits, ParticipantType, TeamSizeRange } from '~/types/api';

/**
 * Секция с информацией об участниках соревнования
 */

interface Props {
  participantLimits: ParticipantLimits;
  participantType: ParticipantType;
  teamSize: TeamSizeRange | null;
  membersCount: number;
}

defineProps<Props>();

const { t } = useI18n();
const { formatParticipants, formatTeamSize, getParticipantTypeLabel } = useCompetitionFormatters();
</script>

<template>
  <UCard>
    <template #header>
      <h2 class="text-xl font-semibold">{{ t('competition.detail.participants') }}</h2>
    </template>
    <div class="space-y-3">
      <div>
        <h3 class="text-sm font-medium text-gray-500 dark:text-gray-400 mb-1">
          {{ t('competition.detail.participantCount') }}
        </h3>
        <p class="text-gray-900 dark:text-white">
          {{ formatParticipants(membersCount, participantLimits.max) }}
        </p>
      </div>

      <div>
        <h3 class="text-sm font-medium text-gray-500 dark:text-gray-400 mb-1">
          {{ t('competition.form.participantType.label') }}
        </h3>
        <p class="text-gray-900 dark:text-white">
          {{ getParticipantTypeLabel(participantType) }}
        </p>
      </div>

      <div>
        <h3 class="text-sm font-medium text-gray-500 dark:text-gray-400 mb-1">
          {{ t('competition.detail.teamSize') }}
        </h3>
        <p class="text-gray-900 dark:text-white">
          {{ teamSize ? formatTeamSize(teamSize) : t('competition.individual') }}
        </p>
      </div>
    </div>
  </UCard>
</template>
