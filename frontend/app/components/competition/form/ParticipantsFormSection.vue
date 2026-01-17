<script setup lang="ts">
/**
 * Секция формы с информацией об участниках
 */

interface Props {
  participantLimitsMin: number;
  participantLimitsMax: number;
  teamSizeMin: number;
  teamSizeMax: number;
  isTeamCompetition: boolean;
}

defineProps<Props>();
const emit = defineEmits(['update:participantLimitsMin', 'update:participantLimitsMax', 'update:teamSizeMin', 'update:teamSizeMax']);

const { t } = useI18n();
</script>

<template>
  <UCard>
    <template #header>
      <h2 class="text-xl font-semibold text-gray-900 dark:text-white">
        {{ t('competition.create.sections.participants') }}
      </h2>
    </template>

    <div class="space-y-6">
      <!-- Participant Limits -->
      <UFormField
        name="participant_limits"
        :label="t('competition.form.participantLimits.label')"
        required
        size="xl"
      >
        <div class="space-y-3">
          <div class="flex justify-between text-base font-medium text-gray-700 dark:text-gray-300">
            <span>{{ t('competition.form.participantLimits.min.label') }}: {{ participantLimitsMin }}</span>
            <span>{{ t('competition.form.participantLimits.max.label') }}: {{ participantLimitsMax }}</span>
          </div>
          <USlider
            :model-value="[participantLimitsMin, participantLimitsMax]"
            :min="1"
            :max="1000"
            :step="1"
            size="xl"
            @update:model-value="(val) => {
              if (val && val[0] !== undefined && val[1] !== undefined) {
                emit('update:participantLimitsMin', val[0]);
                emit('update:participantLimitsMax', val[1]);
              }
            }"
          />
        </div>
      </UFormField>

      <!-- Team Size (only for team competitions) -->
      <UFormField
        v-if="isTeamCompetition"
        name="team_size"
        :label="t('competition.form.teamSize.label')"
        :required="isTeamCompetition"
        size="xl"
      >
        <div class="space-y-3">
          <div class="flex justify-between text-base font-medium text-gray-700 dark:text-gray-300">
            <span>{{ t('competition.form.teamSize.min.label') }}: {{ teamSizeMin }}</span>
            <span>{{ t('competition.form.teamSize.max.label') }}: {{ teamSizeMax }}</span>
          </div>
          <USlider
            :model-value="[teamSizeMin, teamSizeMax]"
            :min="1"
            :max="20"
            :step="1"
            size="xl"
            @update:model-value="(val) => {
              if (val && val[0] !== undefined && val[1] !== undefined) {
                emit('update:teamSizeMin', val[0]);
                emit('update:teamSizeMax', val[1]);
              }
            }"
          />
        </div>
      </UFormField>
    </div>
  </UCard>
</template>
