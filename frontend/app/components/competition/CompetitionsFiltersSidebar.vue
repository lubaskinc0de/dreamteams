<script setup lang="ts">
/**
 * Sidebar with filter controls for competitions
 */

interface Props {
  filterStatus: 'all' | 'active' | 'archived';
}

const props = defineProps<Props>();
const emit = defineEmits(['update:filterStatus']);

const { t } = useI18n();

// Filter options
const filterOptions = [
  { value: 'all', label: t('competitions.filters.all') },
  { value: 'active', label: t('competitions.filters.active') },
  { value: 'archived', label: t('competitions.filters.archived') },
];
</script>

<template>
  <aside class="hidden lg:block w-64 shrink-0">
    <UCard>
      <template #header>
        <h3 class="font-semibold text-gray-900 dark:text-white">
          {{ t('competitions.filters.title') }}
        </h3>
      </template>

      <URadioGroup
        :model-value="filterStatus"
        @update:model-value="emit('update:filterStatus', $event)"
        :items="filterOptions"
        value-key="value"
      />
    </UCard>
  </aside>
</template>
