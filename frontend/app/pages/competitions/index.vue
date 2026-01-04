<script setup lang="ts">
import type { CompetitionModel } from '~/types/api';
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
const filterStatus = ref('all');

// Fetch competitions on mount
onMounted(() => {
  competitionStore.fetchCompetitions();
});

// Filtered competitions based on search and filters
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

  // Filter by status
  if (filterStatus.value === 'active') {
    result = result.filter((comp: CompetitionModel) => !comp.is_archived);
  } else if (filterStatus.value === 'archived') {
    result = result.filter((comp: CompetitionModel) => comp.is_archived);
  }

  return result;
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

        <!-- Search and Create Button -->
        <div class="mb-6 flex gap-3 items-center">
          <UInput
            v-model="searchQuery"
            :placeholder="t('competitions.searchPlaceholder')"
            icon="i-heroicons-magnifying-glass"
            size="lg"
            class="flex-1"
          />
          <UButton
            icon="i-heroicons-plus"
            size="lg"
            color="primary"
            :label="t('competitions.createButton')"
            @click="goToCreate"
          />
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

              <div class="space-y-2">
                <URadio
                  v-model="filterStatus"
                  value="all"
                  :label="t('competitions.filters.all')"
                />
                <URadio
                  v-model="filterStatus"
                  value="active"
                  :label="t('competitions.filters.active')"
                />
                <URadio
                  v-model="filterStatus"
                  value="archived"
                  :label="t('competitions.filters.archived')"
                />
              </div>
            </UCard>
          </aside>

          <!-- Competitions List -->
          <div class="flex-1">
            <!-- Loading State -->
            <div v-if="competitionStore.loading" class="space-y-4">
              <UCard v-for="i in 3" :key="i">
                <div class="space-y-3">
                  <USkeleton class="h-6 w-3/4" />
                  <USkeleton class="h-4 w-full" />
                  <USkeleton class="h-4 w-5/6" />
                  <div class="flex gap-2">
                    <USkeleton class="h-6 w-20" />
                    <USkeleton class="h-6 w-20" />
                  </div>
                </div>
              </UCard>
            </div>

            <!-- Empty State -->
            <UCard v-else-if="filteredCompetitions.length === 0">
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

            <!-- Competitions Grid -->
            <div v-else class="grid gap-4">
              <UCard
                v-for="competition in filteredCompetitions"
                :key="competition.id"
                class="hover:shadow-lg transition-shadow cursor-pointer"
                @click="router.push(`/competitions/${competition.id}`)"
              >
                <div class="space-y-4">
                  <!-- Title and Status -->
                  <div class="flex items-start justify-between gap-4">
                    <h3
                      class="text-xl font-semibold text-gray-900 dark:text-white"
                    >
                      {{ competition.title }}
                    </h3>
                    <UBadge
                      v-if="competition.is_archived"
                      color="neutral"
                      variant="subtle"
                      label="Архив"
                    />
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
                        {{ t('competitions.card.teamSize') }}:
                        {{ competition.team_size.min }}—{{
                          competition.team_size.max
                        }}
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
            </div>
          </div>
        </div>
      </div>
    </UPageBody>
  </UPage>
</template>
