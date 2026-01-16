<script setup lang="ts">
import type { CompetitionSortBy, SortOrder } from '~/types/api';
import { useCompetitionStore } from '~/stores/competition';
import { useDebounceFn } from '@vueuse/core';

const { t } = useI18n();
const competitionStore = useCompetitionStore();
const router = useRouter();

// SEO Meta tags
useSeoMeta({
  title: t('seo.competitions.title'),
  description: t('seo.competitions.description'),
});

// Search and filter state
const searchQuery = ref('');
const filterStatus = ref<'all' | 'active' | 'archived'>('all');

// Delete modal state
const isDeleteModalOpen = ref(false);
const competitionToDelete = ref<string | null>(null);

// Sort state
const sortBy = ref<CompetitionSortBy>('created_at');
const sortOrder = ref<SortOrder>('desc');

// Toggle sort order
const toggleSortOrder = () => {
  sortOrder.value = sortOrder.value === 'asc' ? 'desc' : 'asc';
};

// Computed filter value for API
const isArchivedFilter = computed(() => {
  if (filterStatus.value === 'active') return false;
  if (filterStatus.value === 'archived') return true;
  return undefined;
});

// Computed search value for API (empty string becomes undefined)
const searchFilter = computed(() => searchQuery.value.trim() || undefined);

// Fetch competitions function
const fetchCompetitions = () => {
  competitionStore.fetchCompetitions(1, sortBy.value, sortOrder.value, isArchivedFilter.value, true, searchFilter.value);
};

// Debounced search handler
const debouncedSearch = useDebounceFn(() => {
  fetchCompetitions();
}, 300);

// Fetch competitions on mount
onMounted(() => {
  fetchCompetitions();
});

// Watch sort and filter changes and refetch immediately
watch([sortBy, sortOrder, filterStatus], () => {
  fetchCompetitions();
});

// Watch search changes with debounce
watch(searchQuery, () => {
  debouncedSearch();
});

// Load more handler for infinite scroll
const handleLoadMore = () => {
  competitionStore.loadNextPage(isArchivedFilter.value, searchFilter.value);
};

// Navigate to create page
const goToCreate = () => {
  router.push('/competitions/create');
};


// Delete competition handlers
const toast = useToast();

const openDeleteModal = (competitionId: string) => {
  competitionToDelete.value = competitionId;
  isDeleteModalOpen.value = true;
};

const handleDelete = async () => {
  if (!competitionToDelete.value) return;

  const result = await competitionStore.deleteCompetition(competitionToDelete.value);

  if (result.success) {
    toast.add({
      title: t('toast.competitionDeleted.title'),
      description: t('toast.competitionDeleted.description'),
      icon: 'i-heroicons-check-circle',
      color: 'success',
    });
  } else {
    toast.add({
      title: t('toast.competitionDeleteError.title'),
      description: t('toast.competitionDeleteError.description'),
      icon: 'i-heroicons-exclamation-circle',
      color: 'error',
    });
  }

  isDeleteModalOpen.value = false;
  competitionToDelete.value = null;
};
</script>

<template>
  <UPage>
    <UPageBody>
      <UContainer class="!max-w-7xl">
        <!-- Header -->
        <CompetitionCompetitionsHeader />

        <!-- Search, Sort and Create Button -->
        <CompetitionCompetitionsToolbar
          v-model:search-query="searchQuery"
          v-model:sort-by="sortBy"
          v-model:filter-status="filterStatus"
          :sort-order="sortOrder"
          @toggle-sort-order="toggleSortOrder"
          @create="goToCreate"
        />

        <div class="flex gap-4 md:gap-6 min-h-[calc(100vh-280px)]">
          <!-- Filters Sidebar -->
          <CompetitionCompetitionsFiltersSidebar
            v-model:filter-status="filterStatus"
          />

          <!-- Competitions List -->
          <CompetitionCompetitionsEmptyState
            v-if="!competitionStore.loading && competitionStore.competitions.length === 0"
            @create="goToCreate"
          />

          <CompetitionCompetitionsList
            v-else
            :competitions="competitionStore.competitions"
            :loading="competitionStore.loading"
            :has-more="competitionStore.hasMorePages"
            @click="router.push(`/competitions/${$event}`)"
            @delete="openDeleteModal"
            @load-more="handleLoadMore"
          />
        </div>
      </UContainer>
    </UPageBody>

    <!-- Delete Confirmation Modal -->
    <UiConfirmDeleteModal
      v-model:open="isDeleteModalOpen"
      :title="t('competitions.delete.title')"
      :description="t('competitions.delete.description')"
      :confirm-label="t('competitions.delete.confirm')"
      :cancel-label="t('common.cancel')"
      :is-deleting="competitionStore.loading"
      @confirm="handleDelete"
    />
  </UPage>
</template>
