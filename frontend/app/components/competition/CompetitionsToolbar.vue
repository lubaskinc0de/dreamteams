<script setup lang="ts">
/**
 * Toolbar with search, sort controls, and create button
 */
import type { CompetitionSortBy, SortOrder } from '~/types/api';

interface Props {
  searchQuery: string;
  sortBy: CompetitionSortBy;
  sortOrder: SortOrder;
  filterStatus: 'all' | 'active' | 'archived';
}

const props = defineProps<Props>();
const emit = defineEmits(['update:searchQuery', 'update:sortBy', 'update:filterStatus', 'toggleSortOrder', 'create']);

const { t } = useI18n();

// Mobile filters drawer
const isFiltersOpen = ref(false);

// Sort options
const sortByOptions = [
  { value: 'created_at', label: t('competitions.sort.createdAt') },
  { value: 'title', label: t('competitions.sort.title') },
  { value: 'registration_start', label: t('competitions.sort.registrationStart') },
  { value: 'team_formation_start', label: t('competitions.sort.teamFormationStart') },
];

// Filter options
const filterOptions = [
  { value: 'all', label: t('competitions.filters.all') },
  { value: 'active', label: t('competitions.filters.active') },
  { value: 'archived', label: t('competitions.filters.archived') },
];
</script>

<template>
  <div class="mb-6 flex flex-col sm:flex-row gap-3">
    <div class="flex gap-2 flex-1">
      <UButton
        icon="i-heroicons-funnel"
        size="md"
        color="neutral"
        variant="subtle"
        @click="isFiltersOpen = true"
        class="md:hidden shrink-0"
        square
      />
      <UInput
        :model-value="searchQuery"
        @update:model-value="emit('update:searchQuery', $event)"
        :placeholder="t('competitions.searchPlaceholder')"
        icon="i-heroicons-magnifying-glass"
        size="md"
        class="flex-1"
      />
    </div>
    <div class="flex gap-2 flex-wrap sm:flex-nowrap">
      <UFieldGroup size="md" class="w-full sm:w-auto">
        <USelect
          :model-value="sortBy"
          @update:model-value="emit('update:sortBy', $event)"
          :items="sortByOptions"
          value-key="value"
          size="md"
          icon="i-heroicons-arrows-up-down"
          class="w-full sm:w-auto"
        />
        <UTooltip :text="sortOrder === 'asc' ? t('competitions.sort.asc') : t('competitions.sort.desc')">
          <UButton
            :icon="sortOrder === 'asc' ? 'i-heroicons-arrow-up' : 'i-heroicons-arrow-down'"
            size="md"
            color="neutral"
            variant="subtle"
            @click="emit('toggleSortOrder')"
            square
          />
        </UTooltip>
      </UFieldGroup>
      <UButton
        icon="i-heroicons-plus"
        size="md"
        color="primary"
        :label="t('competitions.createButton')"
        @click="emit('create')"
        class="w-full sm:w-auto"
      />
    </div>
  </div>

  <!-- Mobile Filters Drawer -->
  <UDrawer v-model:open="isFiltersOpen" side="left">
    <template #content>
      <div class="p-6">
        <h3 class="font-semibold text-gray-900 dark:text-white mb-4">
          {{ t('competitions.filters.title') }}
        </h3>
        <URadioGroup
          :model-value="filterStatus"
          @update:model-value="emit('update:filterStatus', $event)"
          :items="filterOptions"
          value-key="value"
        />
      </div>
    </template>
  </UDrawer>
</template>
