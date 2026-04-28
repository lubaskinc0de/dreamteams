<script setup lang="ts">
import type { CompetitionTag, ExploreCompetitionsFilters, ExploreSortBy, ExploreCompetitionModel } from "~/types/api";
import { useExploreCompetitions } from "~/composables/useExploreCompetitions";
import { useInfiniteScroll } from "@vueuse/core";

const { t } = useI18n();
const { getErrorMessage } = useErrorHandler();
const userStore = useUserStore();

// Organizers can't apply — hide Register CTA on cards for them.
const canRegister = computed(() => !userStore.isOrganizer);

const {
  competitions,
  total,
  loading,
  error,
  hasMore,
  loadMore,
  reset,
  applyFilters,
} = useExploreCompetitions();

// Local filter state
const search = ref("");
const sortBy = ref<ExploreSortBy>("most_popular");
const minTeamSize = ref<number | null>(null);
const maxTeamSize = ref<number | null>(null);
const autoAccept = ref(false);
const selectedTagIds = ref<string[]>([]);
const availableTags = ref<CompetitionTag[]>([]);
const selectedTagCache = ref<CompetitionTag[]>([]);
const tagSearch = ref("");
const tagsLoading = ref(false);

const sortOptions = computed(() => [
  { value: "most_popular", label: t("explore.sort.mostPopular") },
  { value: "newest", label: t("explore.sort.newest") },
]);

const buildFilters = (): ExploreCompetitionsFilters => ({
  sort_by: sortBy.value,
  search: search.value.trim() || undefined,
  min_team_size: minTeamSize.value ?? undefined,
  max_team_size: maxTeamSize.value ?? undefined,
  auto_accept: autoAccept.value ? true : undefined,
  tag_ids: selectedTagIds.value.length > 0 ? selectedTagIds.value : undefined,
});

const commitFilters = () => applyFilters(buildFilters());

let searchTimer: ReturnType<typeof setTimeout> | null = null;
watch(search, () => {
  if (searchTimer) clearTimeout(searchTimer);
  searchTimer = setTimeout(commitFilters, 300);
});

watch([sortBy, minTeamSize, maxTeamSize, autoAccept, selectedTagIds], commitFilters, { deep: true });

const fetchTags = async () => {
  tagsLoading.value = true;
  const api = useApi();
  const { data } = await api.listTags({
    page: 1,
    search: tagSearch.value.trim() || undefined,
  });
  if (data) {
    availableTags.value = data.items;
  }
  tagsLoading.value = false;
};

let tagSearchTimer: ReturnType<typeof setTimeout> | null = null;
watch(tagSearch, () => {
  if (tagSearchTimer) clearTimeout(tagSearchTimer);
  tagSearchTimer = setTimeout(fetchTags, 250);
});

const tagOptions = computed(() => {
  const byId = new Map<string, CompetitionTag>();
  for (const tag of selectedTagCache.value) byId.set(tag.id, tag);
  for (const tag of availableTags.value) byId.set(tag.id, tag);
  return [...byId.values()].sort((a, b) => a.value.localeCompare(b.value));
});

watch(selectedTagIds, (ids) => {
  const known = tagOptions.value.filter((tag) => ids.includes(tag.id));
  const byId = new Map(selectedTagCache.value.map((tag) => [tag.id, tag]));
  for (const tag of known) {
    byId.set(tag.id, tag);
  }
  selectedTagCache.value = [...byId.values()].filter((tag) => ids.includes(tag.id));
});

onMounted(() => {
  reset();
  fetchTags();
  useInfiniteScroll(
    window,
    () => loadMore(),
    {
      distance: 400,
      canLoadMore: () => hasMore.value && !loading.value,
    },
  );
});

// Card click and Register CTA both navigate to the standalone submission page,
// which shows full details and (for participants) the apply form.
const goToCompetition = (competition: ExploreCompetitionModel) => {
  return navigateTo(`/competitions/submit/${competition.id}`);
};

useHead({ title: t("explore.title") });

const activeFilterCount = computed(() => {
  let n = 0;
  if (search.value.trim().length > 0) n += 1;
  if (minTeamSize.value !== null) n += 1;
  if (maxTeamSize.value !== null) n += 1;
  if (autoAccept.value) n += 1;
  if (selectedTagIds.value.length > 0) n += 1;
  if (sortBy.value !== "most_popular") n += 1;
  return n;
});

onBeforeUnmount(() => {
  if (tagSearchTimer) clearTimeout(tagSearchTimer);
});
</script>

<template>
  <UPage>
    <UPageBody>
      <UContainer class="!max-w-7xl py-6">
        <h1 class="text-2xl font-bold text-gray-900 dark:text-white mb-6">
          {{ t("explore.title") }}
        </h1>

        <!-- Filters -->
        <UCollapsible class="mb-6 group">
          <UButton
            type="button"
            variant="soft"
            color="neutral"
            size="md"
            leading-icon="i-heroicons-adjustments-horizontal"
            trailing-icon="i-heroicons-chevron-down"
            class="w-full justify-between"
            :ui="{ trailingIcon: 'transition-transform duration-200 group-data-[state=open]:rotate-180' }"
          >
            <span class="flex items-center gap-2">
              {{ t('explore.filters.title') }}
              <UBadge v-if="activeFilterCount > 0" variant="solid" color="primary" size="xs" :label="String(activeFilterCount)" />
            </span>
          </UButton>
          <template #content>
            <UCard class="mt-2">
              <div class="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-4">
                <UFormField :label="t('explore.filters.search')">
                  <UInput v-model="search" icon="i-heroicons-magnifying-glass" :placeholder="t('explore.filters.searchPlaceholder')" class="w-full" />
                </UFormField>

                <UFormField :label="t('explore.filters.sort')">
                  <URadioGroup v-model="sortBy" :items="sortOptions" />
                </UFormField>

                <UFormField :label="t('explore.filters.autoAccept')">
                  <UCheckbox
                    v-model="autoAccept"
                    :label="t('explore.filters.autoAcceptYes')"
                  />
                </UFormField>

                <UFormField :label="t('explore.filters.teamSize')">
                  <div class="flex gap-2">
                    <UInput
                      :model-value="minTeamSize ?? ''"
                      @update:model-value="(v) => minTeamSize = v === '' ? null : Number(v)"
                      type="number"
                      :min="1"
                      :placeholder="t('explore.filters.teamSizeMin')"
                    />
                    <UInput
                      :model-value="maxTeamSize ?? ''"
                      @update:model-value="(v) => maxTeamSize = v === '' ? null : Number(v)"
                      type="number"
                      :min="1"
                      :placeholder="t('explore.filters.teamSizeMax')"
                    />
                  </div>
                </UFormField>

                <UFormField :label="t('explore.filters.tags')" class="sm:col-span-2 lg:col-span-2">
                  <USelectMenu
                    v-model="selectedTagIds"
                    v-model:search-term="tagSearch"
                    :items="tagOptions"
                    value-key="id"
                    label-key="value"
                    multiple
                    clear
                    :placeholder="t('explore.filters.tagsPlaceholder')"
                    :search-input="{ placeholder: t('explore.filters.tagsPlaceholder') }"
                    class="w-full"
                  />
                </UFormField>
              </div>
            </UCard>
          </template>
        </UCollapsible>

        <!-- Results -->
        <section>
          <div class="flex items-center justify-between mb-4">
            <span class="text-sm text-gray-500">
              {{ t("explore.resultsCount", { count: total }) }}
            </span>
          </div>

          <div v-if="error" class="text-center py-16">
            <UIcon name="i-heroicons-exclamation-triangle" class="size-12 text-red-400 mb-4" />
            <p class="text-red-600 dark:text-red-400 text-lg mb-4">
              {{ getErrorMessage(error) }}
            </p>
            <UButton variant="soft" icon="i-heroicons-arrow-path" :label="t('common.retry')" @click="reset" />
          </div>

          <div v-else-if="loading && competitions.length === 0" class="grid grid-cols-1 md:grid-cols-2 xl:grid-cols-3 gap-6">
            <USkeleton v-for="i in 6" :key="i" class="h-64 w-full rounded-xl" />
          </div>

          <UAlert
            v-else-if="!loading && competitions.length === 0"
            color="info"
            variant="soft"
            :title="t('explore.empty')"
            :description="t('explore.emptyDescription')"
            icon="i-heroicons-inbox"
          />

          <div v-else class="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-5 sm:gap-6">
            <CompetitionPreviewCard
              v-for="c in competitions"
              :key="c.id"
              :competition="c"
              :can-register="canRegister"
              @register="() => goToCompetition(c)"
              @click="() => goToCompetition(c)"
            />
          </div>

          <div v-if="loading && competitions.length > 0" class="flex justify-center py-6">
            <UProgress indeterminate size="xs" class="w-48" />
          </div>
        </section>
      </UContainer>
    </UPageBody>
  </UPage>
</template>
