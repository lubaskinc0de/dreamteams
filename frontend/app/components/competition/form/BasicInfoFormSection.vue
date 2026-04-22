<script setup lang="ts">
import type { Domain, ParticipantType } from '~/types/api';

/**
 * Секция формы с базовой информацией о соревновании
 */

interface Props {
  title: string;
  description: string;
  domains: Domain[];
  participantType: ParticipantType;
  isTeamCompetition: boolean;
  autoAccept?: boolean;
  isArchived?: boolean;
  showArchiveField?: boolean;
}

withDefaults(defineProps<Props>(), {
  showArchiveField: false,
  autoAccept: false,
});
const emit = defineEmits(['update:title', 'update:description', 'update:domains', 'update:participantType', 'update:isTeamCompetition', 'update:autoAccept', 'update:isArchived']);

const { t } = useI18n();

// Domain options
const domainOptions = [
  { value: 'frontend' as Domain, label: t('competition.form.domains.options.frontend') },
  { value: 'mobile' as Domain, label: t('competition.form.domains.options.mobile') },
  { value: 'backend' as Domain, label: t('competition.form.domains.options.backend') },
  { value: 'ai' as Domain, label: t('competition.form.domains.options.ai') },
  { value: 'devops' as Domain, label: t('competition.form.domains.options.devops') },
];

// Participant type options
const participantTypeOptions = [
  { value: 'schoolchild' as ParticipantType, label: t('competition.form.participantType.options.schoolchild') },
  { value: 'student' as ParticipantType, label: t('competition.form.participantType.options.student') },
  { value: 'any' as ParticipantType, label: t('competition.form.participantType.options.any') },
];
</script>

<template>
  <UCard class="lg:col-span-2">
    <template #header>
      <h2 class="text-xl font-semibold text-gray-900 dark:text-white">
        {{ t('competition.create.sections.basic') }}
      </h2>
    </template>

    <div class="space-y-6">
      <!-- Title -->
      <UFormField name="title" required size="xl">
        <template #label>
          {{ t('competition.form.title.label') }}
          <HelpTooltip :text="t('competition.form.title.tooltip')" />
        </template>
        <UInput
          :model-value="title"
          @update:model-value="emit('update:title', $event)"
          :placeholder="t('competition.form.title.placeholder')"
          size="xl"
          class="w-full text-lg"
        />
      </UFormField>

      <!-- Description -->
      <UFormField name="description" required size="xl">
        <template #label>
          {{ t('competition.form.description.label') }}
          <HelpTooltip :text="t('competition.form.description.tooltip')" />
        </template>
        <UTextarea
          :model-value="description"
          @update:model-value="emit('update:description', $event)"
          :placeholder="t('competition.form.description.placeholder')"
          :rows="6"
          size="xl"
          class="w-full text-lg"
        />
      </UFormField>

      <!-- Domains -->
      <UFormField name="domains" required size="xl">
        <template #label>
          {{ t('competition.form.domains.label') }}
          <HelpTooltip :text="t('competition.form.domains.tooltip')" />
        </template>
        <UCheckboxGroup
          :model-value="domains"
          @update:model-value="emit('update:domains', $event)"
          :items="domainOptions"
          orientation="horizontal"
          size="xl"
        />
      </UFormField>

      <!-- Participant Type -->
      <UFormField name="participant_type" required size="xl">
        <template #label>
          {{ t('competition.form.participantType.label') }}
          <HelpTooltip :text="t('competition.form.participantType.tooltip')" />
        </template>
        <URadioGroup
          :model-value="participantType"
          @update:model-value="emit('update:participantType', $event)"
          :items="participantTypeOptions"
          size="xl"
        />
      </UFormField>

      <!-- Is Team Competition -->
      <UFormField size="xl">
        <template #label>
          {{ t('competition.form.isTeam.label') }}
          <HelpTooltip :text="t('competition.form.isTeam.tooltip')" />
        </template>
        <div class="flex items-center gap-3">
          <USwitch
            :model-value="isTeamCompetition"
            @update:model-value="emit('update:isTeamCompetition', $event)"
            size="xl"
          />
          <span class="text-gray-700 dark:text-gray-300">{{ t('competition.form.isTeam.checkboxLabel') }}</span>
        </div>
      </UFormField>

      <!-- Auto Accept -->
      <UFormField name="auto_accept" size="xl">
        <template #label>
          {{ t('competition.form.autoAccept.label') }}
          <HelpTooltip :text="t('competition.form.autoAccept.tooltip')" />
        </template>
        <div class="flex items-center gap-3">
          <USwitch
            :model-value="autoAccept"
            @update:model-value="emit('update:autoAccept', $event)"
            size="xl"
          />
          <span class="text-gray-700 dark:text-gray-300">{{ t('competition.form.autoAccept.checkboxLabel') }}</span>
        </div>
      </UFormField>

      <!-- Is Archived (only in edit mode) -->
      <UFormField
        v-if="showArchiveField"
        :label="t('competition.form.isArchived.label')"
        size="xl"
      >
        <div class="flex items-center gap-3">
          <USwitch
            :model-value="isArchived"
            @update:model-value="emit('update:isArchived', $event)"
            size="xl"
          />
          <span class="text-gray-700 dark:text-gray-300">{{ t('competition.form.isArchived.checkboxLabel') }}</span>
        </div>
      </UFormField>
    </div>
  </UCard>
</template>
