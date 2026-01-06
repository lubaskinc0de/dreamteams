<script setup lang="ts">
import type { CompetitionModel } from '~/types/api';

/**
 * Карточка соревнования для отображения в списке
 * Использует переиспользуемые composables и компоненты
 */

interface Props {
  competition: CompetitionModel;
}

const props = defineProps<Props>();

// Emits
const emit = defineEmits<{
  click: [id: string];
  delete: [id: string];
}>();

const { t } = useI18n();
const { formatDateRange, formatNumericRange, formatTeamSize, getFormatLabel } = useCompetitionFormatters();

// Handle card click
const handleClick = () => {
  emit('click', props.competition.id);
};

// Handle delete click
const handleDelete = (event: Event) => {
  event.stopPropagation();
  emit('delete', props.competition.id);
};
</script>

<template>
  <UCard class="hover:shadow-lg transition-shadow">
    <div class="space-y-4">
      <!-- Title, Status and Actions -->
      <div class="flex items-start justify-between gap-4">
        <h3
          class="text-xl font-semibold text-gray-900 dark:text-white cursor-pointer flex-1"
          @click="handleClick"
        >
          {{ competition.title }}
        </h3>
        <div class="flex items-center gap-2 shrink-0">
          <CompetitionStatusBadge :competition="competition" />
          <UButton
            icon="i-heroicons-trash"
            color="error"
            variant="ghost"
            size="sm"
            square
            @click="handleDelete"
          />
        </div>
      </div>

      <!-- Description -->
      <p class="text-gray-600 dark:text-gray-400 line-clamp-2">
        {{ competition.description }}
      </p>

      <!-- Domains -->
      <CompetitionDomainBadges :domains="competition.domains" />

      <!-- Meta Information -->
      <div class="flex flex-wrap gap-x-6 gap-y-2 text-sm text-gray-600 dark:text-gray-400">
        <UiInfoRow
          icon="i-heroicons-calendar"
          :label="t('competitions.card.registrationPeriod')"
          :value="formatDateRange(competition.schedule.registration_start, competition.schedule.registration_end)"
          size="sm"
        />
        <UiInfoRow
          icon="i-heroicons-users"
          :label="t('competitions.card.participants')"
          :value="formatNumericRange(competition.participant_limits.min, competition.participant_limits.max)"
          size="sm"
        />
        <UiInfoRow
          v-if="!(competition.team_size.min === 1 && competition.team_size.max === 1)"
          icon="i-heroicons-user-group"
          :label="t('competitions.card.teamSize')"
          :value="formatTeamSize(competition.team_size)"
          size="sm"
        />
        <UiInfoRow
          v-else
          icon="i-heroicons-user-group"
          :value="formatTeamSize(competition.team_size)"
          size="sm"
        />
        <UiInfoRow
          icon="i-heroicons-map-pin"
          :value="competition.venue.location ? `${getFormatLabel(competition.venue.format)} — ${competition.venue.location}` : getFormatLabel(competition.venue.format)"
          size="sm"
        />
      </div>
    </div>
  </UCard>
</template>
