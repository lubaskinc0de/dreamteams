<script setup lang="ts">
import type { CompetitionModel } from '~/types/api';

/**
 * Компонент для отображения полной информации о соревновании
 * Разбит на переиспользуемые секции
 */

interface Props {
  competition: CompetitionModel;
}

defineProps<Props>();

const { t } = useI18n();
</script>

<template>
  <div class="space-y-6">
    <!-- Description -->
    <UCard>
      <template #header>
        <h2 class="text-xl font-semibold">{{ t('competition.detail.description') }}</h2>
      </template>
      <p class="text-gray-700 dark:text-gray-300 whitespace-pre-wrap">{{ competition.description }}</p>
    </UCard>

    <!-- Schedule Section -->
    <CompetitionSectionsScheduleSection :schedule="competition.schedule" />

    <!-- Details Grid -->
    <div class="grid grid-cols-1 md:grid-cols-2 gap-6">
      <!-- Participants Section -->
      <CompetitionSectionsParticipantDetailsSection
        :participant-limits="competition.participant_limits"
        :participant-type="competition.participant_type"
        :team-size="competition.team_size"
      />

      <!-- Venue Section -->
      <CompetitionSectionsVenueSection :venue="competition.venue" />
    </div>

    <!-- Milestones Section -->
    <CompetitionSectionsMilestonesSection :milestones="competition.milestones" />
  </div>
</template>
