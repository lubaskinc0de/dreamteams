<script setup lang="ts">
import type { CompetitionModel, CompetitionSortBy, SortOrder } from '~/types/api';
import { useCompetitionStore } from '~/stores/competition';

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

// Fetch competitions on mount
onMounted(() => {
  competitionStore.fetchCompetitions(1, sortBy.value, sortOrder.value, isArchivedFilter.value, true);
});

// Watch sort and filter changes and refetch
watch([sortBy, sortOrder, filterStatus], () => {
  competitionStore.fetchCompetitions(1, sortBy.value, sortOrder.value, isArchivedFilter.value, true);
});

// Filtered competitions based on search (status is filtered server-side)
const filteredCompetitions = computed(() => {
  let result = competitionStore.competitions;

  // Filter by search query
  if (searchQuery.value) {
    const query = searchQuery.value.toLowerCase();
    result = result.filter(
      (comp: CompetitionModel) =>
        comp.title.toLowerCase().includes(query) ||
        comp.description.toLowerCase().includes(query),
    );
  }

  return result;
});

// Load more handler for infinite scroll
const handleLoadMore = () => {
  competitionStore.loadNextPage(isArchivedFilter.value);
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
      <div class="max-w-7xl mx-auto">
        <!-- Header -->
        <CompetitionCompetitionsHeader />

        <!-- Search, Sort and Create Button -->
        <CompetitionCompetitionsToolbar
          v-model:search-query="searchQuery"
          v-model:sort-by="sortBy"
          :sort-order="sortOrder"
          @toggle-sort-order="toggleSortOrder"
          @create="goToCreate"
        />

        <div class="flex gap-6">
          <!-- Filters Sidebar -->
          <CompetitionCompetitionsFiltersSidebar
            v-model:filter-status="filterStatus"
          />

          <!-- Competitions List -->
          <CompetitionCompetitionsEmptyState
            v-if="!competitionStore.loading && filteredCompetitions.length === 0"
            @create="goToCreate"
          />

          <CompetitionCompetitionsList
            v-else
            :competitions="filteredCompetitions"
            :loading="competitionStore.loading"
            :has-more="competitionStore.hasMorePages"
            @click="router.push(`/competitions/${$event}`)"
            @delete="openDeleteModal"
            @load-more="handleLoadMore"
          />
        </div>
      </div>
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
