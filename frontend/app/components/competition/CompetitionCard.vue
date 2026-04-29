<script setup lang="ts">
import type { CompetitionModel } from '~/types/api';

/**
 * Карточка соревнования для отображения в списке
 * Использует переиспользуемые composables и компоненты
 */

interface Props {
  competition: CompetitionModel;
  showDelete?: boolean;
}

const props = withDefaults(defineProps<Props>(), { showDelete: true });

// Emits
const emit = defineEmits<{
  click: [id: string];
  delete: [id: string];
}>();

const { t } = useI18n();
const { formatDateRange, formatParticipants, formatTeamSize, getFormatLabel } = useCompetitionFormatters();

// Handle card click
const handleClick = () => {
  emit('click', props.competition.id);
};

// Handle delete click
const handleDelete = () => {
  emit('delete', props.competition.id);
};
</script>

<template>
  <UCard class="w-full hover:shadow-lg transition-shadow overflow-hidden">
    <div class="space-y-4">
      <!-- Title, Status and Actions -->
      <div class="flex items-start justify-between gap-4">
        <h3
          class="text-xl font-semibold text-gray-900 dark:text-white cursor-pointer flex-1 min-w-0 truncate"
          @click="handleClick"
        >
          {{ competition.title }}
        </h3>
        <div class="flex items-center gap-2 shrink-0">
          <CompetitionStatusBadge :competition="competition" />
          <UButton
            v-if="props.showDelete"
            icon="i-heroicons-trash"
            color="error"
            variant="ghost"
            size="sm"
            square
            :title="t('common.delete')"
            @click.stop="handleDelete"
          />
        </div>
      </div>

      <!-- Description -->
      <p class="text-gray-600 dark:text-gray-400 line-clamp-2">
        {{ competition.description }}
      </p>

      <!-- Tags -->
      <CompetitionTagBadges :tags="competition.tags" />

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
          :value="formatParticipants(competition.members_count, competition.participant_limits.max)"
          size="sm"
        />
        <UiInfoRow
          v-if="competition.team_size"
          icon="i-heroicons-user-group"
          :label="t('competitions.card.teamSize')"
          :value="formatTeamSize(competition.team_size)"
          size="sm"
        />
        <UiInfoRow
          v-else
          icon="i-heroicons-user"
          :value="t('competition.individual')"
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
