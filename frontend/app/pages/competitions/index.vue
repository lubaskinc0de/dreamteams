<script setup lang="ts">
import type { CompetitionModel, CompetitionSortBy, SortOrder } from '~/types/api';
import { useCompetitionStore } from '~/stores/competition';
import { useInfiniteScroll } from '@vueuse/core';

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

// Infinite scroll
const scrollArea = useTemplateRef('scrollArea');

onMounted(() => {
  useInfiniteScroll(scrollArea.value?.$el, () => {
    competitionStore.loadNextPage(isArchivedFilter.value);
  }, {
    distance: 200,
    canLoadMore: () => {
      return competitionStore.hasMorePages && !competitionStore.loading;
    }
  });
});

// Navigate to create page
const goToCreate = () => {
  router.push('/competitions/create');
};

// Format date
const formatDate = (dateString: string) => {
  return new Date(dateString).toLocaleDateString('ru-RU', {
    year: 'numeric',
    month: 'long',
    day: 'numeric',
  });
};

// Get domain label
const getDomainLabel = (domain: string) => {
  return t(`competition.form.domains.options.${domain}`);
};

// Get format label
const getFormatLabel = (format: string) => {
  return t(`competition.formats.${format}`);
};

// Get registration status
const getRegistrationStatus = (competition: CompetitionModel) => {
  const now = new Date();
  const regStart = new Date(competition.schedule.registration_start);
  const regEnd = new Date(competition.schedule.registration_end);

  if (now < regStart) {
    return { label: t('competitions.status.notOpen'), color: 'warning' as const };
  } else if (now >= regStart && now <= regEnd) {
    return { label: t('competitions.status.open'), color: 'success' as const };
  } else {
    return { label: t('competitions.status.closed'), color: 'info' as const };
  }
};

// Format team size display
const formatTeamSize = (teamSize: { min: number; max: number }) => {
  if (teamSize.min === 1 && teamSize.max === 1) {
    return t('competitions.card.noTeams');
  }
  return `${teamSize.min}—${teamSize.max}`;
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
        <div class="mb-8">
          <h1 class="text-3xl font-bold text-gray-900 dark:text-white mb-2">
            {{ t('competitions.title') }}
          </h1>
          <p class="text-gray-600 dark:text-gray-400">
            {{ t('competitions.description') }}
          </p>
        </div>

        <!-- Search, Sort and Create Button -->
        <div class="mb-6 flex flex-col sm:flex-row gap-3">
          <UInput
            v-model="searchQuery"
            :placeholder="t('competitions.searchPlaceholder')"
            icon="i-heroicons-magnifying-glass"
            size="md"
            class="flex-1"
          />
          <div class="flex gap-2 flex-wrap sm:flex-nowrap">
            <UFieldGroup size="md" class="w-full sm:w-auto">
              <USelect
                v-model="sortBy"
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
                  @click="toggleSortOrder"
                  square
                />
              </UTooltip>
            </UFieldGroup>
            <UButton
              icon="i-heroicons-plus"
              size="md"
              color="primary"
              :label="t('competitions.createButton')"
              @click="goToCreate"
              class="w-full sm:w-auto"
            />
          </div>
        </div>

        <div class="flex gap-6">
          <!-- Filters Sidebar -->
          <aside class="w-64 shrink-0">
            <UCard>
              <template #header>
                <h3 class="font-semibold text-gray-900 dark:text-white">
                  {{ t('competitions.filters.title') }}
                </h3>
              </template>

              <URadioGroup
                v-model="filterStatus"
                :items="filterOptions"
                value-key="value"
              />
            </UCard>
          </aside>

          <!-- Competitions List -->
          <div class="flex-1 relative">
            <!-- Empty State -->
            <UCard v-if="!competitionStore.loading && filteredCompetitions.length === 0">
              <div class="text-center py-12">
                <UIcon
                  name="i-heroicons-trophy"
                  class="mx-auto h-12 w-12 text-gray-400 dark:text-gray-600 mb-4"
                />
                <h3
                  class="text-lg font-semibold text-gray-900 dark:text-white mb-2"
                >
                  {{ t('competitions.empty') }}
                </h3>
                <p class="text-gray-600 dark:text-gray-400 mb-6">
                  {{ t('competitions.emptyDescription') }}
                </p>
                <UButton
                  icon="i-heroicons-plus"
                  color="primary"
                  :label="t('competitions.createButton')"
                  @click="goToCreate"
                />
              </div>
            </UCard>

            <!-- Competitions Scroll Area -->
            <UScrollArea
              v-else
              ref="scrollArea"
              class="h-[calc(100vh-280px)]"
              :ui="{ viewport: 'gap-4 p-1' }"
            >
              <UCard
                v-for="competition in filteredCompetitions"
                :key="competition.id"
                class="hover:shadow-lg transition-shadow"
              >
                <div class="space-y-4">
                  <!-- Title, Status and Actions -->
                  <div class="flex items-start justify-between gap-4">
                    <h3
                      class="text-xl font-semibold text-gray-900 dark:text-white cursor-pointer flex-1"
                      @click="router.push(`/competitions/${competition.id}`)"
                    >
                      {{ competition.title }}
                    </h3>
                    <div class="flex items-center gap-2 shrink-0">
                      <UBadge
                        v-if="competition.is_archived"
                        color="warning"
                        variant="subtle"
                        :label="t('competitions.badge.archived')"
                      />
                      <UBadge
                        v-else
                        :color="getRegistrationStatus(competition).color"
                        variant="subtle"
                        :label="getRegistrationStatus(competition).label"
                      />
                      <UButton
                        icon="i-heroicons-trash"
                        color="error"
                        variant="ghost"
                        size="sm"
                        square
                        @click.stop="openDeleteModal(competition.id)"
                      />
                    </div>
                  </div>

                  <!-- Description -->
                  <p class="text-gray-600 dark:text-gray-400 line-clamp-2">
                    {{ competition.description }}
                  </p>

                  <!-- Domains -->
                  <div class="flex flex-wrap gap-2">
                    <UBadge
                      v-for="domain in competition.domains"
                      :key="domain"
                      variant="soft"
                      :label="getDomainLabel(domain)"
                    />
                  </div>

                  <!-- Meta Information -->
                  <div
                    class="flex flex-wrap gap-x-6 gap-y-2 text-sm text-gray-600 dark:text-gray-400"
                  >
                    <div class="flex items-center gap-2">
                      <UIcon name="i-heroicons-calendar" class="size-4" />
                      <span>
                        {{ t('competitions.card.registrationPeriod') }}:
                        {{ formatDate(competition.schedule.registration_start) }}
                        —
                        {{ formatDate(competition.schedule.registration_end) }}
                      </span>
                    </div>
                    <div class="flex items-center gap-2">
                      <UIcon name="i-heroicons-users" class="size-4" />
                      <span>
                        {{ t('competitions.card.participants') }}:
                        {{ competition.participant_limits.min }}—{{
                          competition.participant_limits.max
                        }}
                      </span>
                    </div>
                    <div class="flex items-center gap-2">
                      <UIcon name="i-heroicons-user-group" class="size-4" />
                      <span>
                        {{ competition.team_size.min === 1 && competition.team_size.max === 1 ? formatTeamSize(competition.team_size) : t('competitions.card.teamSize') + ': ' + formatTeamSize(competition.team_size) }}
                      </span>
                    </div>
                    <div class="flex items-center gap-2">
                      <UIcon name="i-heroicons-map-pin" class="size-4" />
                      <span>
                        {{ getFormatLabel(competition.venue.format) }}
                        <template v-if="competition.venue.location">
                          — {{ competition.venue.location }}
                        </template>
                      </span>
                    </div>
                  </div>
                </div>
              </UCard>
            </UScrollArea>

            <!-- Loading Indicator -->
            <UProgress
              v-if="competitionStore.loading"
              indeterminate
              size="xs"
              class="absolute top-0 inset-x-0 z-1"
              :ui="{ base: 'bg-default' }"
            />
          </div>
        </div>
      </div>
    </UPageBody>

    <!-- Delete Confirmation Modal -->
    <UModal
      v-model:open="isDeleteModalOpen"
      :title="t('competitions.delete.title')"
      :description="t('competitions.delete.description')"
      :ui="{ footer: 'justify-end' }"
    >
      <template #footer>
        <UButton
          color="neutral"
          variant="outline"
          :label="t('common.cancel')"
          @click="isDeleteModalOpen = false"
        />
        <UButton
          color="error"
          :label="t('competitions.delete.confirm')"
          @click="handleDelete"
        />
      </template>
    </UModal>
  </UPage>
</template>
