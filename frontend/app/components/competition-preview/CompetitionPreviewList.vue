<script setup lang="ts">
/**
 * Competition preview list with:
 * - Desktop (lg+): 3 cards per row, paginated with arrow buttons
 * - Tablet (sm-lg): 2 cards per row, paginated with arrow buttons
 * - Mobile: vertical list with infinite scroll
 */
import type { PreviewCompetitionModel } from "~/types/api";
import { useInfiniteScroll, useWindowSize } from "@vueuse/core";

interface Props {
  competitions: PreviewCompetitionModel[];
  loading: boolean;
  hasMore: boolean;
}

const props = defineProps<Props>();
const emit = defineEmits(["register", "load-more", "view-details"]);

const { width } = useWindowSize();

// Breakpoint-based page size: 3 for lg+, 2 for sm+, 0 for mobile (infinite scroll)
const pageSize = computed(() => {
  if (width.value >= 1024) return 3;
  if (width.value >= 640) return 2;
  return 0; // mobile — infinite scroll, show all
});

const isMobile = computed(() => pageSize.value === 0);

// View pagination (separate from API pagination)
const viewPage = ref(0);

// Reset view page when switching between mobile/desktop
watch(isMobile, () => {
  viewPage.value = 0;
});

// Total view pages based on loaded competitions
const totalViewPages = computed(() => {
  if (isMobile.value) return 1;
  return Math.ceil(props.competitions.length / pageSize.value);
});

// Cards visible on current view page
const visibleCompetitions = computed(() => {
  if (isMobile.value) return props.competitions;
  const start = viewPage.value * pageSize.value;
  return props.competitions.slice(start, start + pageSize.value);
});

const canGoBack = computed(() => viewPage.value > 0);
const canGoForward = computed(() => {
  if (isMobile.value) return false;
  const nextStart = (viewPage.value + 1) * pageSize.value;
  // Can go forward if there are more loaded items OR more to load from API
  return nextStart < props.competitions.length || props.hasMore;
});

const goBack = () => {
  if (canGoBack.value) viewPage.value--;
};

const goForward = () => {
  if (!canGoForward.value) return;

  const nextStart = (viewPage.value + 1) * pageSize.value;

  // If we need more data from the API, load it
  if (nextStart >= props.competitions.length && props.hasMore) {
    emit("load-more");
    // Watch for new data to arrive, then advance
    const stop = watch(
      () => props.competitions.length,
      (newLen) => {
        if (newLen > nextStart - pageSize.value) {
          viewPage.value++;
          stop();
        }
      },
    );
  } else {
    viewPage.value++;
  }
};

// Page indicator text
const pageIndicator = computed(() => {
  if (isMobile.value) return "";
  const current = viewPage.value + 1;
  return `${current} / ${Math.max(totalViewPages.value, current)}`;
});

// Mobile infinite scroll
const listEl = useTemplateRef("listEl");

onMounted(() => {
  if (listEl.value) {
    useInfiniteScroll(
      window,
      () => {
        if (isMobile.value) {
          emit("load-more");
        }
      },
      {
        distance: 400,
        canLoadMore: () => {
          return isMobile.value && props.hasMore && !props.loading;
        },
      },
    );
  }
});
</script>

<template>
  <div ref="listEl">
    <!-- Desktop/Tablet: paginated grid with arrows -->
    <div v-if="!isMobile" class="relative">
      <!-- Navigation arrows + page indicator -->
      <div class="flex items-center justify-center mb-6">
        <div class="flex items-center gap-2">
          <UButton
            icon="i-heroicons-chevron-left"
            variant="ghost"
            color="neutral"
            size="md"
            square
            :disabled="!canGoBack"
            @click="goBack"
          />
          <span class="text-sm text-gray-500 dark:text-gray-400 tabular-nums min-w-[4ch] text-center">
            {{ pageIndicator }}
          </span>
          <UButton
            icon="i-heroicons-chevron-right"
            variant="ghost"
            color="neutral"
            size="md"
            square
            :disabled="!canGoForward"
            @click="goForward"
          />
        </div>
      </div>

      <!-- Cards grid -->
      <div
        class="grid gap-5 sm:gap-6"
        :class="{
          'grid-cols-3': pageSize === 3 && visibleCompetitions.length > 1,
          'grid-cols-2': pageSize === 2 && visibleCompetitions.length > 1,
          'max-w-lg mx-auto': visibleCompetitions.length === 1,
        }"
      >
        <CompetitionPreviewCard
          v-for="competition in visibleCompetitions"
          :key="competition.id"
          :competition="competition"
          @register="emit('register', $event)"
          @click="emit('view-details', $event)"
        />
      </div>

      <!-- Loading for next page fetch -->
      <div v-if="loading" class="flex justify-center py-6">
        <UProgress indeterminate size="xs" class="w-48" />
      </div>
    </div>

    <!-- Mobile: infinite scroll list -->
    <div v-else>
      <div class="flex flex-col gap-5">
        <CompetitionPreviewCard
          v-for="competition in competitions"
          :key="competition.id"
          :competition="competition"
          @register="emit('register', $event)"
          @click="emit('view-details', $event)"
        />
      </div>

      <!-- Loading Indicator -->
      <div v-if="loading" class="flex justify-center py-8">
        <UProgress indeterminate size="xs" class="w-48" />
      </div>
    </div>
  </div>
</template>
