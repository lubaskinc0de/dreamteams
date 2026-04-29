<script setup lang="ts">
/**
 * Секция формы с информацией об участниках.
 * teamSize is null when the competition is individual (no team formation phase).
 */
import type { TeamSizeRange } from "~/types/api";

interface Props {
  participantLimitsMax: number;
  teamSize: TeamSizeRange | null;
  isTeamCompetition: boolean;
  showParticipantLimits?: boolean;
  showTeamSize?: boolean;
}

const props = withDefaults(defineProps<Props>(), {
  showParticipantLimits: true,
  showTeamSize: true,
});
const emit = defineEmits<{
  "update:participantLimitsMax": [value: number];
  "update:teamSize": [value: TeamSizeRange | null];
}>();

const { t } = useI18n();

const updateTeamSize = (patch: Partial<TeamSizeRange>) => {
  const current = props.teamSize ?? { min: 1, max: 5 };
  emit("update:teamSize", { ...current, ...patch });
};
</script>

<template>
  <UCard v-if="showParticipantLimits || (showTeamSize && isTeamCompetition && teamSize)">
    <template #header>
      <h2 class="text-xl font-semibold text-gray-900 dark:text-white">
        {{ t('competition.create.sections.participants') }}
      </h2>
    </template>

    <div class="space-y-6">
      <!-- Participant Limits -->
      <UFormField
        v-if="showParticipantLimits"
        name="participant_limits"
        required
        size="xl"
      >
        <template #label>
          {{ t('competition.form.participantLimits.label') }}
          <HelpTooltip :text="t('competition.form.participantLimits.tooltip')" />
        </template>
        <div class="space-y-3">
          <div class="text-base font-medium text-gray-700 dark:text-gray-300">
            <span>{{ t('competition.form.participantLimits.max.label') }}: {{ participantLimitsMax }}</span>
          </div>
          <USlider
            :model-value="participantLimitsMax"
            :min="1"
            :max="1000"
            :step="1"
            size="xl"
            @update:model-value="(val) => {
              if (typeof val === 'number') {
                emit('update:participantLimitsMax', val);
              }
            }"
          />
        </div>
      </UFormField>

      <!-- Team Size (only for team competitions) -->
      <UFormField
        v-if="showTeamSize && isTeamCompetition && teamSize"
        name="team_size"
        :required="isTeamCompetition"
        size="xl"
      >
        <template #label>
          {{ t('competition.form.teamSize.label') }}
          <HelpTooltip :text="t('competition.form.teamSize.tooltip')" />
        </template>
        <div class="space-y-3">
          <div class="flex justify-between text-base font-medium text-gray-700 dark:text-gray-300">
            <span>{{ t('competition.form.teamSize.min.label') }}: {{ teamSize.min }}</span>
            <span>{{ t('competition.form.teamSize.max.label') }}: {{ teamSize.max }}</span>
          </div>
          <USlider
            :model-value="[teamSize.min, teamSize.max]"
            :min="1"
            :max="20"
            :step="1"
            size="xl"
            @update:model-value="(val) => {
              if (val && val[0] !== undefined && val[1] !== undefined) {
                updateTeamSize({ min: val[0], max: val[1] });
              }
            }"
          />
        </div>
      </UFormField>
    </div>
  </UCard>
</template>
