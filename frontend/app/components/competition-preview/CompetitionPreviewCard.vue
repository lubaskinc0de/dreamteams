<script setup lang="ts">
import type { PreviewCompetitionModel } from "~/types/api";

interface Props {
  competition: PreviewCompetitionModel;
}

const props = defineProps<Props>();

const emit = defineEmits<{
  register: [id: string];
  click: [competition: PreviewCompetitionModel];
}>();

const { t } = useI18n();
const {
  formatDateRange,
  formatParticipants,
  formatTeamSize,
  getFormatLabel,
} = useCompetitionFormatters();

const handleRegister = (event: MouseEvent) => {
  event.stopPropagation(); // Prevent card click when clicking register button
  emit("register", props.competition.id);
};

const handleCardClick = () => {
  emit("click", props.competition);
};
</script>

<template>
  <article
    class="group relative rounded-2xl bg-white dark:bg-gray-900 border border-gray-200 dark:border-gray-800 p-7 sm:p-8 hover:border-primary-400/50 dark:hover:border-primary-500/50 hover:shadow-xl hover:shadow-primary-500/10 transition-all duration-300 cursor-pointer"
    @click="handleCardClick"
  >
    <!-- Title -->
    <h3
      class="text-2xl font-bold text-gray-900 dark:text-white leading-snug mb-3 line-clamp-2 group-hover:text-primary-600 dark:group-hover:text-primary-400 transition-colors duration-200"
    >
      {{ competition.title }}
    </h3>

    <!-- Description -->
    <p class="text-base text-gray-600 dark:text-gray-400 line-clamp-4 mb-5 leading-relaxed">
      {{ competition.description }}
    </p>

    <!-- Domains -->
    <div class="mb-5">
      <CompetitionDomainBadges :domains="competition.domains" size="sm" />
    </div>

    <!-- Meta -->
    <div class="space-y-2.5 pt-5 border-t border-gray-100 dark:border-gray-800">
      <UiInfoRow
        icon="i-heroicons-calendar"
        :value="formatDateRange(competition.schedule.registration_start, competition.schedule.registration_end)"
        size="sm"
      />
      <div class="flex flex-wrap gap-x-5 gap-y-2">
        <UiInfoRow
          icon="i-heroicons-users"
          :value="`${formatParticipants(competition.members_count, competition.participant_limits.max)} ${t('competitionsPreview.card.participantsSuffix')}`"
          size="sm"
        />
        <UiInfoRow
          v-if="competition.team_size"
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

      <!-- Organizer -->
      <div class="flex items-center gap-2.5 min-w-0 pt-1">
        <UAvatar
          :src="competition.organizer.avatar_url || '/no-photo.png'"
          :alt="competition.organizer.name"
          size="xs"
        />
        <span class="text-sm text-gray-500 dark:text-gray-400 truncate">
          {{ competition.organizer.name }}
        </span>
      </div>
    </div>

    <!-- CTA -->
    <UButton
      :label="t('competitionsPreview.card.registerButton')"
      icon="i-heroicons-bolt"
      trailing
      block
      size="lg"
      variant="solid"
      color="primary"
      class="mt-6"
      @click="handleRegister"
    />
  </article>
</template>
