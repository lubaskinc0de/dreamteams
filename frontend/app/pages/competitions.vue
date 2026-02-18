<script setup lang="ts">
import type { PreviewCompetitionModel } from "~/types/api";

/**
 * Public competitions browsing page
 * Shows all available competitions with infinite scroll
 * Works for both authenticated and unauthenticated users
 */

const { t } = useI18n();

// Initialize competitions preview state
const {
  competitions,
  total,
  loading,
  error,
  hasMore,
  loadMore,
  reset,
} = useCompetitionsPreview();

// Load initial data
onMounted(() => {
  reset();
});

const { login } = useAuth();

// Modal state for competition details
const selectedCompetition = ref<PreviewCompetitionModel | null>(null);
const isDetailModalOpen = ref(false);

const handleViewDetails = (competition: PreviewCompetitionModel) => {
  selectedCompetition.value = competition;
  isDetailModalOpen.value = true;
};

const handleCloseDetailModal = () => {
  isDetailModalOpen.value = false;
  // Clear after animation
  setTimeout(() => {
    selectedCompetition.value = null;
  }, 300);
};

// Russian numeral declension: 1 соревнование, 2-4 соревнования, 5-20 соревнований
const getDeclension = (n: number): string => {
  const abs = Math.abs(n) % 100;
  const lastDigit = abs % 10;

  if (abs >= 11 && abs <= 19) {
    return t("competitionsPreview.foundDeclension.many");
  }
  if (lastDigit === 1) {
    return t("competitionsPreview.foundDeclension.one");
  }
  if (lastDigit >= 2 && lastDigit <= 4) {
    return t("competitionsPreview.foundDeclension.few");
  }
  return t("competitionsPreview.foundDeclension.many");
};

// Handle "Place a Competition" button click
const handlePlaceCompetition = () => {
  login();
};

// Handle register button click on card
const handleRegister = (_competitionId: string) => {
  login();
};

// Smooth scroll to content
const scrollToContent = () => {
  document.getElementById("competitions-content")?.scrollIntoView({ behavior: "smooth" });
};

// SEO
useHead({
  title: t("seo.competitionsPreview.title"),
  meta: [
    {
      name: "description",
      content: t("seo.competitionsPreview.description"),
    },
  ],
});
</script>

<template>
  <div class="min-h-screen bg-white dark:bg-gray-950">
    <!-- Hero Banner -->
    <section class="relative overflow-hidden bg-gray-900">
      <!-- Animated pulsating blurs — brighter green/primary tones -->
      <div class="absolute -top-32 -left-32 w-125 h-125 bg-primary-500/40 rounded-full blur-[140px] animate-pulse" />
      <div class="absolute top-1/2 left-1/2 -translate-x-1/2 -translate-y-1/2 w-150 h-100 bg-emerald-500/30 rounded-full blur-[160px] animate-[pulse_4s_ease-in-out_infinite]" />
      <div class="absolute -bottom-32 -right-32 w-112.5 h-112.5 bg-primary-400/35 rounded-full blur-[120px] animate-[pulse_3s_ease-in-out_infinite_0.5s]" />
      <div class="absolute top-0 right-1/4 w-64 h-64 bg-emerald-400/20 rounded-full blur-[100px] animate-[pulse_5s_ease-in-out_infinite_1s]" />

      <div class="relative z-10 max-w-6xl mx-auto px-4 sm:px-6 py-10 sm:py-14">
        <div class="text-center">
          <p class="text-primary-400 text-sm font-semibold tracking-widest uppercase mb-3">
            DreamTeams
          </p>
          <h1 class="text-white text-3xl sm:text-4xl lg:text-5xl font-extrabold tracking-tight leading-tight mb-6">
            <i18n-t keypath="competitionsPreview.found" tag="span">
              <template #found>
                <span
                  class="underline decoration-primary-400 decoration-2 underline-offset-4 cursor-pointer hover:text-primary-300 transition-colors"
                  @click="scrollToContent"
                >{{ t("competitionsPreview.foundLink") }}</span>
              </template>
              <template #total>{{ total }}</template>
              <template #declension>{{ getDeclension(total) }}</template>
            </i18n-t>
          </h1>
          <UButton
            :label="t('competitionsPreview.placeButton')"
            icon="i-heroicons-rocket-launch"
            size="xl"
            variant="solid"
            color="primary"
            class="shadow-lg shadow-primary-500/25"
            @click="handlePlaceCompetition"
          />
        </div>
      </div>
    </section>

    <!-- Content -->
    <section id="competitions-content" class="relative overflow-hidden bg-gray-50 dark:bg-gray-950">
      <!-- Geometric grid background -->
      <div class="absolute inset-0 opacity-[0.04] dark:opacity-[0.06]" style="background-image: url(&quot;data:image/svg+xml,%3Csvg width='40' height='40' viewBox='0 0 40 40' xmlns='http://www.w3.org/2000/svg'%3E%3Cpath d='M0 0h40v40H0z' fill='none' stroke='%2394a3b8' stroke-width='0.5'/%3E%3C/svg%3E&quot;);" />
      <!-- Hex dots accent -->
      <div class="absolute inset-0 opacity-[0.03] dark:opacity-[0.04]" style="background-image: url(&quot;data:image/svg+xml,%3Csvg width='24' height='24' viewBox='0 0 24 24' xmlns='http://www.w3.org/2000/svg'%3E%3Ccircle cx='12' cy='12' r='1.5' fill='%2322c55e'/%3E%3C/svg%3E&quot;);" />
      <!-- Soft radial glow -->
      <div class="absolute top-0 left-1/2 -translate-x-1/2 w-[800px] h-[400px] bg-primary-500/5 dark:bg-primary-500/8 rounded-full blur-[120px]" />

      <div class="relative z-10 max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8 sm:py-12">
        <!-- Error State -->
        <div v-if="error" class="text-center py-16">
          <UIcon name="i-heroicons-exclamation-triangle" class="size-12 text-red-400 mb-4" />
          <p class="text-red-600 dark:text-red-400 text-lg">
            {{ error.message }}
          </p>
        </div>

        <!-- Empty State -->
        <CompetitionPreviewEmptyState
          v-else-if="!loading && competitions.length === 0"
          @place-competition="handlePlaceCompetition"
        />

        <!-- Competitions List -->
        <CompetitionPreviewList
          v-else
          :competitions="competitions"
          :loading="loading"
          :has-more="hasMore"
          @register="handleRegister"
          @load-more="loadMore"
          @view-details="handleViewDetails"
        />
      </div>
    </section>

    <!-- Competition Detail Modal/Drawer -->
    <CompetitionPreviewDetailModal
      :competition="selectedCompetition"
      :open="isDetailModalOpen"
      @close="handleCloseDetailModal"
      @register="handleRegister"
    />
  </div>
</template>
