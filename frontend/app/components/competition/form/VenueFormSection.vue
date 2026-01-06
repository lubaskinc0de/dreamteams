<script setup lang="ts">
import type { CompetitionFormat } from '~/types/api';

/**
 * Секция формы с информацией о месте проведения
 */

interface Props {
  format: CompetitionFormat;
  location: string | null;
}

defineProps<Props>();
const emit = defineEmits(['update:format', 'update:location']);

const { t } = useI18n();

// Venue format options
const venueFormatOptions = [
  { value: 'online' as CompetitionFormat, label: t('competition.form.venue.format.options.online') },
  { value: 'offline' as CompetitionFormat, label: t('competition.form.venue.format.options.offline') },
  { value: 'hybrid' as CompetitionFormat, label: t('competition.form.venue.format.options.hybrid') },
];
</script>

<template>
  <UCard>
    <template #header>
      <h2 class="text-xl font-semibold text-gray-900 dark:text-white">
        {{ t('competition.create.sections.venue') }}
      </h2>
    </template>

    <div class="space-y-6">
      <!-- Format -->
      <UFormField
        name="venue.format"
        :label="t('competition.form.venue.format.label')"
        required
        size="xl"
      >
        <URadioGroup
          :model-value="format"
          @update:model-value="emit('update:format', $event)"
          :items="venueFormatOptions"
          size="xl"
        />
      </UFormField>

      <!-- Location -->
      <UFormField
        v-if="format !== 'online'"
        name="venue.location"
        :label="t('competition.form.venue.location.label')"
        size="xl"
      >
        <UInput
          :model-value="location || ''"
          @update:model-value="emit('update:location', $event || null)"
          :placeholder="t('competition.form.venue.location.placeholder')"
          size="xl"
          class="w-full text-lg"
        />
      </UFormField>
    </div>
  </UCard>
</template>
